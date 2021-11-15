# Auto generated do not edit manually
# fmt: off
# pyright: reportPrivateUsage=false
from __future__ import annotations
from enum import Enum, Flag
from typing import Any, Callable, ClassVar, Optional
from ..base import *

__all__ = [
    "WlDisplay",
    "WlRegistry",
    "WlCallback",
    "WlCompositor",
    "WlShmPool",
    "WlShm",
    "WlBuffer",
    "WlDataOffer",
    "WlDataSource",
    "WlDataDevice",
    "WlDataDeviceManager",
    "WlShell",
    "WlShellSurface",
    "WlSurface",
    "WlSeat",
    "WlPointer",
    "WlKeyboard",
    "WlTouch",
    "WlOutput",
    "WlRegion",
    "WlSubcompositor",
    "WlSubsurface",
]

class WlDisplay(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_display",
        requests=[
            ("sync", [ArgNewId("callback", "wl_callback")]),
            ("get_registry", [ArgNewId("registry", "wl_registry")]),
        ],
        events=[
            ("error", [ArgObject("object_id", None), ArgUInt("code"), ArgStr("message")]),
            ("delete_id", [ArgUInt("id")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_object": 0,
                    "invalid_method": 1,
                    "no_memory": 2,
                    "implementation": 3,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def sync(self) -> WlCallback:
        _opcode = OpCode(0)
        callback = self._connection.create_proxy(WlCallback)
        _data, _fds = self._interface.pack(_opcode, (callback,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return callback

    def get_registry(self) -> WlRegistry:
        _opcode = OpCode(1)
        registry = self._connection.create_proxy(WlRegistry)
        _data, _fds = self._interface.pack(_opcode, (registry,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return registry

    def on_error(self, handler: Callable[[Proxy, int, str], bool]) -> Optional[Callable[[Proxy, int, str], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_delete_id(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_OBJECT = 0
        INVALID_METHOD = 1
        NO_MEMORY = 2
        IMPLEMENTATION = 3

class WlRegistry(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_registry",
        requests=[
            ("bind", [ArgUInt("name"), ArgStr("id_interface"), ArgUInt("id_version"), ArgNewId("id", None)]),
        ],
        events=[
            ("global", [ArgUInt("name"), ArgStr("interface"), ArgUInt("version")]),
            ("global_remove", [ArgUInt("name")]),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def bind(self, name: int, id_interface: str, id_version: int, id: Proxy) -> None:
        _opcode = OpCode(0)
        _proxy_iface = id._interface.name
        if _proxy_iface != id_interface:
            raise TypeError("[{}(id)] expected {} (got {})"
                            .format(self, id_interface, _proxy_iface))
        _data, _fds = self._interface.pack(_opcode, (name, id_interface, id_version, id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_global(self, handler: Callable[[int, str, int], bool]) -> Optional[Callable[[int, str, int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_global_remove(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlCallback(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_callback",
        requests=[
        ],
        events=[
            ("done", [ArgUInt("callback_data")]),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def on_done(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlCompositor(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_compositor",
        requests=[
            ("create_surface", [ArgNewId("id", "wl_surface")]),
            ("create_region", [ArgNewId("id", "wl_region")]),
        ],
        events=[
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def create_surface(self) -> WlSurface:
        _opcode = OpCode(0)
        id = self._connection.create_proxy(WlSurface)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def create_region(self) -> WlRegion:
        _opcode = OpCode(1)
        id = self._connection.create_proxy(WlRegion)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

class WlShmPool(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_shm_pool",
        requests=[
            ("create_buffer", [ArgNewId("id", "wl_buffer"), ArgInt("offset"), ArgInt("width"), ArgInt("height"), ArgInt("stride"), ArgUInt("format", "wl_shm.format")]),
            ("destroy", []),
            ("resize", [ArgInt("size")]),
        ],
        events=[
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def create_buffer(self, offset: int, width: int, height: int, stride: int, format: WlShm.Format) -> WlBuffer:
        _opcode = OpCode(0)
        id = self._connection.create_proxy(WlBuffer)
        _data, _fds = self._interface.pack(_opcode, (id, offset, width, height, stride, format,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def destroy(self) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def resize(self, size: int) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (size,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlShmPool:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

class WlShm(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_shm",
        requests=[
            ("create_pool", [ArgNewId("id", "wl_shm_pool"), ArgFd("fd"), ArgInt("size")]),
        ],
        events=[
            ("format", [ArgUInt("format", "format")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_format": 0,
                    "invalid_stride": 1,
                    "invalid_fd": 2,
                },
            ),
            WEnum(
                name="format",
                values={
                    "argb8888": 0,
                    "xrgb8888": 1,
                    "c8": 538982467,
                    "rgb332": 943867730,
                    "bgr233": 944916290,
                    "xrgb4444": 842093144,
                    "xbgr4444": 842089048,
                    "rgbx4444": 842094674,
                    "bgrx4444": 842094658,
                    "argb4444": 842093121,
                    "abgr4444": 842089025,
                    "rgba4444": 842088786,
                    "bgra4444": 842088770,
                    "xrgb1555": 892424792,
                    "xbgr1555": 892420696,
                    "rgbx5551": 892426322,
                    "bgrx5551": 892426306,
                    "argb1555": 892424769,
                    "abgr1555": 892420673,
                    "rgba5551": 892420434,
                    "bgra5551": 892420418,
                    "rgb565": 909199186,
                    "bgr565": 909199170,
                    "rgb888": 875710290,
                    "bgr888": 875710274,
                    "xbgr8888": 875709016,
                    "rgbx8888": 875714642,
                    "bgrx8888": 875714626,
                    "abgr8888": 875708993,
                    "rgba8888": 875708754,
                    "bgra8888": 875708738,
                    "xrgb2101010": 808669784,
                    "xbgr2101010": 808665688,
                    "rgbx1010102": 808671314,
                    "bgrx1010102": 808671298,
                    "argb2101010": 808669761,
                    "abgr2101010": 808665665,
                    "rgba1010102": 808665426,
                    "bgra1010102": 808665410,
                    "yuyv": 1448695129,
                    "yvyu": 1431918169,
                    "uyvy": 1498831189,
                    "vyuy": 1498765654,
                    "ayuv": 1448433985,
                    "nv12": 842094158,
                    "nv21": 825382478,
                    "nv16": 909203022,
                    "nv61": 825644622,
                    "yuv410": 961959257,
                    "yvu410": 961893977,
                    "yuv411": 825316697,
                    "yvu411": 825316953,
                    "yuv420": 842093913,
                    "yvu420": 842094169,
                    "yuv422": 909202777,
                    "yvu422": 909203033,
                    "yuv444": 875713881,
                    "yvu444": 875714137,
                    "r8": 538982482,
                    "r16": 540422482,
                    "rg88": 943212370,
                    "gr88": 943215175,
                    "rg1616": 842221394,
                    "gr1616": 842224199,
                    "xrgb16161616f": 1211388504,
                    "xbgr16161616f": 1211384408,
                    "argb16161616f": 1211388481,
                    "abgr16161616f": 1211384385,
                    "xyuv8888": 1448434008,
                    "vuy888": 875713878,
                    "vuy101010": 808670550,
                    "y210": 808530521,
                    "y212": 842084953,
                    "y216": 909193817,
                    "y410": 808531033,
                    "y412": 842085465,
                    "y416": 909194329,
                    "xvyu2101010": 808670808,
                    "xvyu12_16161616": 909334104,
                    "xvyu16161616": 942954072,
                    "y0l0": 810299481,
                    "x0l0": 810299480,
                    "y0l2": 843853913,
                    "x0l2": 843853912,
                    "yuv420_8bit": 942691673,
                    "yuv420_10bit": 808539481,
                    "xrgb8888_a8": 943805016,
                    "xbgr8888_a8": 943800920,
                    "rgbx8888_a8": 943806546,
                    "bgrx8888_a8": 943806530,
                    "rgb888_a8": 943798354,
                    "bgr888_a8": 943798338,
                    "rgb565_a8": 943797586,
                    "bgr565_a8": 943797570,
                    "nv24": 875714126,
                    "nv42": 842290766,
                    "p210": 808530512,
                    "p010": 808530000,
                    "p012": 842084432,
                    "p016": 909193296,
                    "axbxgxrx106106106106": 808534593,
                    "nv15": 892425806,
                    "q410": 808531025,
                    "q401": 825242705,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def create_pool(self, fd: Fd, size: int) -> WlShmPool:
        _opcode = OpCode(0)
        id = self._connection.create_proxy(WlShmPool)
        _data, _fds = self._interface.pack(_opcode, (id, fd, size,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def on_format(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_FORMAT = 0
        INVALID_STRIDE = 1
        INVALID_FD = 2

    class Format(Enum):
        ARGB8888 = 0
        XRGB8888 = 1
        C8 = 538982467
        RGB332 = 943867730
        BGR233 = 944916290
        XRGB4444 = 842093144
        XBGR4444 = 842089048
        RGBX4444 = 842094674
        BGRX4444 = 842094658
        ARGB4444 = 842093121
        ABGR4444 = 842089025
        RGBA4444 = 842088786
        BGRA4444 = 842088770
        XRGB1555 = 892424792
        XBGR1555 = 892420696
        RGBX5551 = 892426322
        BGRX5551 = 892426306
        ARGB1555 = 892424769
        ABGR1555 = 892420673
        RGBA5551 = 892420434
        BGRA5551 = 892420418
        RGB565 = 909199186
        BGR565 = 909199170
        RGB888 = 875710290
        BGR888 = 875710274
        XBGR8888 = 875709016
        RGBX8888 = 875714642
        BGRX8888 = 875714626
        ABGR8888 = 875708993
        RGBA8888 = 875708754
        BGRA8888 = 875708738
        XRGB2101010 = 808669784
        XBGR2101010 = 808665688
        RGBX1010102 = 808671314
        BGRX1010102 = 808671298
        ARGB2101010 = 808669761
        ABGR2101010 = 808665665
        RGBA1010102 = 808665426
        BGRA1010102 = 808665410
        YUYV = 1448695129
        YVYU = 1431918169
        UYVY = 1498831189
        VYUY = 1498765654
        AYUV = 1448433985
        NV12 = 842094158
        NV21 = 825382478
        NV16 = 909203022
        NV61 = 825644622
        YUV410 = 961959257
        YVU410 = 961893977
        YUV411 = 825316697
        YVU411 = 825316953
        YUV420 = 842093913
        YVU420 = 842094169
        YUV422 = 909202777
        YVU422 = 909203033
        YUV444 = 875713881
        YVU444 = 875714137
        R8 = 538982482
        R16 = 540422482
        RG88 = 943212370
        GR88 = 943215175
        RG1616 = 842221394
        GR1616 = 842224199
        XRGB16161616F = 1211388504
        XBGR16161616F = 1211384408
        ARGB16161616F = 1211388481
        ABGR16161616F = 1211384385
        XYUV8888 = 1448434008
        VUY888 = 875713878
        VUY101010 = 808670550
        Y210 = 808530521
        Y212 = 842084953
        Y216 = 909193817
        Y410 = 808531033
        Y412 = 842085465
        Y416 = 909194329
        XVYU2101010 = 808670808
        XVYU12_16161616 = 909334104
        XVYU16161616 = 942954072
        Y0L0 = 810299481
        X0L0 = 810299480
        Y0L2 = 843853913
        X0L2 = 843853912
        YUV420_8BIT = 942691673
        YUV420_10BIT = 808539481
        XRGB8888_A8 = 943805016
        XBGR8888_A8 = 943800920
        RGBX8888_A8 = 943806546
        BGRX8888_A8 = 943806530
        RGB888_A8 = 943798354
        BGR888_A8 = 943798338
        RGB565_A8 = 943797586
        BGR565_A8 = 943797570
        NV24 = 875714126
        NV42 = 842290766
        P210 = 808530512
        P010 = 808530000
        P012 = 842084432
        P016 = 909193296
        AXBXGXRX106106106106 = 808534593
        NV15 = 892425806
        Q410 = 808531025
        Q401 = 825242705

class WlBuffer(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_buffer",
        requests=[
            ("destroy", []),
        ],
        events=[
            ("release", []),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlBuffer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_release(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlDataOffer(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_data_offer",
        requests=[
            ("accept", [ArgUInt("serial"), ArgStr("mime_type")]),
            ("receive", [ArgStr("mime_type"), ArgFd("fd")]),
            ("destroy", []),
            ("finish", []),
            ("set_actions", [ArgUInt("dnd_actions", "wl_data_device_manager.dnd_action"), ArgUInt("preferred_action", "wl_data_device_manager.dnd_action")]),
        ],
        events=[
            ("offer", [ArgStr("mime_type")]),
            ("source_actions", [ArgUInt("source_actions", "wl_data_device_manager.dnd_action")]),
            ("action", [ArgUInt("dnd_action", "wl_data_device_manager.dnd_action")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_finish": 0,
                    "invalid_action_mask": 1,
                    "invalid_action": 2,
                    "invalid_offer": 3,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def accept(self, serial: int, mime_type: str) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, (serial, mime_type,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def receive(self, mime_type: str, fd: Fd) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (mime_type, fd,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def destroy(self) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def finish(self) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_actions(self, dnd_actions: WlDataDeviceManager.DndAction, preferred_action: WlDataDeviceManager.DndAction) -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (dnd_actions, preferred_action,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlDataOffer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_offer(self, handler: Callable[[str], bool]) -> Optional[Callable[[str], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_source_actions(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_action(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_FINISH = 0
        INVALID_ACTION_MASK = 1
        INVALID_ACTION = 2
        INVALID_OFFER = 3

class WlDataSource(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_data_source",
        requests=[
            ("offer", [ArgStr("mime_type")]),
            ("destroy", []),
            ("set_actions", [ArgUInt("dnd_actions", "wl_data_device_manager.dnd_action")]),
        ],
        events=[
            ("target", [ArgStr("mime_type")]),
            ("send", [ArgStr("mime_type"), ArgFd("fd")]),
            ("cancelled", []),
            ("dnd_drop_performed", []),
            ("dnd_finished", []),
            ("action", [ArgUInt("dnd_action", "wl_data_device_manager.dnd_action")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_action_mask": 0,
                    "invalid_source": 1,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def offer(self, mime_type: str) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, (mime_type,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def destroy(self) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_actions(self, dnd_actions: WlDataDeviceManager.DndAction) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (dnd_actions,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlDataSource:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_target(self, handler: Callable[[str], bool]) -> Optional[Callable[[str], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_send(self, handler: Callable[[str, Fd], bool]) -> Optional[Callable[[str, Fd], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_cancelled(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_dnd_drop_performed(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_dnd_finished(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_action(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_ACTION_MASK = 0
        INVALID_SOURCE = 1

class WlDataDevice(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_data_device",
        requests=[
            ("start_drag", [ArgObject("source", "wl_data_source", True), ArgObject("origin", "wl_surface"), ArgObject("icon", "wl_surface", True), ArgUInt("serial")]),
            ("set_selection", [ArgObject("source", "wl_data_source", True), ArgUInt("serial")]),
            ("release", []),
        ],
        events=[
            ("data_offer", [ArgNewId("id", "wl_data_offer")]),
            ("enter", [ArgUInt("serial"), ArgObject("surface", "wl_surface"), ArgFixed("x"), ArgFixed("y"), ArgObject("id", "wl_data_offer", True)]),
            ("leave", []),
            ("motion", [ArgUInt("time"), ArgFixed("x"), ArgFixed("y")]),
            ("drop", []),
            ("selection", [ArgObject("id", "wl_data_offer", True)]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "role": 0,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def start_drag(self, source: Optional[WlDataSource], origin: WlSurface, icon: Optional[WlSurface], serial: int) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, (source, origin, icon, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_selection(self, source: Optional[WlDataSource], serial: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (source, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def release(self) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_data_offer(self, handler: Callable[[WlDataOffer], bool]) -> Optional[Callable[[WlDataOffer], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_enter(self, handler: Callable[[int, WlSurface, float, float, Optional[WlDataOffer]], bool]) -> Optional[Callable[[int, WlSurface, float, float, Optional[WlDataOffer]], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_motion(self, handler: Callable[[int, float, float], bool]) -> Optional[Callable[[int, float, float], bool]]:
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_drop(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_selection(self, handler: Callable[[Optional[WlDataOffer]], bool]) -> Optional[Callable[[Optional[WlDataOffer]], bool]]:
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        ROLE = 0

class WlDataDeviceManager(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_data_device_manager",
        requests=[
            ("create_data_source", [ArgNewId("id", "wl_data_source")]),
            ("get_data_device", [ArgNewId("id", "wl_data_device"), ArgObject("seat", "wl_seat")]),
        ],
        events=[
        ],
        enums=[
            WEnum(
                name="dnd_action",
                values={
                    "none": 0,
                    "copy": 1,
                    "move": 2,
                    "ask": 4,
                },
                flag=True,
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def create_data_source(self) -> WlDataSource:
        _opcode = OpCode(0)
        id = self._connection.create_proxy(WlDataSource)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_data_device(self, seat: WlSeat) -> WlDataDevice:
        _opcode = OpCode(1)
        id = self._connection.create_proxy(WlDataDevice)
        _data, _fds = self._interface.pack(_opcode, (id, seat,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    class DndAction(Flag):
        NONE = 0
        COPY = 1
        MOVE = 2
        ASK = 4

class WlShell(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_shell",
        requests=[
            ("get_shell_surface", [ArgNewId("id", "wl_shell_surface"), ArgObject("surface", "wl_surface")]),
        ],
        events=[
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "role": 0,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def get_shell_surface(self, surface: WlSurface) -> WlShellSurface:
        _opcode = OpCode(0)
        id = self._connection.create_proxy(WlShellSurface)
        _data, _fds = self._interface.pack(_opcode, (id, surface,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    class Error(Enum):
        ROLE = 0

class WlShellSurface(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_shell_surface",
        requests=[
            ("pong", [ArgUInt("serial")]),
            ("move", [ArgObject("seat", "wl_seat"), ArgUInt("serial")]),
            ("resize", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgUInt("edges", "resize")]),
            ("set_toplevel", []),
            ("set_transient", [ArgObject("parent", "wl_surface"), ArgInt("x"), ArgInt("y"), ArgUInt("flags", "transient")]),
            ("set_fullscreen", [ArgUInt("method", "fullscreen_method"), ArgUInt("framerate"), ArgObject("output", "wl_output", True)]),
            ("set_popup", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgObject("parent", "wl_surface"), ArgInt("x"), ArgInt("y"), ArgUInt("flags", "transient")]),
            ("set_maximized", [ArgObject("output", "wl_output", True)]),
            ("set_title", [ArgStr("title")]),
            ("set_class", [ArgStr("class_")]),
        ],
        events=[
            ("ping", [ArgUInt("serial")]),
            ("configure", [ArgUInt("edges", "resize"), ArgInt("width"), ArgInt("height")]),
            ("popup_done", []),
        ],
        enums=[
            WEnum(
                name="resize",
                values={
                    "none": 0,
                    "top": 1,
                    "bottom": 2,
                    "left": 4,
                    "top_left": 5,
                    "bottom_left": 6,
                    "right": 8,
                    "top_right": 9,
                    "bottom_right": 10,
                },
                flag=True,
            ),
            WEnum(
                name="transient",
                values={
                    "inactive": 1,
                },
                flag=True,
            ),
            WEnum(
                name="fullscreen_method",
                values={
                    "default": 0,
                    "scale": 1,
                    "driver": 2,
                    "fill": 3,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def pong(self, serial: int) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def move(self, seat: WlSeat, serial: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (seat, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def resize(self, seat: WlSeat, serial: int, edges: Resize) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (seat, serial, edges,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_toplevel(self) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_transient(self, parent: WlSurface, x: int, y: int, flags: Transient) -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (parent, x, y, flags,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_fullscreen(self, method: FullscreenMethod, framerate: int, output: Optional[WlOutput]) -> None:
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, (method, framerate, output,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_popup(self, seat: WlSeat, serial: int, parent: WlSurface, x: int, y: int, flags: Transient) -> None:
        _opcode = OpCode(6)
        _data, _fds = self._interface.pack(_opcode, (seat, serial, parent, x, y, flags,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_maximized(self, output: Optional[WlOutput]) -> None:
        _opcode = OpCode(7)
        _data, _fds = self._interface.pack(_opcode, (output,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_title(self, title: str) -> None:
        _opcode = OpCode(8)
        _data, _fds = self._interface.pack(_opcode, (title,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_class(self, class_: str) -> None:
        _opcode = OpCode(9)
        _data, _fds = self._interface.pack(_opcode, (class_,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_ping(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_configure(self, handler: Callable[[int, int, int], bool]) -> Optional[Callable[[int, int, int], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_popup_done(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Resize(Flag):
        NONE = 0
        TOP = 1
        BOTTOM = 2
        LEFT = 4
        TOP_LEFT = 5
        BOTTOM_LEFT = 6
        RIGHT = 8
        TOP_RIGHT = 9
        BOTTOM_RIGHT = 10

    class Transient(Flag):
        INACTIVE = 1

    class FullscreenMethod(Enum):
        DEFAULT = 0
        SCALE = 1
        DRIVER = 2
        FILL = 3

class WlSurface(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_surface",
        requests=[
            ("destroy", []),
            ("attach", [ArgObject("buffer", "wl_buffer", True), ArgInt("x"), ArgInt("y")]),
            ("damage", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            ("frame", [ArgNewId("callback", "wl_callback")]),
            ("set_opaque_region", [ArgObject("region", "wl_region", True)]),
            ("set_input_region", [ArgObject("region", "wl_region", True)]),
            ("commit", []),
            ("set_buffer_transform", [ArgInt("transform")]),
            ("set_buffer_scale", [ArgInt("scale")]),
            ("damage_buffer", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
        ],
        events=[
            ("enter", [ArgObject("output", "wl_output")]),
            ("leave", [ArgObject("output", "wl_output")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_scale": 0,
                    "invalid_transform": 1,
                    "invalid_size": 2,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def attach(self, buffer: Optional[WlBuffer], x: int, y: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (buffer, x, y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def damage(self, x: int, y: int, width: int, height: int) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def frame(self) -> WlCallback:
        _opcode = OpCode(3)
        callback = self._connection.create_proxy(WlCallback)
        _data, _fds = self._interface.pack(_opcode, (callback,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return callback

    def set_opaque_region(self, region: Optional[WlRegion]) -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (region,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_input_region(self, region: Optional[WlRegion]) -> None:
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, (region,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def commit(self) -> None:
        _opcode = OpCode(6)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_buffer_transform(self, transform: int) -> None:
        _opcode = OpCode(7)
        _data, _fds = self._interface.pack(_opcode, (transform,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_buffer_scale(self, scale: int) -> None:
        _opcode = OpCode(8)
        _data, _fds = self._interface.pack(_opcode, (scale,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def damage_buffer(self, x: int, y: int, width: int, height: int) -> None:
        _opcode = OpCode(9)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlSurface:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_enter(self, handler: Callable[[WlOutput], bool]) -> Optional[Callable[[WlOutput], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[WlOutput], bool]) -> Optional[Callable[[WlOutput], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_SCALE = 0
        INVALID_TRANSFORM = 1
        INVALID_SIZE = 2

class WlSeat(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_seat",
        requests=[
            ("get_pointer", [ArgNewId("id", "wl_pointer")]),
            ("get_keyboard", [ArgNewId("id", "wl_keyboard")]),
            ("get_touch", [ArgNewId("id", "wl_touch")]),
            ("release", []),
        ],
        events=[
            ("capabilities", [ArgUInt("capabilities", "capability")]),
            ("name", [ArgStr("name")]),
        ],
        enums=[
            WEnum(
                name="capability",
                values={
                    "pointer": 1,
                    "keyboard": 2,
                    "touch": 4,
                },
                flag=True,
            ),
            WEnum(
                name="error",
                values={
                    "missing_capability": 0,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def get_pointer(self) -> WlPointer:
        _opcode = OpCode(0)
        id = self._connection.create_proxy(WlPointer)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_keyboard(self) -> WlKeyboard:
        _opcode = OpCode(1)
        id = self._connection.create_proxy(WlKeyboard)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_touch(self) -> WlTouch:
        _opcode = OpCode(2)
        id = self._connection.create_proxy(WlTouch)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def release(self) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_capabilities(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_name(self, handler: Callable[[str], bool]) -> Optional[Callable[[str], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Capability(Flag):
        POINTER = 1
        KEYBOARD = 2
        TOUCH = 4

    class Error(Enum):
        MISSING_CAPABILITY = 0

class WlPointer(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_pointer",
        requests=[
            ("set_cursor", [ArgUInt("serial"), ArgObject("surface", "wl_surface", True), ArgInt("hotspot_x"), ArgInt("hotspot_y")]),
            ("release", []),
        ],
        events=[
            ("enter", [ArgUInt("serial"), ArgObject("surface", "wl_surface"), ArgFixed("surface_x"), ArgFixed("surface_y")]),
            ("leave", [ArgUInt("serial"), ArgObject("surface", "wl_surface")]),
            ("motion", [ArgUInt("time"), ArgFixed("surface_x"), ArgFixed("surface_y")]),
            ("button", [ArgUInt("serial"), ArgUInt("time"), ArgUInt("button"), ArgUInt("state", "button_state")]),
            ("axis", [ArgUInt("time"), ArgUInt("axis", "axis"), ArgFixed("value")]),
            ("frame", []),
            ("axis_source", [ArgUInt("axis_source", "axis_source")]),
            ("axis_stop", [ArgUInt("time"), ArgUInt("axis", "axis")]),
            ("axis_discrete", [ArgUInt("axis", "axis"), ArgInt("discrete")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "role": 0,
                },
            ),
            WEnum(
                name="button_state",
                values={
                    "released": 0,
                    "pressed": 1,
                },
            ),
            WEnum(
                name="axis",
                values={
                    "vertical_scroll": 0,
                    "horizontal_scroll": 1,
                },
            ),
            WEnum(
                name="axis_source",
                values={
                    "wheel": 0,
                    "finger": 1,
                    "continuous": 2,
                    "wheel_tilt": 3,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def set_cursor(self, serial: int, surface: Optional[WlSurface], hotspot_x: int, hotspot_y: int) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, (serial, surface, hotspot_x, hotspot_y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def release(self) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_enter(self, handler: Callable[[int, WlSurface, float, float], bool]) -> Optional[Callable[[int, WlSurface, float, float], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[int, WlSurface], bool]) -> Optional[Callable[[int, WlSurface], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_motion(self, handler: Callable[[int, float, float], bool]) -> Optional[Callable[[int, float, float], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_button(self, handler: Callable[[int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int], bool]]:
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis(self, handler: Callable[[int, int, float], bool]) -> Optional[Callable[[int, int, float], bool]]:
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_frame(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis_source(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(6)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis_stop(self, handler: Callable[[int, int], bool]) -> Optional[Callable[[int, int], bool]]:
        _opcode = OpCode(7)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis_discrete(self, handler: Callable[[int, int], bool]) -> Optional[Callable[[int, int], bool]]:
        _opcode = OpCode(8)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        ROLE = 0

    class ButtonState(Enum):
        RELEASED = 0
        PRESSED = 1

    class Axis(Enum):
        VERTICAL_SCROLL = 0
        HORIZONTAL_SCROLL = 1

    class AxisSource(Enum):
        WHEEL = 0
        FINGER = 1
        CONTINUOUS = 2
        WHEEL_TILT = 3

class WlKeyboard(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_keyboard",
        requests=[
            ("release", []),
        ],
        events=[
            ("keymap", [ArgUInt("format", "keymap_format"), ArgFd("fd"), ArgUInt("size")]),
            ("enter", [ArgUInt("serial"), ArgObject("surface", "wl_surface"), ArgArray("keys")]),
            ("leave", [ArgUInt("serial"), ArgObject("surface", "wl_surface")]),
            ("key", [ArgUInt("serial"), ArgUInt("time"), ArgUInt("key"), ArgUInt("state", "key_state")]),
            ("modifiers", [ArgUInt("serial"), ArgUInt("mods_depressed"), ArgUInt("mods_latched"), ArgUInt("mods_locked"), ArgUInt("group")]),
            ("repeat_info", [ArgInt("rate"), ArgInt("delay")]),
        ],
        enums=[
            WEnum(
                name="keymap_format",
                values={
                    "no_keymap": 0,
                    "xkb_v1": 1,
                },
            ),
            WEnum(
                name="key_state",
                values={
                    "released": 0,
                    "pressed": 1,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def release(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_keymap(self, handler: Callable[[int, Fd, int], bool]) -> Optional[Callable[[int, Fd, int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_enter(self, handler: Callable[[int, WlSurface, bytes], bool]) -> Optional[Callable[[int, WlSurface, bytes], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[int, WlSurface], bool]) -> Optional[Callable[[int, WlSurface], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_key(self, handler: Callable[[int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int], bool]]:
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_modifiers(self, handler: Callable[[int, int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int, int], bool]]:
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_repeat_info(self, handler: Callable[[int, int], bool]) -> Optional[Callable[[int, int], bool]]:
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class KeymapFormat(Enum):
        NO_KEYMAP = 0
        XKB_V1 = 1

    class KeyState(Enum):
        RELEASED = 0
        PRESSED = 1

class WlTouch(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_touch",
        requests=[
            ("release", []),
        ],
        events=[
            ("down", [ArgUInt("serial"), ArgUInt("time"), ArgObject("surface", "wl_surface"), ArgInt("id"), ArgFixed("x"), ArgFixed("y")]),
            ("up", [ArgUInt("serial"), ArgUInt("time"), ArgInt("id")]),
            ("motion", [ArgUInt("time"), ArgInt("id"), ArgFixed("x"), ArgFixed("y")]),
            ("frame", []),
            ("cancel", []),
            ("shape", [ArgInt("id"), ArgFixed("major"), ArgFixed("minor")]),
            ("orientation", [ArgInt("id"), ArgFixed("orientation")]),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def release(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_down(self, handler: Callable[[int, int, WlSurface, int, float, float], bool]) -> Optional[Callable[[int, int, WlSurface, int, float, float], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_up(self, handler: Callable[[int, int, int], bool]) -> Optional[Callable[[int, int, int], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_motion(self, handler: Callable[[int, int, float, float], bool]) -> Optional[Callable[[int, int, float, float], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_frame(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_cancel(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_shape(self, handler: Callable[[int, float, float], bool]) -> Optional[Callable[[int, float, float], bool]]:
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_orientation(self, handler: Callable[[int, float], bool]) -> Optional[Callable[[int, float], bool]]:
        _opcode = OpCode(6)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlOutput(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_output",
        requests=[
            ("release", []),
        ],
        events=[
            ("geometry", [ArgInt("x"), ArgInt("y"), ArgInt("physical_width"), ArgInt("physical_height"), ArgInt("subpixel"), ArgStr("make"), ArgStr("model"), ArgInt("transform")]),
            ("mode", [ArgUInt("flags", "mode"), ArgInt("width"), ArgInt("height"), ArgInt("refresh")]),
            ("done", []),
            ("scale", [ArgInt("factor")]),
        ],
        enums=[
            WEnum(
                name="subpixel",
                values={
                    "unknown": 0,
                    "none": 1,
                    "horizontal_rgb": 2,
                    "horizontal_bgr": 3,
                    "vertical_rgb": 4,
                    "vertical_bgr": 5,
                },
            ),
            WEnum(
                name="transform",
                values={
                    "normal": 0,
                    "90": 1,
                    "180": 2,
                    "270": 3,
                    "flipped": 4,
                    "flipped_90": 5,
                    "flipped_180": 6,
                    "flipped_270": 7,
                },
            ),
            WEnum(
                name="mode",
                values={
                    "current": 1,
                    "preferred": 2,
                },
                flag=True,
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def release(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_geometry(self, handler: Callable[[int, int, int, int, int, str, str, int], bool]) -> Optional[Callable[[int, int, int, int, int, str, str, int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_mode(self, handler: Callable[[int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_done(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_scale(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Subpixel(Enum):
        UNKNOWN = 0
        NONE = 1
        HORIZONTAL_RGB = 2
        HORIZONTAL_BGR = 3
        VERTICAL_RGB = 4
        VERTICAL_BGR = 5

    class Transform(Enum):
        NORMAL = 0
        U90 = 1
        U180 = 2
        U270 = 3
        FLIPPED = 4
        FLIPPED_90 = 5
        FLIPPED_180 = 6
        FLIPPED_270 = 7

    class Mode(Flag):
        CURRENT = 1
        PREFERRED = 2

class WlRegion(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_region",
        requests=[
            ("destroy", []),
            ("add", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            ("subtract", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
        ],
        events=[
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def add(self, x: int, y: int, width: int, height: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def subtract(self, x: int, y: int, width: int, height: int) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlRegion:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

class WlSubcompositor(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_subcompositor",
        requests=[
            ("destroy", []),
            ("get_subsurface", [ArgNewId("id", "wl_subsurface"), ArgObject("surface", "wl_surface"), ArgObject("parent", "wl_surface")]),
        ],
        events=[
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "bad_surface": 0,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def get_subsurface(self, surface: WlSurface, parent: WlSurface) -> WlSubsurface:
        _opcode = OpCode(1)
        id = self._connection.create_proxy(WlSubsurface)
        _data, _fds = self._interface.pack(_opcode, (id, surface, parent,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def __enter__(self) -> WlSubcompositor:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    class Error(Enum):
        BAD_SURFACE = 0

class WlSubsurface(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="wl_subsurface",
        requests=[
            ("destroy", []),
            ("set_position", [ArgInt("x"), ArgInt("y")]),
            ("place_above", [ArgObject("sibling", "wl_surface")]),
            ("place_below", [ArgObject("sibling", "wl_surface")]),
            ("set_sync", []),
            ("set_desync", []),
        ],
        events=[
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "bad_surface": 0,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_position(self, x: int, y: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (x, y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def place_above(self, sibling: WlSurface) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (sibling,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def place_below(self, sibling: WlSurface) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (sibling,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_sync(self) -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_desync(self) -> None:
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> WlSubsurface:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    class Error(Enum):
        BAD_SURFACE = 0

# fmt: on