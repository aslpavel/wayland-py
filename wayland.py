#!/usr/bin/env python
# pyright: scrict
"""Basic wayland client implementation
"""
import pdb
import asyncio
import io
import logging
import socket
from abc import abstractmethod
from asyncio import CancelledError, Future, StreamReader, StreamWriter, Task
from collections import deque
from struct import Struct
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
        "_id_last",
        "_id_free",
        "_proxies",
        "_write_queue",
        "_write_notify",
        "_fds_queue",
        "_run_task",
        "_is_terminated",
        "_display",
        "_registry",
        "_registry_globals",
    ]

    _path: str
    _id_last: Id
    _id_free: List[Id]
    _proxies: Dict[Id, "Proxy"]
    _write_queue: Deque[Message]
    _write_notify: "Event[None]"
    _fds_queue: Deque[int]
    _run_task: Optional[Future[Any]]
    _is_terminated: bool
    _display: "Proxy"
    _registry: "Proxy"
    _registry_globals: Dict[str, Tuple[int, Optional["Proxy"]]]

    def __init__(self, path: Optional[str] = None):
        self._path = path or "/run/user/1000/wayland-1"
        self._id_last = Id(0)
        self._id_free = []
        self._proxies = {}
        self._write_queue = deque()
        self._write_notify = Event()
        self._fds_queue = deque()
        self._is_terminated = False
        self._run_task = None

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
        name, proxy = entry
        if proxy is None:
            proxy = self.create_proxy(interface)
            self._registry("bind", name, proxy)
            self._registry_globals[interface.name] = (name, proxy)
        return proxy

    def sync(self) -> "Sync":
        """Create synchronization scope

        This async contextmanager can be used as a berrier to ensure
        all previous requests and resulting events have been handled.
        """
        return Sync(self)

    @property
    def is_terminated(self):
        self._is_terminated

    def terminate(self, msg: Optional[Any] = None) -> None:
        """Teminate wayland connection"""
        term_msg = "wayland connection has been terminated"
        if msg is not None:
            term_msg = msg
        if self._is_terminated:
            return
        self._is_terminated = True
        if self._run_task is not None:
            self._run_task.cancel(term_msg)
        proxies = self._proxies.copy()
        proxies.clear()
        for proxy in proxies.values():
            proxy._events.cancel(term_msg)

    def run(self) -> Task[None]:
        """Start running wayland connection"""
        if self._is_terminated:
            raise RuntimeError("connection has already been terminated")
        if self._run_task is not None:
            raise RuntimeError("connection is already running")
        return asyncio.create_task(self._run(), name="wayland io task")

    async def _run(self) -> None:
        """Start running wayland connection"""
        writer: Optional[StreamWriter] = None
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
            sock.connect(self._path)
            sock.setblocking(False)
            self._run_task = asyncio.gather(
                self._reader(sock),
                self._writer(sock),
            )
            await self.sync()
            await self._run_task
        except (CancelledError, ConnectionResetError):
            pass
        except Exception:
            logging.exception("wayland io task failed")
            raise
        finally:
            if writer is not None:
                writer.close()
            self.terminate()

    async def _writer(self, sock: socket.socket) -> None:
        """Write queued messages to the socket"""
        fds = []
        buff = bytearray()
        while not self._is_terminated:
            # wait for messages to be send
            if not self._write_queue:
                await self._write_notify

            # pack messages
            buff.clear()
            while self._write_queue:
                message = self._write_queue.popleft()
                buff.extend(
                    MSG_HEADER.pack(
                        message.id,
                        message.opcode,
                        MSG_HEADER.size + len(message.data),
                    )
                )
                buff.extend(message.data)
                fds.extend(message.fds)

            # send messages
            offset = 0
            while offset < len(buff):
                try:
                    offset += socket.send_fds(sock, [buff[offset:]], fds)
                    fds.clear()
                except BlockingIOError:
                    await _wait_writeable(sock.fileno())
                    continue
        raise CancelledError()

    async def _reader(self, sock: socket.socket) -> None:
        """Read and dispatch messages from the socket"""
        size: int = MSG_HEADER.size  # required size
        buff = bytearray()

        while not self._is_terminated:
            # receive data until required size is received
            while len(buff) < size:
                try:
                    data, fds_new, _flags, _address = socket.recv_fds(sock, 4096, 32)
                    if not data:
                        raise CancelledError()
                    self._fds_queue.extend(fds_new)
                    buff.extend(data)
                except BlockingIOError:
                    await _wait_readable(sock.fileno())
                    continue

            # unpack message
            id, opcode, size = MSG_HEADER.unpack(buff[: MSG_HEADER.size])
            if len(buff) < size:
                continue
            message = Message(Id(id), OpCode(opcode), buff[MSG_HEADER.size : size], [])

            # consume data and reset size
            buff = buff[size:]
            size = MSG_HEADER.size

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
        raise CancelledError()

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

    def _on_registry_global(self, name: int, interface: str, _version: int) -> bool:
        """Register name in registry globals"""
        self._registry_globals[interface] = (name, None)
        return True

    def _on_registry_global_remove(self, target_name: int):
        """Unregister name from registry globals"""
        for interface, (name, proxy) in self._registry_globals.items():
            if target_name == name:
                self._registry_globals.pop(interface)
                if proxy is not None:
                    self._proxies.pop(proxy._id)
                break
        return True

    def _recv_fd(self) -> Optional[int]:
        """Pop next descriptor from file descriptor queue"""
        if self._fds_queue:
            return self._fds_queue.popleft()

    def _submit_message(self, message: Message):
        """Submit message for writing"""
        if message.id not in self._proxies:
            raise RuntimeError("object has already been deleted")
        self._write_queue.append(message)
        self._write_notify(None)


async def _wait_readable(fd: int) -> None:
    """Wait for file descriptor to become readable"""
    loop = asyncio.get_running_loop()
    readable = loop.create_future()
    try:
        loop.add_reader(fd, readable.set_result, None)
        await readable
    finally:
        loop.remove_reader(fd)


async def _wait_writeable(fd: int) -> None:
    """Wait for file descriptor to become writable"""
    loop = asyncio.get_running_loop()
    writable = loop.create_future()
    try:
        loop.add_writer(fd, writable.set_result, None)
        await writable
    finally:
        loop.remove_writer(fd)


class Sync:
    __slots__ = ["connection", "done"]
    connection: Connection
    done: Future[List[Any]]

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        callback = connection.create_proxy(WL_CALLBACK)
        self.done = callback.on_async("done")
        connection.display("sync", callback)

    def __await__(self) -> Generator[Any, None, List[Any]]:
        return self.done.__await__()

    async def __aenter__(self) -> "Sync":
        return self

    async def __aexit__(self, _et: Any, ev: Any, _tb: Any):
        if ev is None and not self.connection.is_terminated:
            await self.done


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

        def on_named(event: Tuple[str, List[Any]]):
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
        ("bind", [ArgUInt("name"), ArgNewId("id", None)]),
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


async def main():
    conn = Connection()
    done = conn.run()
    await conn.sync()

    print("interfaces:")
    for interface in conn._registry_globals:
        print("   ", interface)

    wl_shm = conn.get_global(WL_SHM)
    wl_shm.on("format", print_message)

    await asyncio.sleep(0.1)
    await conn.sync()
    conn.terminate()


def print_message(*args: Any):
    print(args)
    return True


if __name__ == "__main__":
    asyncio.run(main())
