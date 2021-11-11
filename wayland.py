#!/usr/bin/env python
# pyright: scrict
"""Basic wayland client implementation
"""
import asyncio
import io
import logging
from mmap import mmap
import os
import socket
import secrets
from _posixshmem import shm_open, shm_unlink
from xml.etree import ElementTree
from abc import abstractmethod
from asyncio import Future
from collections import deque
from struct import Struct
from weakref import WeakSet
from typing import (
    Any,
    Callable,
    ClassVar,
    Deque,
    Dict,
    List,
    NamedTuple,
    NewType,
    Optional,
    Set,
    Tuple,
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
        "_on_terminated",
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
    _on_terminated: asyncio.Event

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
        self._on_terminated = asyncio.Event()

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
        self._display._is_attached = True  # display is always attached
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

    async def on_terminated(self) -> None:
        await self._on_terminated.wait()

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

        # cancel futures
        futures = self._futures.copy()
        self._futures.clear()
        for future in futures:
            future.cancel(term_msg)

        # notify termination
        self._on_terminated.set()

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
                    break
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
            args = proxy._interface.unpack(
                self,
                message.opcode,
                message.data,
            )
            proxy._dispatch(opcode, args)

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

    def _on_display_error(self, proxy: "Proxy", code: int, message: str) -> bool:
        """Handle for `wl_display.error` event"""
        # TODO: add error handling
        print(f"\x1b[91mERROR: proxy='{proxy}' code='{code}' message='{message}'\x1b[m")
        self.terminate()
        return True

    def _on_display_delete_id(self, id: Id) -> bool:
        """Unregister proxy"""
        proxy = self._proxies.pop(id, None)
        print("delete:", proxy)
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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return str(self)


class ArgUInt(Arg):
    struct: ClassVar[Struct] = Struct("I")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"[{self.name}] unsigend integer expected")
        write.write(self.struct.pack(value))

    def unpack(self, read: io.BytesIO, _connection: Connection) -> Any:
        return self.struct.unpack(read.read(self.struct.size))[0]


class ArgInt(Arg):
    struct: ClassVar[Struct] = Struct("i")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, int):
            raise ValueError(f"[{self.name}] signed integer expected")
        write.write(self.struct.pack(value))

    def unpack(self, read: io.BytesIO, _connection: Connection) -> Any:
        return self.struct.unpack(read.read(self.struct.size))[0]


class ArgFixed(Arg):
    """Signed 24.8 floating point value"""

    struct: ClassVar[Struct] = Struct("i")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError(f"[{self.name}]  float expected")
        value = (int(value) << 8) + int((value % 1.0) * 256)
        write.write(self.struct.pack(value))

    def unpack(self, read: io.BytesIO, _conneciton: Connection) -> Any:
        value = self.struct.unpack(read.read(self.struct.size))[0]
        return float(value >> 8) + ((value & 0xFF) / 256.0)


class ArgStr(Arg):
    """String argument

    String is zero teminated and 32-bit aligned
    """

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


class ArgArray(Arg):
    """Bytes argument

    Bytes are 32-bit aligned
    """

    struct: ClassVar[Struct] = Struct("I")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        data: bytes
        if isinstance(value, str):
            data = value.encode()
        elif isinstance(value, bytes):
            data = value
        else:
            raise ValueError(f"[{self.name}] string or bytes expected")
        size = len(data)
        write.write(self.struct.pack(size))
        write.write(data)
        write.write(b"\x00" * (-size % 4))

    def unpack(self, read: io.BytesIO, _connection: Connection) -> Any:
        size = self.struct.unpack(read.read(self.struct.size))[0]
        value = read.read(size)
        read.read(-size % 4)
        return value


class ArgNewId(Arg):
    struct: ClassVar[Struct] = Struct("I")
    interface: Optional[str]

    def __init__(self, name: str, interface: Optional[str]):
        super().__init__(name)
        self.interface = interface

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, Proxy):
            raise ValueError(f"[{self.name}] proxy object expected got {value}")
        if value._is_attached:
            raise ValueError(f"[{self.name}] proxy has already been attached")
        value._is_attached = True
        if self.interface is not None and self.interface != value._interface.name:
            raise ValueError(
                f"[{self.name}] proxy object must implement '{self.interface}' "
                f"interface (given '{value._interface.name}'')"
            )
        write.write(self.struct.pack(value._id))

    def unpack(self, _read: io.BytesIO, _connection: Connection) -> Any:
        raise NotImplementedError()

    def __str__(self) -> str:
        return f"ArgNewId({self.name}, {self.interface})"


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

    def __str__(self) -> str:
        return f"ArgObject({self.name}, {self.interface})"


class ArgFd(Arg):
    def pack(self, _write: io.BytesIO, _value: Any) -> None:
        # not actually writing anything, magic happanes on the _writer side
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
        opcode: OpCode,
        args: Tuple[Any, ...],
    ) -> Tuple[bytes, List[int]]:
        """Pack arguments for the specified opcode

        Returns bytes data and descritpros to be send
        """
        name, args_desc = self._requests[opcode]
        if len(args) != len(args_desc):
            raise TypeError(
                f"[{self.name}.{name}] takes {len(args_desc)} arguments ({len(args)} given)"
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
                    raise TypeError(
                        f"[{self.name}.{name}({arg_desc.name})] "
                        f"expected file descriptor '{arg}'"
                    )
                fds.append(fd)
        return write.getvalue(), fds

    def unpack(
        self,
        connection: Connection,
        opcode: OpCode,
        data: bytes,
    ) -> List[Any]:
        """Unpack opcode and data into request name and list of arguments"""
        if opcode >= len(self._events):
            raise RuntimeError(f"[{self.name}] received unknown event {opcode}")
        _name, args_desc = self._events[opcode]
        read = io.BytesIO(data)
        args: List[Any] = []
        for arg_desc in args_desc:
            args.append(arg_desc.unpack(read, connection))
        return args

    def __repr__(self) -> str:
        return f"{self.name}(requests={self._requests}, events={self._events})"


EventHandler = Callable[..., bool]


class Proxy:
    __slots__ = [
        "_id",
        "_interface",
        "_connection",
        "_is_deleted",
        "_is_attached",
        "_handlers",
    ]
    _id: Id
    _interface: Interface
    _connection: Connection
    _is_deleted: bool
    _is_attached: bool
    _handlers: List[Optional[EventHandler]]

    def __init__(self, id: Id, interface: Interface, connection: Connection) -> None:
        self._id = id
        self._interface = interface
        self._connection = connection
        self._is_deleted = False
        self._is_attached = False
        self._handlers = [None] * len(interface._events)

    def __call__(self, name: str, *args: Any) -> None:
        # print(f"{self._interface.name}.{name}{args}")
        if not self._is_attached:
            raise RuntimeError(f"[{self}.{name}({args}) proxy is not attached]")
        desc = self._interface._requests_by_name.get(name)
        if desc is None:
            raise ValueError(f"[{self}] does not have request '{name}'")
        opcode, _args_desc = desc
        data, fds = self._interface.pack(opcode, args)
        self._connection._submit_message(Message(self._id, opcode, data, fds))

    def on(self, name: str, handler: EventHandler) -> Optional[EventHandler]:
        """Register handler for the event"""
        desc = self._interface._events_by_name.get(name)
        if desc is None:
            raise ValueError(f"[{self}] does not have event '{name}'")
        opcode, _args_desc = desc
        old_handler, self._handlers[opcode] = self._handlers[opcode], handler
        return old_handler

    def on_async(self, name: str) -> Future[Tuple[Any, ...]]:
        """Create future which is resolved on event"""

        def handler(*args: Any) -> bool:
            future.set_result(args)
            return False

        self.on(name, handler)
        future: Future[Tuple[Any, ...]] = asyncio.get_running_loop().create_future()
        self._connection._futures.add(future)

        return future

    def _dispatch(self, opcode: OpCode, args: List[Any]) -> None:
        """Dispatch event to the handler"""
        handler = self._handlers[opcode]
        if handler is None:
            return
        try:
            if not handler(*args):
                self._handlers[opcode] = None
        except Exception:
            name = self._interface._events[opcode][0]
            logging.exception(f"[{self}.{name}] handler raised and error")
            self._handlers[opcode] = None

    """
    def __getattr__(self, name: str) -> Callable[..., Any]:
        return lambda *args: self(name, *args)
    """

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self._interface.name}@{self._id}"


def load_protocol(path: str) -> Dict[str, Interface]:
    """Load interfaces from protocol XML file"""
    tree = ElementTree.parse(path)

    ifaces: Dict[str, Interface] = {}
    for node in tree.getroot():
        if node.tag != "interface":
            continue
        iface_name = node.get("name")
        if iface_name is None:
            raise ValueError("interface must have name attribute")
        events = []
        requests = []

        for child in node:
            if child.tag in {"request", "event"}:
                name = child.get("name")
                if name is None:
                    raise ValueError(f"[{iface_name}] {child.tag} without a name")
                args: List[Arg] = []
                for arg_node in child:
                    if arg_node.tag != "arg":
                        continue
                    arg_name = arg_node.get("name")
                    if arg_name is None:
                        raise ValueError(
                            f"[{iface_name}.{name}] argument without a name"
                        )
                    arg_type = arg_node.get("type")
                    if arg_type is None:
                        raise ValueError(
                            f"[{iface_name}.{name}] argument without a type"
                        )
                    if arg_type == "uint":
                        # TODO: enum support
                        args.append(ArgUInt(arg_name))
                    elif arg_type == "int":
                        args.append(ArgInt(arg_name))
                    elif arg_type == "fixed":
                        args.append(ArgFixed(arg_name))
                    elif arg_type == "string":
                        args.append(ArgStr(arg_name))
                    elif arg_type == "array":
                        args.append(ArgArray(arg_name))
                    elif arg_type == "fd":
                        args.append(ArgFd(arg_name))
                    elif arg_type == "object":
                        args.append(ArgObject(arg_name, arg_node.get("interface")))
                    elif arg_type == "new_id":
                        arg_iface = arg_node.get("interface")
                        if arg_iface is not None:
                            args.append(ArgNewId(arg_name, arg_iface))
                        else:
                            # new_id without interface is unpacked into 3 arguments
                            # (interface_name: str, version: uint, id: new_id)
                            args.append(ArgStr("interface"))
                            args.append(ArgUInt("version"))
                            args.append(ArgNewId("interface", None))

                if child.tag == "request":
                    requests.append((name, args))
                else:
                    events.append((name, args))

            elif child.tag == "enum":
                pass

        iface = Interface(iface_name, requests, events)
        ifaces[iface_name] = iface
    return ifaces


class SharedMemory:
    """Create shared memory file

    This can be send over to wayland compositor, or converted to numpy array:
        shm = SharedMemory(8192)
        array = numpy.ndarray(shape=(32,32), dtype=float, shm)
    """

    __slots__ = ["_fd", "_mmap", "_is_closed"]
    _fd: int
    _mmap: mmap
    _is_closed: bool

    def __init__(self, size: int, fd: Optional[int] = None) -> None:
        self._is_closed = False
        if fd is None:
            name = secrets.token_hex(16)
            flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
            self._fd = shm_open(name, flags, 0o600)
            try:
                os.ftruncate(self._fd, size)
                self._mmap = mmap(self._fd, size)
            finally:
                shm_unlink(name)
        else:
            self._fd = fd
            self._mmap = mmap(self._fd, size)

    def fileno(self) -> int:
        if self._is_closed:
            raise RuntimeError("shared memory file is closed")
        return self._fd

    @property
    def buf(self) -> mmap:
        return self._mmap

    def close(self):
        is_closed, self._is_closed = self._is_closed, True
        if is_closed:
            return
        os.close(self._fd)
        self._mmap.close()

    def __del__(self):
        return self.close()


WAYLAND_PROTO = load_protocol("wayland.xml")
WL_DISPLAY = WAYLAND_PROTO["wl_display"]
WL_REGISTRY = WAYLAND_PROTO["wl_registry"]
WL_CALLBACK = WAYLAND_PROTO["wl_callback"]
WL_SHM = WAYLAND_PROTO["wl_shm"]
WL_SHM_POOL = WAYLAND_PROTO["wl_shm_pool"]
WL_BUFFER = WAYLAND_PROTO["wl_buffer"]
WL_SURFACE = WAYLAND_PROTO["wl_surface"]
WL_COMPOSITOR = WAYLAND_PROTO["wl_compositor"]

XDG_SHELL_PROTO = load_protocol("xdg-shell.xml")
XDG_WM_BASE = XDG_SHELL_PROTO["xdg_wm_base"]
XDG_SURFACE = XDG_SHELL_PROTO["xdg_surface"]
XDG_TOPLEVEL = XDG_SHELL_PROTO["xdg_toplevel"]


async def main() -> None:
    # globals
    conn = await Connection().connect()
    wl_shm = conn.get_global(WL_SHM)
    wl_compositor = conn.get_global(WL_COMPOSITOR)
    xdg_wm_base = conn.get_global(XDG_WM_BASE)

    # surface
    wl_surf = conn.create_proxy(WL_SURFACE)
    wl_compositor("create_surface", wl_surf)
    xdg_surf = conn.create_proxy(XDG_SURFACE)
    xdg_wm_base("get_xdg_surface", xdg_surf, wl_surf)
    xdg_toplevel = conn.create_proxy(XDG_TOPLEVEL)
    xdg_surf("get_toplevel", xdg_toplevel)
    xdg_toplevel("set_title", "wayland-py")
    wl_surf("commit")

    # memory buffer
    width = 640
    height = 480
    stride = width * 4
    size = stride * height
    buf_mem = SharedMemory(size)

    # draw
    for y in range(height):
        for x in range(width):
            offset = y * stride + x * 4
            if (x + int(y / 8) * 8) % 16 < 8:
                buf_mem.buf[offset : offset + 4] = b"\x66\x66\x66\xff"
            else:
                buf_mem.buf[offset : offset + 4] = b"\xee\xee\xee\xff"

    # create wl_buffer
    pool = conn.create_proxy(WL_SHM_POOL)
    wl_shm("create_pool", pool, buf_mem, size)
    buf = conn.create_proxy(WL_BUFFER)
    pool("create_buffer", buf, 0, width, height, stride, 1)
    pool("destroy")

    def on_configure(serial: int) -> bool:
        print("draw")
        xdg_surf("ack_configure", serial)
        wl_surf("attach", buf, 0, 0)
        wl_surf("commit")
        return True

    xdg_surf.on("configure", on_configure)

    await conn.on_terminated()


def print_message(msg: str) -> Callable[..., bool]:
    def print_message_handler(*args: Any) -> bool:
        print(msg, args)
        return True

    return print_message_handler


if __name__ == "__main__":
    asyncio.run(main())
