"""Base wayland abstractions
"""
# private variables used between classes in file
# pyright: reportPrivateUsage=false
from __future__ import annotations
import asyncio
import io
import logging
from mmap import mmap
import sys
import os
import socket
import secrets
from enum import Enum
from _posixshmem import shm_open, shm_unlink
from xml.etree import ElementTree
from abc import ABC, abstractmethod
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
    Protocol as Proto,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    runtime_checkable,
)

__all__ = [
    "Id",
    "OpCode",
    "Connection",
    "Arg",
    "ArgUInt",
    "ArgInt",
    "ArgFixed",
    "ArgStr",
    "ArgArray",
    "ArgNewId",
    "ArgObject",
    "ArgFd",
    "Interface",
    "WRequest",
    "WEvent",
    "WEnum",
    "Proxy",
    "Protocol",
    "Fd",
    "SharedMemory",
    "PROXIES",
]

Id = NewType("Id", int)
OpCode = NewType("OpCode", int)
MSG_HEADER = Struct("IHH")
PROXIES: Dict[str, Type[Proxy]] = {}

P = TypeVar("P", bound="Proxy")
C = TypeVar("C", bound="Connection")


class Message(NamedTuple):
    """Wayland message"""

    id: Id
    opcode: OpCode
    data: bytes
    fds: List[Fd]


class Connection(ABC):
    __slots__ = [
        "_socket",
        "_loop",
        "_is_terminated",
        "_is_server",
        "_on_terminated",
        "_write_buff",
        "_write_fds",
        "_write_queue",
        "_write_done",
        "_read_buff",
        "_read_fds",
        "_id_last",
        "_id_free",
        "_proxies",
        "_futures",
        "_debug",
    ]

    _socket: Optional[socket.socket]
    _loop: asyncio.AbstractEventLoop
    _is_terminated: bool
    _is_server: bool
    _on_terminated: asyncio.Event
    _debug: bool

    _write_fds: List[Fd]
    _write_buff: bytearray
    _write_queue: Deque[Message]
    _write_done: asyncio.Event

    _read_buff: bytearray
    _read_fds: Deque[Fd]

    _id_last: Id
    _id_free: List[Id]
    _proxies: Dict[Id, "Proxy"]

    def __init__(self, debug: Optional[bool] = None, is_server: bool = False) -> None:
        self._socket = None
        self._loop = asyncio.get_running_loop()
        self._is_terminated = False
        self._is_server = is_server
        self._on_terminated = asyncio.Event()
        self._debug = bool(os.getenv("WAYLAND_DEBUG")) if debug is None else debug

        self._write_fds = []
        self._write_buff = bytearray()
        self._write_queue = deque()
        self._write_done = asyncio.Event()
        self._write_done.set()

        self._read_fds = deque()
        self._read_buff = bytearray()

        self._id_last = Id(0)
        self._id_free = []
        self._proxies = {}

    def create_proxy(self, proxy_type: Type[P]) -> P:
        """Create proxy by proxy type"""
        if self._is_terminated:
            raise RuntimeError("connection has already been terminated")
        id = self._id_alloc()
        proxy = proxy_type(id, self)
        self._proxies[id] = proxy
        return proxy

    def create_proxy_by_interface(self, interface: Interface) -> Proxy:
        """Create new proxy object"""
        if self._is_terminated:
            raise RuntimeError("connection has already been terminated")
        id = self._id_alloc()
        proxy = Proxy(id, self, interface)
        self._proxies[id] = proxy
        return proxy

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

        # disconnect
        self._writer_disable()
        self._reader_disable()
        if self._socket is not None:
            self._socket.close()

        # detach all proxies
        for proxy in self._proxies.values():
            proxy._detach(msg if msg else "wayland connection terminated")
        self._proxies.clear()

        # notify termination
        self._on_terminated.set()

    @abstractmethod
    async def _create_socket(self) -> socket.socket:
        """Create connected wayland socket"""

    async def connect(self: C) -> C:
        """Start running wayland connection"""
        if self._socket is not None:
            raise RuntimeError("socket has already been set")
        self._socket = await self._create_socket()
        self._socket.setblocking(False)
        self._writer_enable()
        self._reader_enable()
        return self

    async def flush(self) -> None:
        """Wait for all pending events to be send"""
        await self._write_done.wait()

    async def __aenter__(self: C) -> C:
        return await self.connect()

    async def __aexit__(self, et: Any, *_: Any) -> None:
        if et is None:
            await self.on_terminated()
        else:
            self.terminate()

    def _writer_enable(self) -> None:
        if self._is_terminated:
            raise RuntimeError("connection has beend terminated")
        self._write_done.clear()
        if self._socket is not None:
            self._loop.add_writer(self._socket, self._writer)

    def _writer_disable(self) -> None:
        if self._socket is not None:
            self._loop.remove_writer(self._socket)
        self._write_done.set()

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
        offset = 0
        try:
            while offset < len(self._write_buff):
                try:
                    fds: List[int] = []
                    for fd in self._write_fds:
                        if isinstance(fd, _Fd):
                            fds.append(fd.fileno())
                        else:
                            fds.append(fd)
                    offset += socket.send_fds(
                        self._socket, [self._write_buff[offset:]], fds
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
        close = False
        while True:
            try:
                data, fds, _, _ = socket.recv_fds(self._socket, 4096, 32)
                if not data:
                    close = True
                    break
                self._read_fds.extend(open(fd, "w+b") for fd in fds)
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

        if close:
            self.terminate("connection closed")

    def _id_alloc(self) -> Id:
        if self._id_free:
            return self._id_free.pop()
        else:
            self._id_last = Id(self._id_last + 1)
            return self._id_last

    def _fd_recv(self) -> Optional[Fd]:
        """Pop next descriptor from file descriptor queue"""
        if self._read_fds:
            return self._read_fds.popleft()
        return None

    def _new_id_recv(self, id: Id, iface_name: str) -> Proxy:
        """Receive proxy with new_id command"""
        proxy_type = PROXIES.get(iface_name)
        if proxy_type is None:
            raise ValueError(f"failed to resolve proxy type {iface_name}")
        proxy = proxy_type(id, self)
        if self._is_server:
            iface = proxy_type.interface.swap_events_and_requests()
            proxy = Proxy(id, self, iface)
        else:
            proxy = proxy_type(id, self)
        self._proxies[id] = proxy
        proxy._is_attached = True
        return proxy

    def _delete_proxy(self, target: Union[Proxy, Id]) -> None:
        """Delete proxy"""
        id = target._id if isinstance(target, Proxy) else target
        proxy = self._proxies.pop(id, None)
        if proxy is not None:
            proxy._detach("deleted by server")
        self._id_free.append(id)

    def _message_submit(self, message: Message) -> None:
        """Submit message for writing"""
        if message.id not in self._proxies:
            raise RuntimeError("object has already been deleted")
        self._write_queue.append(message)
        self._writer_enable()


class Arg(ABC):
    type_name: ClassVar[str]
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def pack(self, write: io.BytesIO, value: Any) -> None:
        pass

    @abstractmethod
    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        pass

    def __str__(self) -> str:
        return f'{self.__class__.__name__}("{self.name}")'

    def __repr__(self) -> str:
        return str(self)


class ArgUInt(Arg):
    type_name: ClassVar[str] = "int"
    struct: ClassVar[Struct] = Struct("I")
    enum: Optional[str]

    def __init__(self, name: str, enum: Optional[str] = None):
        super().__init__(name)
        self.enum = enum

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if isinstance(value, Enum):
            write.write(self.struct.pack(value.value))
        elif isinstance(value, int) and value >= 0:
            write.write(self.struct.pack(value))
        else:
            raise TypeError(f"[{self.name}] unsigend integer expected")

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        return self.struct.unpack(read.read(self.struct.size))[0]

    def __str__(self) -> str:
        if self.enum:
            return f'ArgUInt("{self.name}", "{self.enum}")'
        return f'ArgUInt("{self.name}")'


class ArgInt(Arg):
    type_name: ClassVar[str] = "int"
    struct: ClassVar[Struct] = Struct("i")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, int):
            raise TypeError(f"[{self.name}] signed integer expected")
        write.write(self.struct.pack(value))

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        return self.struct.unpack(read.read(self.struct.size))[0]


class ArgFixed(Arg):
    """Signed 24.8 floating point value"""

    type_name: ClassVar[str] = "float"
    struct: ClassVar[Struct] = Struct("i")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError(f"[{self.name}]  float expected")
        value = (int(value) << 8) + int((value % 1.0) * 256)
        write.write(self.struct.pack(value))

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        value = self.struct.unpack(read.read(self.struct.size))[0]
        return float(value >> 8) + ((value & 0xFF) / 256.0)


class ArgStr(Arg):
    """String argument

    String is zero teminated and 32-bit aligned
    """

    type_name: ClassVar[str] = "str"
    struct: ClassVar[Struct] = Struct("I")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        data: bytes
        if isinstance(value, str):
            data = value.encode()
        elif isinstance(value, bytes):
            data = value
        else:
            raise TypeError(f"[{self.name}] string or bytes expected")
        size = len(data) + 1  # null terminated length
        write.write(self.struct.pack(size))
        write.write(data)
        # null terminated and padded to 32-bit
        padding = (-size % 4) + 1
        write.write(b"\x00" * padding)

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        size = self.struct.unpack(read.read(self.struct.size))[0]
        value = read.read(size - 1).decode()
        read.read((-size % 4) + 1)
        return value


class ArgArray(Arg):
    """Bytes argument

    Bytes are 32-bit aligned
    """

    type_name: ClassVar[str] = "bytes"
    struct: ClassVar[Struct] = Struct("I")

    def pack(self, write: io.BytesIO, value: Any) -> None:
        data: bytes
        if isinstance(value, str):
            data = value.encode()
        elif isinstance(value, bytes):
            data = value
        else:
            raise TypeError(f"[{self.name}] string or bytes expected")
        size = len(data)
        write.write(self.struct.pack(size))
        write.write(data)
        write.write(b"\x00" * (-size % 4))

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        size = self.struct.unpack(read.read(self.struct.size))[0]
        value = read.read(size)
        read.read(-size % 4)
        return value


class ArgNewId(Arg):
    type_name: ClassVar[str] = "Proxy"
    struct: ClassVar[Struct] = Struct("I")
    interface: Optional[str]

    def __init__(self, name: str, interface: Optional[str]):
        super().__init__(name)
        self.interface = interface

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if not isinstance(value, Proxy):
            raise TypeError(f"[{self.name}] proxy object expected got {value}")
        if value._is_attached:
            raise TypeError(f"[{self.name}] proxy has already been attached")
        value._is_attached = True
        if self.interface is not None and self.interface != value._interface.name:
            raise TypeError(
                f"[{self.name}] proxy object must implement '{self.interface}' "
                f"interface (given '{value._interface.name}'')"
            )
        write.write(self.struct.pack(value._id))

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        id = Id(self.struct.unpack(read.read(self.struct.size))[0])
        if id in connection._proxies:
            raise RuntimeError(f"[{self.name}] proxy with id={id} already exists")
        interface: Optional[str] = self.interface or hint
        if interface is None:
            raise RuntimeError(f"[{self.name}] cannot unpack proxy without intreface")
        return connection._new_id_recv(id, interface)

    def __str__(self) -> str:
        interface = f'"{self.interface}"' if self.interface is not None else "None"
        return f'ArgNewId("{self.name}", {interface})'


class ArgObject(Arg):
    type_name: ClassVar[str] = "Proxy"
    struct: ClassVar[Struct] = Struct("I")
    interface: Optional[str]
    optional: bool

    def __init__(self, name: str, interface: Optional[str], optional: bool = False):
        super().__init__(name)
        self.interface = interface
        self.optional = optional

    def pack(self, write: io.BytesIO, value: Any) -> None:
        if self.optional and value is None:
            write.write(self.struct.pack(0))
        if not isinstance(value, Proxy):
            raise TypeError(f"[{self.name}] proxy object expected {value}")
        if self.interface is not None and self.interface != value._interface.name:
            raise TypeError(
                f"[{self.name}] proxy object must implement '{self.interface}' "
                f"interface (given '{value._interface.name}'')"
            )
        write.write(self.struct.pack(value._id))

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        id = self.struct.unpack(read.read(self.struct.size))[0]
        if self.optional and id == 0:
            return None
        proxy = connection._proxies.get(id)
        if proxy is None:
            raise RuntimeError("[{self.name}] unknown incomming object")
        return proxy

    def __str__(self) -> str:
        interface = f'"{self.interface}"' if self.interface is not None else "None"
        if self.optional:
            return f'ArgObject("{self.name}", {interface}, True)'
        else:
            return f'ArgObject("{self.name}", {interface})'


class ArgFd(Arg):
    type_name: ClassVar[str] = "Fd"

    def pack(self, write: io.BytesIO, value: Any) -> None:
        # not actually writing anything, magic happanes on the _writer side
        pass

    def unpack(
        self,
        read: io.BytesIO,
        connection: Connection,
        hint: Optional[Any] = None,
    ) -> Any:
        fd = connection._fd_recv()
        if fd is None:
            raise RuntimeError(f"[{self.name}] expected file descriptor")
        return fd


class Interface:
    __slots__ = [
        "name",
        "events",
        "requests",
        "requests_by_name",
        "events_by_name",
        "enums",
        "summary",
        "unpack_enum",
    ]
    name: str
    events: List[WEvent]
    events_by_name: Dict[str, Tuple[OpCode, WEvent]]
    requests: List[WRequest]
    requests_by_name: Dict[str, Tuple[OpCode, WRequest]]
    enums: List[WEnum]
    summary: Optional[str]
    unpack_enum: Optional[Callable[[str, int], Any]]

    def __init__(
        self,
        name: str,
        requests: List[WRequest],
        events: List[WEvent],
        enums: List[WEnum],
        summary: Optional[str] = None,
    ) -> None:
        self.name = name
        self.requests = requests
        self.events = events
        self.enums = enums
        self.summary = summary
        self.unpack_enum = None

        self.requests_by_name = {}
        for opcode, request in enumerate(requests):
            self.requests_by_name[request.name] = (OpCode(opcode), request)
        self.events_by_name = {}
        for opcode, event in enumerate(events):
            self.events_by_name[event.name] = (OpCode(opcode), event)

    def pack(
        self,
        opcode: OpCode,
        args: Tuple[Any, ...],
    ) -> Tuple[bytes, List[Fd]]:
        """Pack arguments for the specified opcode

        Returns bytes data and descritpros to be send
        """
        req = self.requests[opcode]
        if len(args) != len(req.args):
            raise TypeError(
                f"[{self.name}.{req.name}] takes {len(req.args)} arguments ({len(args)} given)"
            )
        write = io.BytesIO()
        fds: List[Fd] = []
        for arg, arg_desc in zip(args, req.args):
            arg_desc.pack(write, arg)
            if isinstance(arg_desc, ArgFd):
                if isinstance(arg, (int, _Fd)):
                    fds.append(arg)
                else:
                    raise TypeError(
                        f"[{self.name}.{req.name}({arg_desc.name})] "
                        f"expected file descriptor '{arg}'"
                    )
        return write.getvalue(), fds

    def unpack(
        self,
        connection: Connection,
        opcode: OpCode,
        data: bytes,
    ) -> List[Any]:
        """Unpack opcode and data into request name and list of arguments"""
        if opcode >= len(self.events):
            raise RuntimeError(f"[{self.name}] received unknown event {opcode}")
        request = self.events[opcode]
        read = io.BytesIO(data)
        args: List[Any] = []
        for index, arg_desc in enumerate(request.args):
            if (
                isinstance(arg_desc, ArgUInt)
                and arg_desc.enum is not None
                and self.unpack_enum is not None
            ):
                args.append(
                    self.unpack_enum(arg_desc.enum, arg_desc.unpack(read, connection))
                )
            elif isinstance(arg_desc, ArgNewId) and arg_desc.interface is None:
                args.append(arg_desc.unpack(read, connection, args[index - 2]))
            else:
                args.append(arg_desc.unpack(read, connection))
        return args

    def swap_events_and_requests(self) -> Interface:
        """Create new interface with swapped events and requests"""
        return Interface(
            name=self.name,
            requests=[event.to_request() for event in self.events],
            events=[request.to_event() for request in self.requests],
            enums=self.enums,
            summary=self.summary,
        )

    def __repr__(self) -> str:
        return self.name


EventHandler = Callable[..., bool]


class Proxy:
    __slots__ = [
        "_id",
        "_interface",
        "_connection",
        "_is_attached",
        "_is_detached",
        "_handlers",
        "_futures",
    ]
    interface: ClassVar[Interface]
    _id: Id
    _interface: Interface
    _connection: Connection
    _is_attached: bool
    _is_detached: bool
    _handlers: List[Optional[EventHandler]]
    _futures: WeakSet[Future[Any]]

    def __init__(
        self,
        id: Id,
        connection: Connection,
        interface: Optional[Interface] = None,
    ) -> None:
        if interface is None:
            # interface must always be provided and only seem optional for typechecker
            raise RuntimeError("interface must be providied")
        self._id = id
        self._interface = interface
        self._connection = connection
        self._is_attached = False
        self._is_detached = False
        self._handlers = [None] * len(interface.events)
        self._futures = WeakSet()

    def __call__(self, name: str, *args: Any) -> None:
        if not self._is_attached or self._is_detached:
            raise RuntimeError(f"[{self}] {name}({args}) proxy is not attached")
        desc = self._interface.requests_by_name.get(name)
        if desc is None:
            raise ValueError(f"[{self}] does not have request '{name}'")
        opcode, _ = desc
        self._call(opcode, args)

    def _call(self, opcode: OpCode, args: Tuple[Any, ...]) -> None:
        if self._connection._debug:
            print(f" -> {self._call_fmt(opcode, args)}", file=sys.stderr)
        data, fds = self._interface.pack(opcode, args)
        self._connection._message_submit(Message(self._id, opcode, data, fds))

    def _call_fmt(self, opcode: OpCode, args: Tuple[Any, ...]) -> str:
        request = self._interface.requests[opcode]
        args_repr = ", ".join(
            f"{arg.name}={repr(value)}" for arg, value in zip(request.args, args)
        )
        return f"{self}.{request.name}({args_repr})"

    def on(self, name: str, handler: EventHandler) -> Optional[EventHandler]:
        """Register handler for the event"""
        if self._is_detached:
            raise RuntimeError(f"[{self}] is deleted")
        desc = self._interface.events_by_name.get(name)
        if desc is None:
            raise ValueError(f"[{self}] does not have event '{name}'")
        opcode, _ = desc
        old_handler, self._handlers[opcode] = self._handlers[opcode], handler
        return old_handler

    def on_async(self, name: str) -> Future[Tuple[Any, ...]]:
        """Create future which is resolved on event"""

        def handler(*args: Any) -> bool:
            future.set_result(args)
            return False

        self.on(name, handler)
        future: Future[Tuple[Any, ...]] = asyncio.get_running_loop().create_future()
        self._futures.add(future)

        return future

    def _dispatch(self, opcode: OpCode, args: List[Any]) -> None:
        """Dispatch event to the handler"""
        if self._connection._debug:
            print(f"{self._dispatch_fmt(opcode, args)}", file=sys.stderr)
        handler = self._handlers[opcode]
        if handler is None:
            fmt = self._dispatch_fmt(opcode, args)
            print(f"\x1b[93mUNHANDLED: {fmt}\x1b[m", file=sys.stderr)
            return
        try:
            if not handler(*args):
                self._handlers[opcode] = None
        except Exception:
            event = self._interface.events[opcode]
            logging.exception(f"[{self}.{event.name}] handler raised an error")
            self._handlers[opcode] = None

    def _dispatch_fmt(self, opcode: OpCode, args: List[Any]) -> str:
        """Format incomming message"""
        event = self._interface.events[opcode]
        args_repr = ", ".join(
            f"{arg.name}={repr(value)}" for arg, value in zip(event.args, args)
        )
        return f"{self}.{event.name}({args_repr})"

    def _detach(self, msg: str) -> None:
        is_detached, self._is_detached = self._is_detached, True
        if is_detached:
            return None
        for future in self._futures:
            future.cancel(f"{self} {msg}")
        self._futures.clear()

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self._interface.name}@{self._id}"


class WRequest(NamedTuple):
    name: str
    args: List[Arg]
    summary: Optional[str] = None
    destructor: bool = False

    def to_event(self) -> WEvent:
        """Convert request definition to event definition"""
        return WEvent(self.name, self.args, self.summary)


class WEvent(NamedTuple):
    name: str
    args: List[Arg]
    summary: Optional[str] = None

    def to_request(self) -> WRequest:
        """Convert event definition to request definition"""
        return WRequest(self.name, self.args, self.summary)


class WEnum:
    name: str
    values: Dict[str, int]
    flag: bool

    def __init__(self, name: str, values: Dict[str, int], flag: bool = False):
        self.name = name
        self.values = values
        self.flag = flag


class Protocol:
    __slots__ = ["name", "interfaces", "extern"]
    name: str
    interfaces: Dict[str, Interface]
    extern: Set[str]

    def __init__(
        self,
        name: str,
        interfaces: Dict[str, Interface],
        extern: Set[str],
    ):
        self.name = name
        self.interfaces = interfaces
        self.extern = extern

    def __str__(self) -> str:
        return f'<Protocol(name="{self.name}")>'

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, name: str) -> Interface:
        return self.interfaces[name]

    @classmethod
    def load(cls, path: str) -> Protocol:
        """Load interfaces from protocol XML file"""
        root = ElementTree.parse(path).getroot()

        ifaces: Dict[str, Interface] = {}
        extern: Set[str] = set()
        protocol_name = root.get("name")
        if protocol_name is None:
            raise ValueError("protocol must define name attribute")

        for node in root:
            if node.tag != "interface":
                continue
            iface_name = node.get("name")
            if iface_name is None:
                raise ValueError("interface must have name attribute")

            events: List[WEvent] = []
            requests: List[WRequest] = []
            enums: List[WEnum] = []
            iface_summary: Optional[str] = None

            for child in node:
                if child.tag in {"request", "event"}:
                    name = child.get("name")
                    if name is None:
                        raise ValueError(f"[{iface_name}] {child.tag} without a name")
                    args: List[Arg] = []
                    summary: Optional[str] = None
                    for arg_node in child:
                        if arg_node.tag == "description":
                            summary = arg_node.get("summary")
                            continue
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
                            enum_name = arg_node.get("enum")
                            args.append(ArgUInt(arg_name, enum_name))
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
                            arg_iface = arg_node.get("interface")
                            if arg_iface is not None:
                                extern.add(arg_iface)
                            optional = arg_node.get("allow-null") == "true"
                            args.append(ArgObject(arg_name, arg_iface, optional))
                        elif arg_type == "new_id":
                            arg_iface = arg_node.get("interface")
                            if arg_iface is not None:
                                extern.add(arg_iface)
                                args.append(ArgNewId(arg_name, arg_iface))
                            else:
                                # new_id without interface is unpacked into 3 arguments
                                # (interface_name: str, version: uint, id: new_id)
                                args.append(ArgStr(f"{arg_name}_interface"))
                                args.append(ArgUInt(f"{arg_name}_version"))
                                args.append(ArgNewId(arg_name, None))

                    if child.tag == "request":
                        destructor = child.get("type") == "destructor"
                        requests.append(WRequest(name, args, summary, destructor))
                    else:
                        events.append(WEvent(name, args, summary))

                elif child.tag == "enum":
                    name = child.get("name")
                    if name is None:
                        raise ValueError(f"[{iface_name}] `{child.tag}` without a name")
                    enum: Dict[str, int] = {}
                    for var in child:
                        if var.tag != "entry":
                            continue
                        var_name = var.get("name")
                        if var_name is None:
                            raise ValueError(
                                f"[{iface_name}.{name}] `{var.tag}` without a name"
                            )
                        value_str = var.get("value")
                        if value_str is None:
                            raise ValueError(
                                f"[{iface_name}.{name}] `{var.tag}` without a value"
                            )
                        if value_str.startswith("0x"):
                            value = int(value_str[2:], 16)
                        else:
                            value = int(value_str)
                        enum[var_name] = value
                    flag = child.get("bitfield") == "true"
                    enums.append(WEnum(name, enum, flag))

                elif child.tag == "description":
                    iface_summary = child.get("summary")

            iface = Interface(iface_name, requests, events, enums, iface_summary)
            ifaces[iface_name] = iface

        extern -= set(ifaces)
        return Protocol(protocol_name, ifaces, extern)


@runtime_checkable
class _Fd(Proto):
    def fileno(self) -> int:
        ...


Fd = Union[_Fd, int]


class SharedMemory:
    """Create shared memory file

    This can be send over to wayland compositor, or converted to numpy array:
        shm = SharedMemory(8192)
        array = numpy.ndarray(shape=(32,32), dtype=float, shm.buf)
    """

    __slots__ = ["_fd", "_mmap", "_is_closed"]
    _fd: int
    _mmap: mmap
    _is_closed: bool

    def __init__(self, size: int, fd: Optional[Fd] = None) -> None:
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
            if isinstance(fd, int):
                self._fd = fd
            else:
                self._fd = os.dup(fd.fileno())
            self._mmap = mmap(self._fd, size)

    def fileno(self) -> int:
        if self._is_closed:
            raise RuntimeError("shared memory file is closed")
        return self._fd

    @property
    def buf(self) -> memoryview:
        return cast(memoryview, self._mmap)

    def close(self) -> None:
        is_closed, self._is_closed = self._is_closed, True
        if is_closed:
            return
        os.close(self._fd)
        self._mmap.close()

    def __del__(self) -> None:
        return self.close()

    def __str__(self) -> str:
        return f"SharedMemory(fd={self._fd}, size={len(self._mmap)})"

    def __repr__(self) -> str:
        return str(self)
