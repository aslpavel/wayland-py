#!/usr/bin/env python
# pyright: scrict
"""Basic wayland client implementation
"""
import asyncio
import io
import logging
import os
import socket
from abc import abstractmethod
from asyncio import CancelledError, Future, Task
from collections import deque
from struct import Struct
from weakref import WeakSet
from typing import (
    Any,
    Callable,
    ClassVar,
    Deque,
    Dict,
    Generator,
    Generic,
    List,
    NamedTuple,
    NewType,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

Id = NewType("Id", int)
OpCode = NewType("OpCode", int)
MSG_HEADER = Struct("IHH")


class Message(NamedTuple):
    """Wayland message"""

    id: Id
    opcode: OpCode
    data: bytes
    fds: List[int]


class Connection:
    __slots__ = [
        "_path",
        "_socket",
        "_loop",
        "_is_terminated",
        "_write_buff",
        "_write_fds",
        "_write_queue",
        "_read_buff",
        "_read_fds",
        "_id_last",
        "_id_free",
        "_proxies",
        "_futures",
        "_display",
        "_registry",
        "_registry_globals",
    ]

    _path: str
    _socket: Optional[socket.socket]
    _loop: asyncio.AbstractEventLoop
    _is_terminated: bool

    _write_fds: List[int]
    _write_buff: bytearray
    _write_queue: Deque[Message]

    _read_buff: bytearray
    _read_fds: Deque[int]

    _id_last: Id
    _id_free: List[Id]
    _proxies: Dict[Id, "Proxy"]
    _futures: WeakSet[Future[Any]]

    _display: "Proxy"
    _registry: "Proxy"
    _registry_globals: Dict[
        str, Tuple[int, int, Optional["Proxy"]]
    ]  # (name, verison, proxy)

    def __init__(self, path: Optional[str] = None) -> None:
        if path is not None:
            self._path = path
        else:
            runtime_dir = os.getenv("XDG_RUNTIME_DIR")
            if runtime_dir is None:
                raise RuntimeError("XDG_RUNTIME_DIR is not set")
            display = os.getenv("WAYLAND_DISPLAY", "wayland-0")
            self._path = os.path.join(runtime_dir, display)
        self._socket = None
        self._loop = asyncio.get_running_loop()
        self._is_terminated = False

        self._write_fds = []
        self._write_buff = bytearray()
        self._write_queue = deque()

        self._read_fds = deque()
        self._read_buff = bytearray()

        self._id_last = Id(0)
        self._id_free = []
        self._proxies = {}
        self._futures = WeakSet()

        self._display = self.create_proxy(WL_DISPLAY)
        self._display.on("error", self._on_display_error)
        self._display.on("delete_id", self._on_display_delete_id)

        self._registry = self.create_proxy(WL_REGISTRY)
        self._registry.on("global", self._on_registry_global)
        self._registry.on("global_remove", self._on_registry_global_remove)
        self._registry_globals = {}
        self._display("get_registry", self._registry)

    @property
    def display(self) -> "Proxy":
        return self._display

    def create_proxy(self, interface: "Interface") -> "Proxy":
        """Create new proxy object"""
        if self._is_terminated:
            raise RuntimeError("connection has already been terminated")
        # allocate id
        id: Id
        if self._id_free:
            id = self._id_free.pop()
        else:
            self._id_last = Id(self._id_last + 1)
            id = self._id_last
        # register proxy
        proxy = Proxy(id, interface, self)
        self._proxies[id] = proxy
        return proxy

    def get_global(self, interface: "Interface") -> "Proxy":
        """Get global exposing interface"""
        entry = self._registry_globals.get(interface.name)
        if entry is None:
            raise RuntimeError(f"no globals provide: {interface}")
        name, version, proxy = entry
        if proxy is None:
            proxy = self.create_proxy(interface)
            self._registry("bind", name, interface.name, version, proxy)
            self._registry_globals[interface.name] = (name, version, proxy)
        return proxy

    async def sync(self) -> None:
        """Ensures all requests are processed

        This funciton can be used as a berrier to ensure all previous
        requests and resulting events have been handled.
        """
        callback = self.create_proxy(WL_CALLBACK)
        done = callback.on_async("done")
        self.display("sync", callback)
        await done

    @property
    def is_terminated(self) -> bool:
        return self._is_terminated

    def terminate(self, msg: Optional[Any] = None) -> None:
        """Teminate wayland connection"""
        is_terminated, self._is_terminated = self._is_terminated, True
        if is_terminated:
            return

        term_msg = "wayland connection has been terminated"
        if msg is not None:
            term_msg = msg

        # disconnect
        self._writer_disable()
        self._reader_disable()
        if self._socket is not None:
            self._socket.close()

        # cacnel proxies
        proxies = self._proxies.copy()
        self._proxies.clear()
        for proxy in proxies.values():
            proxy._events.cancel(term_msg)

        # cancel futures
        futures = self._futures.copy()
        self._futures.clear()
        for future in futures:
            future.cancel(term_msg)

    async def connect(self) -> "Connection":
        """Start running wayland connection"""
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        self._socket.connect(self._path)
        self._socket.setblocking(False)
        self._writer_enable()
        self._reader_enable()
        await self.sync()
        return self

    def _writer_enable(self) -> None:
        if self._is_terminated:
            raise RuntimeError("connection has beend terminated")
        if self._socket is not None:
            self._loop.add_writer(self._socket, self._writer)

    def _writer_disable(self) -> None:
        if self._socket is not None:
            self._loop.remove_writer(self._socket)

    def _writer(self) -> None:
        """Write pending messages"""
        if self._is_terminated or self._socket is None:
            self._writer_disable()
            return

        # pack queued messages
        while self._write_queue:
            message = self._write_queue.popleft()
            self._write_buff.extend(
                MSG_HEADER.pack(
                    message.id,
                    message.opcode,
                    MSG_HEADER.size + len(message.data),
                )
            )
            self._write_buff.extend(message.data)
            self._write_fds.extend(message.fds)

        # send messages
        try:
            offset = 0
            while offset < len(self._write_buff):
                try:
                    offset += socket.send_fds(
                        self._socket, [self._write_buff[offset:]], self._write_fds
                    )
                    self._write_fds.clear()
                except BlockingIOError:
                    break
        except Exception:
            error_msg = "failed to write to wayland socket"
            logging.exception(error_msg)
            self.terminate(error_msg)
        finally:
            self._write_buff = self._write_buff[offset:]
            if not self._write_buff and not self._write_queue:
                self._writer_disable()

    def _reader_enable(self) -> None:
        if self._is_terminated:
            raise RuntimeError("connection has beend terminated")
        if self._socket is not None:
            self._loop.add_reader(self._socket, self._reader)

    def _reader_disable(self) -> None:
        if self._socket is not None:
            self._loop.remove_reader(self._socket)

    def _reader(self) -> None:
        """Read incomming messages"""
        if self._is_terminated or self._socket is None:
            self._reader_disable()
            return

        # reading data
        while True:
            try:
                data, fds, _flags, _address = socket.recv_fds(self._socket, 4096, 32)
                if not data:
                    self.terminate("connection closed")
                self._read_fds.extend(fds)
                self._read_buff.extend(data)
            except BlockingIOError:
                break
            except Exception:
                error_msg = "failed to read from wayland socket"
                logging.exception(error_msg)
                self.terminate(error_msg)
                return

        while len(self._read_buff) >= MSG_HEADER.size:
            # unpack message
            id, opcode, size = MSG_HEADER.unpack(self._read_buff[: MSG_HEADER.size])
            if len(self._read_buff) < size:
                return
            message = Message(
                Id(id),
                OpCode(opcode),
                self._read_buff[MSG_HEADER.size : size],
                [],
            )
            # consume data and reset size
            self._read_buff = self._read_buff[size:]

            # dispatch event
            proxy = self._proxies.get(message.id)
            if proxy is None:
                logging.error("unhandled message: %s", message)
                continue
            name, args = proxy._interface.unpack(
                self,
                message.opcode,
                message.data,
            )
            proxy._events((name, args))

    def _on_display_error(self, proxy: "Proxy", code: int, message: str) -> bool:
        """Handler for `wl_display.error` event"""
        # TODO: add error handling
        print(f"\x1b[91mERROR: proxy='{proxy}' code='{code}' message='{message}'\x1b[m")
        return True

    def _on_display_delete_id(self, id: Id) -> bool:
        """Handler for `wl_display.delete_id` evet"""
        self._proxies.pop(id, None)
        self._id_free.append(id)
        return True

    def _on_registry_global(self, name: int, interface: str, version: int) -> bool:
        """Register name in registry globals"""
        self._registry_globals[interface] = (name, version, None)
        return True

    def _on_registry_global_remove(self, target_name: int) -> bool:
        """Unregister name from registry globals"""
        for interface, (name, _version, proxy) in self._registry_globals.items():
            if target_name == name:
                self._registry_globals.pop(interface)
                if proxy is not None:
                    self._proxies.pop(proxy._id)
                break
        return True

    def _recv_fd(self) -> Optional[int]:
        """Pop next descriptor from file descriptor queue"""
        if self._read_fds:
            return self._read_fds.popleft()
        return None

    def _submit_message(self, message: Message) -> None:
        """Submit message for writing"""
        if message.id not in self._proxies:
            raise RuntimeError("object has already been deleted")
        self._write_queue.append(message)
        self._writer_enable()


class Arg:
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def pack(self, write: io.BytesIO, value: Any) -> None:
        pass

    @abstractmethod
    def unpack(self, read: io.BytesIO, connection: Connection) -> Any:
        pass


class ArgNewId(Arg):
    struct: ClassVar[Struct] = Struct("I")
    interface: Optional[str]

    def __init__(self, name: str, interface: Optional[str]):
        super().__init__(name)
        self.interface = interface

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, Proxy):
            raise ValueError(f"[{self.name}] proxy object expected {value}")
        if self.interface is not None and self.interface != value._interface.name:
            raise ValueError(
                f"[{self.name}] proxy object must implement '{self.interface}' "
                f"interface (given '{value._interface.name}'')"
            )
        write.write(self.struct.pack(value._id))

    def unpack(self, _read: io.BytesIO, _connection: Connection) -> Any:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"ArgNewId({self.name}, {self.interface})"


class ArgUInt(Arg):
    struct: ClassVar[Struct] = Struct("I")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"[{self.name}] unsigend integer expected")
        write.write(self.struct.pack(value))

    def unpack(self, read: io.BytesIO, _connection: Connection) -> Any:
        return self.struct.unpack(read.read(self.struct.size))[0]


class ArgObject(Arg):
    struct: ClassVar[Struct] = Struct("I")
    interface: Optional[str]

    def __init__(self, name: str, interface: Optional[str]):
        super().__init__(name)
        self.interface = interface

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, Proxy):
            raise ValueError(f"[{self.name}] proxy object expected {value}")
        if self.interface is not None and self.interface != value._interface.name:
            raise ValueError(
                f"[{self.name}] proxy object must implement '{self.interface}' "
                f"interface (given '{value._interface.name}'')"
            )
        write.write(self.struct.pack(value._id))

    def unpack(self, read: io.BytesIO, connection: Connection) -> Any:
        id = self.struct.unpack(read.read(self.struct.size))[0]
        proxy = connection._proxies.get(id)
        if proxy is None:
            raise RuntimeError("[{self.name}] unknown incomming object")
        return proxy


class ArgStr(Arg):
    struct: ClassVar[Struct] = Struct("I")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        data: bytes
        if isinstance(value, str):
            data = value.encode()
        elif isinstance(value, bytes):
            data = value
        else:
            raise ValueError(f"[{self.name}] string or bytes expected")
        size = len(data) + 1  # null terminated length
        write.write(self.struct.pack(size))
        write.write(data)
        # null terminated and padded to 32-bit
        padding = (-size % 4) + 1
        write.write(b"\x00" * padding)

    def unpack(self, read: io.BytesIO, _connection: Connection) -> Any:
        size = self.struct.unpack(read.read(self.struct.size))[0]
        value = read.read(size - 1).decode()
        read.read((-size % 4) + 1)
        return value


class ArgFd(Arg):
    def pack(self, _write: io.BytesIO, _value: Any) -> None:
        # noop for file descriptor
        pass

    def unpack(self, _read: io.BytesIO, connection: Connection) -> Any:
        fd = connection._recv_fd()
        if fd is None:
            raise RuntimeError(f"[{self.name}] expected file descriptor")
        return fd


class Interface:
    __slots__ = ["name", "_events", "_requests", "_requests_by_name", "_events_by_name"]
    name: str
    _events: List[Tuple[str, List[Arg]]]
    _events_by_name: Dict[str, Tuple[OpCode, List[Arg]]]
    _requests: List[Tuple[str, List[Arg]]]
    _requests_by_name: Dict[str, Tuple[OpCode, List[Arg]]]

    def __init__(
        self,
        name: str,
        requests: List[Tuple[str, List[Arg]]],
        events: List[Tuple[str, List[Arg]]],
    ) -> None:
        self.name = name
        self._requests = requests
        self._events = events
        self._requests_by_name = {}
        for opcode, (name, args) in enumerate(requests):
            self._requests_by_name[name] = (OpCode(opcode), args)
        self._events_by_name = {}
        for opcode, (name, args) in enumerate(events):
            self._events_by_name[name] = (OpCode(opcode), args)

    def pack(
        self,
        request: str,
        args: Tuple[Any, ...],
    ) -> Tuple[OpCode, bytes, List[int]]:
        """Convert request and its arguments into OpCode, data and fds"""
        desc = self._requests_by_name.get(request)
        if desc is None:
            raise AttributeError(f"unknow request name: {self.name}.{request}")
        opcode, args_desc = desc
        if len(args) != len(args_desc):
            raise TypeError(
                f"{self.name}.{request} takes {len(args_desc)} arguments ({len(args)} given)"
            )
        write = io.BytesIO()
        fds: List[int] = []
        for arg, arg_desc in zip(args, args_desc):
            arg_desc.pack(write, arg)
            if isinstance(arg_desc, ArgFd):
                fd: int
                if hasattr(arg, "fileno"):
                    fd = arg.fileno()
                elif isinstance(arg, int):
                    fd = arg
                else:
                    raise TypeError(f"[{arg_desc.name}] expected file descriptor")
                fds.append(fd)
        return opcode, write.getvalue(), fds

    def unpack(
        self,
        connection: Connection,
        opcode: OpCode,
        data: bytes,
    ) -> Tuple[str, List[Any]]:
        """Unpack opcode and data into request name and list of arguments"""
        if opcode >= len(self._events):
            raise RuntimeError(f"[{self.name}] received unknown event {opcode}")
        name, args_desc = self._events[opcode]
        read = io.BytesIO(data)
        args: List[Any] = []
        for arg_desc in args_desc:
            args.append(arg_desc.unpack(read, connection))
        return name, args

    def __repr__(self) -> str:
        return self.name


class Proxy:
    __slots__ = ["_id", "_interface", "_connection", "_is_deleted", "_events"]
    _id: Id
    _interface: Interface
    _connection: Connection
    _events: "Event[Tuple[str, List[Any]]]"

    def __init__(self, id: Id, interface: Interface, connection: Connection) -> None:
        self._id = id
        self._interface = interface
        self._connection = connection
        self._is_deleted = False
        self._events = Event()

    def __call__(self, request: str, *args: Any) -> None:
        opcode, data, fds = self._interface.pack(request, args)
        self._connection._submit_message(Message(self._id, opcode, data, fds))

    def on(self, name: str, callback: Callable[..., bool]) -> None:
        if name not in self._interface._events_by_name:
            raise ValueError(f"[{self._interface.name}] does not have event '{name}'")

        def on_named(event: Tuple[str, List[Any]]) -> bool:
            event_name, event_args = event
            if event_name != name:
                return True
            return callback(*event_args)

        self._events.on(on_named)

    def on_async(self, name: str) -> Future[List[Any]]:
        if name not in self._interface._events_by_name:
            raise ValueError(f"[{self._interface.name}] does not have event '{name}'")

        def on_resolve(event: Tuple[str, List[Any]]) -> bool:
            event_name, event_args = event
            if event_name != name:
                return True
            future.set_result(event_args)
            return False

        future: Future[List[Any]] = asyncio.get_running_loop().create_future()
        self._connection._futures.add(future)
        self._events.on(on_resolve)
        return future

    """
    def __getattr__(self, name: str) -> Callable[..., Any]:
        return lambda *args: self(name, *args)
    """

    def __repr__(self) -> str:
        return f"{self._interface.name}@{self._id}"


WL_DISPLAY = Interface(
    name="wl_display",
    requests=[
        ("sync", [ArgNewId("callback", "wl_callback")]),
        ("get_registry", [ArgNewId("registry", "wl_registry")]),
    ],
    events=[
        ("error", [ArgObject("object_id", None), ArgUInt("code"), ArgStr("message")]),
        ("delete_id", [ArgUInt("id")]),
    ],
)
WL_REGISTRY = Interface(
    name="wl_registry",
    requests=[
        # whenever new_id does not specify interface it implies, that three arguments
        # must be used instead (name: str, version: uint, id: new_id)
        (
            "bind",
            [
                ArgUInt("name"),
                ArgStr("interface"),
                ArgUInt("version"),
                ArgNewId("id", None),
            ],
        ),
    ],
    events=[
        ("global", [ArgUInt("name"), ArgStr("interface"), ArgUInt("version")]),
        ("global_remove", [ArgUInt("name")]),
    ],
)
WL_CALLBACK = Interface(
    name="wl_callback",
    requests=[],
    events=[("done", [ArgUInt("callback_data")])],
)
WL_SHM = Interface(
    name="wl_shm",
    requests=[
        ("create_pool", [ArgNewId("id", "wl_shm_pool"), ArgFd("fd"), ArgUInt("size")])
    ],
    events=[("format", [ArgUInt("format")])],
)
INTERFACES: Dict[str, Interface] = {
    interface.name: interface
    for interface in [WL_DISPLAY, WL_REGISTRY, WL_CALLBACK, WL_SHM]
}


E = TypeVar("E")


class Event(Generic[E]):
    __slots__ = ["_handlers", "_futures"]

    def __init__(self) -> None:
        self._handlers: Set[Callable[[E], bool]] = set()
        self._futures: Set[Future[E]] = set()

    def __call__(self, event: E) -> None:
        """Raise new event"""
        handlers = self._handlers.copy()
        self._handlers.clear()
        for handler in handlers:
            try:
                if handler(event):
                    self._handlers.add(handler)
            except Exception:
                logging.exception("unhandled exception in handler %s", handler)
        futures = self._futures.copy()
        self._futures.clear()
        for future in futures:
            future.set_result(event)

    def cancel(self, msg: Optional[Any] = None) -> None:
        """Cancel all waiting futures"""
        futures = self._futures.copy()
        self._futures.clear()
        for future in futures:
            future.cancel(msg)

    def on(self, handler: Callable[[E], bool]) -> None:
        """Register event handler

        Handler is kept subscribed as long as it returns True
        """
        self._handlers.add(handler)

    def __await__(self) -> Generator[Any, None, E]:
        """Await for next event"""
        future: Future[E] = asyncio.get_running_loop().create_future()
        self._futures.add(future)
        return future.__await__()

    def __repr__(self) -> str:
        return f"Events(handlers={len(self._handlers)}, futures={len(self._futures)})"


async def main() -> None:
    conn = await Connection().connect()

    print("interfaces:")
    for interface in conn._registry_globals:
        print("   ", interface)

    wl_shm = conn.get_global(WL_SHM)
    wl_shm.on("format", print_message("wl_shm format:"))

    await conn.sync()
    conn.terminate()


def print_message(msg: str) -> Callable[..., bool]:
    def print_message_handler(*args: Any) -> bool:
        print(msg, args)
        return True

    return print_message_handler


if __name__ == "__main__":
    asyncio.run(main())
