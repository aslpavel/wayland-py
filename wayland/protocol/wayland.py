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
    """core global object"""
    interface: ClassVar[Interface] = Interface(
        name="wl_display",
        requests=[
            WRequest("sync", [ArgNewId("callback", "wl_callback")]),
            WRequest("get_registry", [ArgNewId("registry", "wl_registry")]),
        ],
        events=[
            WEvent("error", [ArgObject("object_id", None), ArgUInt("code"), ArgStr("message")]),
            WEvent("delete_id", [ArgUInt("id")]),
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
        """asynchronous roundtrip"""
        callback = self._connection.create_proxy(WlCallback)
        self._call(OpCode(0), (callback,))
        return callback

    def get_registry(self) -> WlRegistry:
        """get global registry object"""
        registry = self._connection.create_proxy(WlRegistry)
        self._call(OpCode(1), (registry,))
        return registry

    def on_error(self, handler: Callable[[Proxy, int, str], bool]) -> Optional[Callable[[Proxy, int, str], bool]]:
        """fatal error event"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_delete_id(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """acknowledge object ID deletion"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_OBJECT = 0
        INVALID_METHOD = 1
        NO_MEMORY = 2
        IMPLEMENTATION = 3

def _unpack_enum_wl_display(name: str, value: int) -> Any:
    if name == "error":
        return WlDisplay.Error(value)
    return None
WlDisplay.interface.unpack_enum = _unpack_enum_wl_display

class WlRegistry(Proxy):
    """global registry object"""
    interface: ClassVar[Interface] = Interface(
        name="wl_registry",
        requests=[
            WRequest("bind", [ArgUInt("name"), ArgStr("id_interface"), ArgUInt("id_version"), ArgNewId("id", None)]),
        ],
        events=[
            WEvent("global", [ArgUInt("name"), ArgStr("interface"), ArgUInt("version")]),
            WEvent("global_remove", [ArgUInt("name")]),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def bind(self, name: int, id_interface: str, id_version: int, id: Proxy) -> None:
        """bind an object to the display"""
        _proxy_iface = id._interface.name
        if _proxy_iface != id_interface:
            raise TypeError("[{}(id)] expected {} (got {})"
                            .format(self, id_interface, _proxy_iface))
        self._call(OpCode(0), (name, id_interface, id_version, id,))
        return None

    def on_global(self, handler: Callable[[int, str, int], bool]) -> Optional[Callable[[int, str, int], bool]]:
        """announce global object"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_global_remove(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """announce removal of global object"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlCallback(Proxy):
    """callback object"""
    interface: ClassVar[Interface] = Interface(
        name="wl_callback",
        requests=[
        ],
        events=[
            WEvent("done", [ArgUInt("callback_data")]),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def on_done(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """done event"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlCompositor(Proxy):
    """the compositor singleton"""
    interface: ClassVar[Interface] = Interface(
        name="wl_compositor",
        requests=[
            WRequest("create_surface", [ArgNewId("id", "wl_surface")]),
            WRequest("create_region", [ArgNewId("id", "wl_region")]),
        ],
        events=[
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def create_surface(self) -> WlSurface:
        """create new surface"""
        id = self._connection.create_proxy(WlSurface)
        self._call(OpCode(0), (id,))
        return id

    def create_region(self) -> WlRegion:
        """create new region"""
        id = self._connection.create_proxy(WlRegion)
        self._call(OpCode(1), (id,))
        return id

class WlShmPool(Proxy):
    """a shared memory pool"""
    interface: ClassVar[Interface] = Interface(
        name="wl_shm_pool",
        requests=[
            WRequest("create_buffer", [ArgNewId("id", "wl_buffer"), ArgInt("offset"), ArgInt("width"), ArgInt("height"), ArgInt("stride"), ArgUInt("format", "wl_shm.format")]),
            WRequest("destroy", []),
            WRequest("resize", [ArgInt("size")]),
        ],
        events=[
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def create_buffer(self, offset: int, width: int, height: int, stride: int, format: WlShm.Format) -> WlBuffer:
        """create a buffer from the pool"""
        id = self._connection.create_proxy(WlBuffer)
        self._call(OpCode(0), (id, offset, width, height, stride, format,))
        return id

    def destroy(self) -> None:
        """destroy the pool"""
        self._call(OpCode(1), tuple())
        return None

    def resize(self, size: int) -> None:
        """change the size of the pool mapping"""
        self._call(OpCode(2), (size,))
        return None

    def __enter__(self) -> WlShmPool:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

class WlShm(Proxy):
    """shared memory support"""
    interface: ClassVar[Interface] = Interface(
        name="wl_shm",
        requests=[
            WRequest("create_pool", [ArgNewId("id", "wl_shm_pool"), ArgFd("fd"), ArgInt("size")]),
        ],
        events=[
            WEvent("format", [ArgUInt("format", "format")]),
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
        """create a shm pool"""
        id = self._connection.create_proxy(WlShmPool)
        self._call(OpCode(0), (id, fd, size,))
        return id

    def on_format(self, handler: Callable[[Format], bool]) -> Optional[Callable[[Format], bool]]:
        """pixel format description"""
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

def _unpack_enum_wl_shm(name: str, value: int) -> Any:
    if name == "error":
        return WlShm.Error(value)
    if name == "format":
        return WlShm.Format(value)
    return None
WlShm.interface.unpack_enum = _unpack_enum_wl_shm

class WlBuffer(Proxy):
    """content for a wl_surface"""
    interface: ClassVar[Interface] = Interface(
        name="wl_buffer",
        requests=[
            WRequest("destroy", []),
        ],
        events=[
            WEvent("release", []),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy a buffer"""
        self._call(OpCode(0), tuple())
        return None

    def __enter__(self) -> WlBuffer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_release(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """compositor releases buffer"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlDataOffer(Proxy):
    """offer to transfer data"""
    interface: ClassVar[Interface] = Interface(
        name="wl_data_offer",
        requests=[
            WRequest("accept", [ArgUInt("serial"), ArgStr("mime_type")]),
            WRequest("receive", [ArgStr("mime_type"), ArgFd("fd")]),
            WRequest("destroy", []),
            WRequest("finish", []),
            WRequest("set_actions", [ArgUInt("dnd_actions", "wl_data_device_manager.dnd_action"), ArgUInt("preferred_action", "wl_data_device_manager.dnd_action")]),
        ],
        events=[
            WEvent("offer", [ArgStr("mime_type")]),
            WEvent("source_actions", [ArgUInt("source_actions", "wl_data_device_manager.dnd_action")]),
            WEvent("action", [ArgUInt("dnd_action", "wl_data_device_manager.dnd_action")]),
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
        """accept one of the offered mime types"""
        self._call(OpCode(0), (serial, mime_type,))
        return None

    def receive(self, mime_type: str, fd: Fd) -> None:
        """request that the data is transferred"""
        self._call(OpCode(1), (mime_type, fd,))
        return None

    def destroy(self) -> None:
        """destroy data offer"""
        self._call(OpCode(2), tuple())
        return None

    def finish(self) -> None:
        """the offer will no longer be used"""
        self._call(OpCode(3), tuple())
        return None

    def set_actions(self, dnd_actions: WlDataDeviceManager.DndAction, preferred_action: WlDataDeviceManager.DndAction) -> None:
        """set the available/preferred drag-and-drop actions"""
        self._call(OpCode(4), (dnd_actions, preferred_action,))
        return None

    def __enter__(self) -> WlDataOffer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_offer(self, handler: Callable[[str], bool]) -> Optional[Callable[[str], bool]]:
        """advertise offered mime type"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_source_actions(self, handler: Callable[[WlDataDeviceManager.DndAction], bool]) -> Optional[Callable[[WlDataDeviceManager.DndAction], bool]]:
        """notify the source-side available actions"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_action(self, handler: Callable[[WlDataDeviceManager.DndAction], bool]) -> Optional[Callable[[WlDataDeviceManager.DndAction], bool]]:
        """notify the selected action"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_FINISH = 0
        INVALID_ACTION_MASK = 1
        INVALID_ACTION = 2
        INVALID_OFFER = 3

def _unpack_enum_wl_data_offer(name: str, value: int) -> Any:
    if name == "error":
        return WlDataOffer.Error(value)
    return None
WlDataOffer.interface.unpack_enum = _unpack_enum_wl_data_offer

class WlDataSource(Proxy):
    """offer to transfer data"""
    interface: ClassVar[Interface] = Interface(
        name="wl_data_source",
        requests=[
            WRequest("offer", [ArgStr("mime_type")]),
            WRequest("destroy", []),
            WRequest("set_actions", [ArgUInt("dnd_actions", "wl_data_device_manager.dnd_action")]),
        ],
        events=[
            WEvent("target", [ArgStr("mime_type")]),
            WEvent("send", [ArgStr("mime_type"), ArgFd("fd")]),
            WEvent("cancelled", []),
            WEvent("dnd_drop_performed", []),
            WEvent("dnd_finished", []),
            WEvent("action", [ArgUInt("dnd_action", "wl_data_device_manager.dnd_action")]),
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
        """add an offered mime type"""
        self._call(OpCode(0), (mime_type,))
        return None

    def destroy(self) -> None:
        """destroy the data source"""
        self._call(OpCode(1), tuple())
        return None

    def set_actions(self, dnd_actions: WlDataDeviceManager.DndAction) -> None:
        """set the available drag-and-drop actions"""
        self._call(OpCode(2), (dnd_actions,))
        return None

    def __enter__(self) -> WlDataSource:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_target(self, handler: Callable[[str], bool]) -> Optional[Callable[[str], bool]]:
        """a target accepts an offered mime type"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_send(self, handler: Callable[[str, Fd], bool]) -> Optional[Callable[[str, Fd], bool]]:
        """send the data"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_cancelled(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """selection was cancelled"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_dnd_drop_performed(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """the drag-and-drop operation physically finished"""
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_dnd_finished(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """the drag-and-drop operation concluded"""
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_action(self, handler: Callable[[WlDataDeviceManager.DndAction], bool]) -> Optional[Callable[[WlDataDeviceManager.DndAction], bool]]:
        """notify the selected action"""
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_ACTION_MASK = 0
        INVALID_SOURCE = 1

def _unpack_enum_wl_data_source(name: str, value: int) -> Any:
    if name == "error":
        return WlDataSource.Error(value)
    return None
WlDataSource.interface.unpack_enum = _unpack_enum_wl_data_source

class WlDataDevice(Proxy):
    """data transfer device"""
    interface: ClassVar[Interface] = Interface(
        name="wl_data_device",
        requests=[
            WRequest("start_drag", [ArgObject("source", "wl_data_source", True), ArgObject("origin", "wl_surface"), ArgObject("icon", "wl_surface", True), ArgUInt("serial")]),
            WRequest("set_selection", [ArgObject("source", "wl_data_source", True), ArgUInt("serial")]),
            WRequest("release", []),
        ],
        events=[
            WEvent("data_offer", [ArgNewId("id", "wl_data_offer")]),
            WEvent("enter", [ArgUInt("serial"), ArgObject("surface", "wl_surface"), ArgFixed("x"), ArgFixed("y"), ArgObject("id", "wl_data_offer", True)]),
            WEvent("leave", []),
            WEvent("motion", [ArgUInt("time"), ArgFixed("x"), ArgFixed("y")]),
            WEvent("drop", []),
            WEvent("selection", [ArgObject("id", "wl_data_offer", True)]),
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
        """start drag-and-drop operation"""
        self._call(OpCode(0), (source, origin, icon, serial,))
        return None

    def set_selection(self, source: Optional[WlDataSource], serial: int) -> None:
        """copy data to the selection"""
        self._call(OpCode(1), (source, serial,))
        return None

    def release(self) -> None:
        """destroy data device"""
        self._call(OpCode(2), tuple())
        return None

    def __enter__(self) -> WlDataDevice:
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()

    def on_data_offer(self, handler: Callable[[WlDataOffer], bool]) -> Optional[Callable[[WlDataOffer], bool]]:
        """introduce a new wl_data_offer"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_enter(self, handler: Callable[[int, WlSurface, float, float, Optional[WlDataOffer]], bool]) -> Optional[Callable[[int, WlSurface, float, float, Optional[WlDataOffer]], bool]]:
        """initiate drag-and-drop session"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """end drag-and-drop session"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_motion(self, handler: Callable[[int, float, float], bool]) -> Optional[Callable[[int, float, float], bool]]:
        """drag-and-drop session motion"""
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_drop(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """end drag-and-drop session successfully"""
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_selection(self, handler: Callable[[Optional[WlDataOffer]], bool]) -> Optional[Callable[[Optional[WlDataOffer]], bool]]:
        """advertise new selection"""
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        ROLE = 0

def _unpack_enum_wl_data_device(name: str, value: int) -> Any:
    if name == "error":
        return WlDataDevice.Error(value)
    return None
WlDataDevice.interface.unpack_enum = _unpack_enum_wl_data_device

class WlDataDeviceManager(Proxy):
    """data transfer interface"""
    interface: ClassVar[Interface] = Interface(
        name="wl_data_device_manager",
        requests=[
            WRequest("create_data_source", [ArgNewId("id", "wl_data_source")]),
            WRequest("get_data_device", [ArgNewId("id", "wl_data_device"), ArgObject("seat", "wl_seat")]),
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
        """create a new data source"""
        id = self._connection.create_proxy(WlDataSource)
        self._call(OpCode(0), (id,))
        return id

    def get_data_device(self, seat: WlSeat) -> WlDataDevice:
        """create a new data device"""
        id = self._connection.create_proxy(WlDataDevice)
        self._call(OpCode(1), (id, seat,))
        return id

    class DndAction(Flag):
        NONE = 0
        COPY = 1
        MOVE = 2
        ASK = 4

def _unpack_enum_wl_data_device_manager(name: str, value: int) -> Any:
    if name == "dnd_action":
        return WlDataDeviceManager.DndAction(value)
    return None
WlDataDeviceManager.interface.unpack_enum = _unpack_enum_wl_data_device_manager

class WlShell(Proxy):
    """create desktop-style surfaces"""
    interface: ClassVar[Interface] = Interface(
        name="wl_shell",
        requests=[
            WRequest("get_shell_surface", [ArgNewId("id", "wl_shell_surface"), ArgObject("surface", "wl_surface")]),
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
        """create a shell surface from a surface"""
        id = self._connection.create_proxy(WlShellSurface)
        self._call(OpCode(0), (id, surface,))
        return id

    class Error(Enum):
        ROLE = 0

def _unpack_enum_wl_shell(name: str, value: int) -> Any:
    if name == "error":
        return WlShell.Error(value)
    return None
WlShell.interface.unpack_enum = _unpack_enum_wl_shell

class WlShellSurface(Proxy):
    """desktop-style metadata interface"""
    interface: ClassVar[Interface] = Interface(
        name="wl_shell_surface",
        requests=[
            WRequest("pong", [ArgUInt("serial")]),
            WRequest("move", [ArgObject("seat", "wl_seat"), ArgUInt("serial")]),
            WRequest("resize", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgUInt("edges", "resize")]),
            WRequest("set_toplevel", []),
            WRequest("set_transient", [ArgObject("parent", "wl_surface"), ArgInt("x"), ArgInt("y"), ArgUInt("flags", "transient")]),
            WRequest("set_fullscreen", [ArgUInt("method", "fullscreen_method"), ArgUInt("framerate"), ArgObject("output", "wl_output", True)]),
            WRequest("set_popup", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgObject("parent", "wl_surface"), ArgInt("x"), ArgInt("y"), ArgUInt("flags", "transient")]),
            WRequest("set_maximized", [ArgObject("output", "wl_output", True)]),
            WRequest("set_title", [ArgStr("title")]),
            WRequest("set_class", [ArgStr("class_")]),
        ],
        events=[
            WEvent("ping", [ArgUInt("serial")]),
            WEvent("configure", [ArgUInt("edges", "resize"), ArgInt("width"), ArgInt("height")]),
            WEvent("popup_done", []),
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
        """respond to a ping event"""
        self._call(OpCode(0), (serial,))
        return None

    def move(self, seat: WlSeat, serial: int) -> None:
        """start an interactive move"""
        self._call(OpCode(1), (seat, serial,))
        return None

    def resize(self, seat: WlSeat, serial: int, edges: Resize) -> None:
        """start an interactive resize"""
        self._call(OpCode(2), (seat, serial, edges,))
        return None

    def set_toplevel(self) -> None:
        """make the surface a toplevel surface"""
        self._call(OpCode(3), tuple())
        return None

    def set_transient(self, parent: WlSurface, x: int, y: int, flags: Transient) -> None:
        """make the surface a transient surface"""
        self._call(OpCode(4), (parent, x, y, flags,))
        return None

    def set_fullscreen(self, method: FullscreenMethod, framerate: int, output: Optional[WlOutput]) -> None:
        """make the surface a fullscreen surface"""
        self._call(OpCode(5), (method, framerate, output,))
        return None

    def set_popup(self, seat: WlSeat, serial: int, parent: WlSurface, x: int, y: int, flags: Transient) -> None:
        """make the surface a popup surface"""
        self._call(OpCode(6), (seat, serial, parent, x, y, flags,))
        return None

    def set_maximized(self, output: Optional[WlOutput]) -> None:
        """make the surface a maximized surface"""
        self._call(OpCode(7), (output,))
        return None

    def set_title(self, title: str) -> None:
        """set surface title"""
        self._call(OpCode(8), (title,))
        return None

    def set_class(self, class_: str) -> None:
        """set surface class"""
        self._call(OpCode(9), (class_,))
        return None

    def on_ping(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """ping client"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_configure(self, handler: Callable[[Resize, int, int], bool]) -> Optional[Callable[[Resize, int, int], bool]]:
        """suggest resize"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_popup_done(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """popup interaction is done"""
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

def _unpack_enum_wl_shell_surface(name: str, value: int) -> Any:
    if name == "resize":
        return WlShellSurface.Resize(value)
    if name == "transient":
        return WlShellSurface.Transient(value)
    if name == "fullscreen_method":
        return WlShellSurface.FullscreenMethod(value)
    return None
WlShellSurface.interface.unpack_enum = _unpack_enum_wl_shell_surface

class WlSurface(Proxy):
    """an onscreen surface"""
    interface: ClassVar[Interface] = Interface(
        name="wl_surface",
        requests=[
            WRequest("destroy", []),
            WRequest("attach", [ArgObject("buffer", "wl_buffer", True), ArgInt("x"), ArgInt("y")]),
            WRequest("damage", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            WRequest("frame", [ArgNewId("callback", "wl_callback")]),
            WRequest("set_opaque_region", [ArgObject("region", "wl_region", True)]),
            WRequest("set_input_region", [ArgObject("region", "wl_region", True)]),
            WRequest("commit", []),
            WRequest("set_buffer_transform", [ArgInt("transform")]),
            WRequest("set_buffer_scale", [ArgInt("scale")]),
            WRequest("damage_buffer", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
        ],
        events=[
            WEvent("enter", [ArgObject("output", "wl_output")]),
            WEvent("leave", [ArgObject("output", "wl_output")]),
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
        """delete surface"""
        self._call(OpCode(0), tuple())
        return None

    def attach(self, buffer: Optional[WlBuffer], x: int, y: int) -> None:
        """set the surface contents"""
        self._call(OpCode(1), (buffer, x, y,))
        return None

    def damage(self, x: int, y: int, width: int, height: int) -> None:
        """mark part of the surface damaged"""
        self._call(OpCode(2), (x, y, width, height,))
        return None

    def frame(self) -> WlCallback:
        """request a frame throttling hint"""
        callback = self._connection.create_proxy(WlCallback)
        self._call(OpCode(3), (callback,))
        return callback

    def set_opaque_region(self, region: Optional[WlRegion]) -> None:
        """set opaque region"""
        self._call(OpCode(4), (region,))
        return None

    def set_input_region(self, region: Optional[WlRegion]) -> None:
        """set input region"""
        self._call(OpCode(5), (region,))
        return None

    def commit(self) -> None:
        """commit pending surface state"""
        self._call(OpCode(6), tuple())
        return None

    def set_buffer_transform(self, transform: int) -> None:
        """sets the buffer transformation"""
        self._call(OpCode(7), (transform,))
        return None

    def set_buffer_scale(self, scale: int) -> None:
        """sets the buffer scaling factor"""
        self._call(OpCode(8), (scale,))
        return None

    def damage_buffer(self, x: int, y: int, width: int, height: int) -> None:
        """mark part of the surface damaged using buffer coordinates"""
        self._call(OpCode(9), (x, y, width, height,))
        return None

    def __enter__(self) -> WlSurface:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_enter(self, handler: Callable[[WlOutput], bool]) -> Optional[Callable[[WlOutput], bool]]:
        """surface enters an output"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[WlOutput], bool]) -> Optional[Callable[[WlOutput], bool]]:
        """surface leaves an output"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_SCALE = 0
        INVALID_TRANSFORM = 1
        INVALID_SIZE = 2

def _unpack_enum_wl_surface(name: str, value: int) -> Any:
    if name == "error":
        return WlSurface.Error(value)
    return None
WlSurface.interface.unpack_enum = _unpack_enum_wl_surface

class WlSeat(Proxy):
    """group of input devices"""
    interface: ClassVar[Interface] = Interface(
        name="wl_seat",
        requests=[
            WRequest("get_pointer", [ArgNewId("id", "wl_pointer")]),
            WRequest("get_keyboard", [ArgNewId("id", "wl_keyboard")]),
            WRequest("get_touch", [ArgNewId("id", "wl_touch")]),
            WRequest("release", []),
        ],
        events=[
            WEvent("capabilities", [ArgUInt("capabilities", "capability")]),
            WEvent("name", [ArgStr("name")]),
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
        """return pointer object"""
        id = self._connection.create_proxy(WlPointer)
        self._call(OpCode(0), (id,))
        return id

    def get_keyboard(self) -> WlKeyboard:
        """return keyboard object"""
        id = self._connection.create_proxy(WlKeyboard)
        self._call(OpCode(1), (id,))
        return id

    def get_touch(self) -> WlTouch:
        """return touch object"""
        id = self._connection.create_proxy(WlTouch)
        self._call(OpCode(2), (id,))
        return id

    def release(self) -> None:
        """release the seat object"""
        self._call(OpCode(3), tuple())
        return None

    def __enter__(self) -> WlSeat:
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()

    def on_capabilities(self, handler: Callable[[Capability], bool]) -> Optional[Callable[[Capability], bool]]:
        """seat capabilities changed"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_name(self, handler: Callable[[str], bool]) -> Optional[Callable[[str], bool]]:
        """unique identifier for this seat"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Capability(Flag):
        POINTER = 1
        KEYBOARD = 2
        TOUCH = 4

    class Error(Enum):
        MISSING_CAPABILITY = 0

def _unpack_enum_wl_seat(name: str, value: int) -> Any:
    if name == "capability":
        return WlSeat.Capability(value)
    if name == "error":
        return WlSeat.Error(value)
    return None
WlSeat.interface.unpack_enum = _unpack_enum_wl_seat

class WlPointer(Proxy):
    """pointer input device"""
    interface: ClassVar[Interface] = Interface(
        name="wl_pointer",
        requests=[
            WRequest("set_cursor", [ArgUInt("serial"), ArgObject("surface", "wl_surface", True), ArgInt("hotspot_x"), ArgInt("hotspot_y")]),
            WRequest("release", []),
        ],
        events=[
            WEvent("enter", [ArgUInt("serial"), ArgObject("surface", "wl_surface"), ArgFixed("surface_x"), ArgFixed("surface_y")]),
            WEvent("leave", [ArgUInt("serial"), ArgObject("surface", "wl_surface")]),
            WEvent("motion", [ArgUInt("time"), ArgFixed("surface_x"), ArgFixed("surface_y")]),
            WEvent("button", [ArgUInt("serial"), ArgUInt("time"), ArgUInt("button"), ArgUInt("state", "button_state")]),
            WEvent("axis", [ArgUInt("time"), ArgUInt("axis", "axis"), ArgFixed("value")]),
            WEvent("frame", []),
            WEvent("axis_source", [ArgUInt("axis_source", "axis_source")]),
            WEvent("axis_stop", [ArgUInt("time"), ArgUInt("axis", "axis")]),
            WEvent("axis_discrete", [ArgUInt("axis", "axis"), ArgInt("discrete")]),
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
        """set the pointer surface"""
        self._call(OpCode(0), (serial, surface, hotspot_x, hotspot_y,))
        return None

    def release(self) -> None:
        """release the pointer object"""
        self._call(OpCode(1), tuple())
        return None

    def __enter__(self) -> WlPointer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()

    def on_enter(self, handler: Callable[[int, WlSurface, float, float], bool]) -> Optional[Callable[[int, WlSurface, float, float], bool]]:
        """enter event"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[int, WlSurface], bool]) -> Optional[Callable[[int, WlSurface], bool]]:
        """leave event"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_motion(self, handler: Callable[[int, float, float], bool]) -> Optional[Callable[[int, float, float], bool]]:
        """pointer motion event"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_button(self, handler: Callable[[int, int, int, ButtonState], bool]) -> Optional[Callable[[int, int, int, ButtonState], bool]]:
        """pointer button event"""
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis(self, handler: Callable[[int, Axis, float], bool]) -> Optional[Callable[[int, Axis, float], bool]]:
        """axis event"""
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_frame(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """end of a pointer event sequence"""
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis_source(self, handler: Callable[[AxisSource], bool]) -> Optional[Callable[[AxisSource], bool]]:
        """axis source event"""
        _opcode = OpCode(6)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis_stop(self, handler: Callable[[int, Axis], bool]) -> Optional[Callable[[int, Axis], bool]]:
        """axis stop event"""
        _opcode = OpCode(7)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_axis_discrete(self, handler: Callable[[Axis, int], bool]) -> Optional[Callable[[Axis, int], bool]]:
        """axis click event"""
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

def _unpack_enum_wl_pointer(name: str, value: int) -> Any:
    if name == "error":
        return WlPointer.Error(value)
    if name == "button_state":
        return WlPointer.ButtonState(value)
    if name == "axis":
        return WlPointer.Axis(value)
    if name == "axis_source":
        return WlPointer.AxisSource(value)
    return None
WlPointer.interface.unpack_enum = _unpack_enum_wl_pointer

class WlKeyboard(Proxy):
    """keyboard input device"""
    interface: ClassVar[Interface] = Interface(
        name="wl_keyboard",
        requests=[
            WRequest("release", []),
        ],
        events=[
            WEvent("keymap", [ArgUInt("format", "keymap_format"), ArgFd("fd"), ArgUInt("size")]),
            WEvent("enter", [ArgUInt("serial"), ArgObject("surface", "wl_surface"), ArgArray("keys")]),
            WEvent("leave", [ArgUInt("serial"), ArgObject("surface", "wl_surface")]),
            WEvent("key", [ArgUInt("serial"), ArgUInt("time"), ArgUInt("key"), ArgUInt("state", "key_state")]),
            WEvent("modifiers", [ArgUInt("serial"), ArgUInt("mods_depressed"), ArgUInt("mods_latched"), ArgUInt("mods_locked"), ArgUInt("group")]),
            WEvent("repeat_info", [ArgInt("rate"), ArgInt("delay")]),
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
        """release the keyboard object"""
        self._call(OpCode(0), tuple())
        return None

    def __enter__(self) -> WlKeyboard:
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()

    def on_keymap(self, handler: Callable[[KeymapFormat, Fd, int], bool]) -> Optional[Callable[[KeymapFormat, Fd, int], bool]]:
        """keyboard mapping"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_enter(self, handler: Callable[[int, WlSurface, bytes], bool]) -> Optional[Callable[[int, WlSurface, bytes], bool]]:
        """enter event"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_leave(self, handler: Callable[[int, WlSurface], bool]) -> Optional[Callable[[int, WlSurface], bool]]:
        """leave event"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_key(self, handler: Callable[[int, int, int, KeyState], bool]) -> Optional[Callable[[int, int, int, KeyState], bool]]:
        """key event"""
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_modifiers(self, handler: Callable[[int, int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int, int], bool]]:
        """modifier and group state"""
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_repeat_info(self, handler: Callable[[int, int], bool]) -> Optional[Callable[[int, int], bool]]:
        """repeat rate and delay"""
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class KeymapFormat(Enum):
        NO_KEYMAP = 0
        XKB_V1 = 1

    class KeyState(Enum):
        RELEASED = 0
        PRESSED = 1

def _unpack_enum_wl_keyboard(name: str, value: int) -> Any:
    if name == "keymap_format":
        return WlKeyboard.KeymapFormat(value)
    if name == "key_state":
        return WlKeyboard.KeyState(value)
    return None
WlKeyboard.interface.unpack_enum = _unpack_enum_wl_keyboard

class WlTouch(Proxy):
    """touchscreen input device"""
    interface: ClassVar[Interface] = Interface(
        name="wl_touch",
        requests=[
            WRequest("release", []),
        ],
        events=[
            WEvent("down", [ArgUInt("serial"), ArgUInt("time"), ArgObject("surface", "wl_surface"), ArgInt("id"), ArgFixed("x"), ArgFixed("y")]),
            WEvent("up", [ArgUInt("serial"), ArgUInt("time"), ArgInt("id")]),
            WEvent("motion", [ArgUInt("time"), ArgInt("id"), ArgFixed("x"), ArgFixed("y")]),
            WEvent("frame", []),
            WEvent("cancel", []),
            WEvent("shape", [ArgInt("id"), ArgFixed("major"), ArgFixed("minor")]),
            WEvent("orientation", [ArgInt("id"), ArgFixed("orientation")]),
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def release(self) -> None:
        """release the touch object"""
        self._call(OpCode(0), tuple())
        return None

    def __enter__(self) -> WlTouch:
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()

    def on_down(self, handler: Callable[[int, int, WlSurface, int, float, float], bool]) -> Optional[Callable[[int, int, WlSurface, int, float, float], bool]]:
        """touch down event and beginning of a touch sequence"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_up(self, handler: Callable[[int, int, int], bool]) -> Optional[Callable[[int, int, int], bool]]:
        """end of a touch event sequence"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_motion(self, handler: Callable[[int, int, float, float], bool]) -> Optional[Callable[[int, int, float, float], bool]]:
        """update of touch point coordinates"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_frame(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """end of touch frame event"""
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_cancel(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """touch session cancelled"""
        _opcode = OpCode(4)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_shape(self, handler: Callable[[int, float, float], bool]) -> Optional[Callable[[int, float, float], bool]]:
        """update shape of touch point"""
        _opcode = OpCode(5)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_orientation(self, handler: Callable[[int, float], bool]) -> Optional[Callable[[int, float], bool]]:
        """update orientation of touch point"""
        _opcode = OpCode(6)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

class WlOutput(Proxy):
    """compositor output region"""
    interface: ClassVar[Interface] = Interface(
        name="wl_output",
        requests=[
            WRequest("release", []),
        ],
        events=[
            WEvent("geometry", [ArgInt("x"), ArgInt("y"), ArgInt("physical_width"), ArgInt("physical_height"), ArgInt("subpixel"), ArgStr("make"), ArgStr("model"), ArgInt("transform")]),
            WEvent("mode", [ArgUInt("flags", "mode"), ArgInt("width"), ArgInt("height"), ArgInt("refresh")]),
            WEvent("done", []),
            WEvent("scale", [ArgInt("factor")]),
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
        """release the output object"""
        self._call(OpCode(0), tuple())
        return None

    def __enter__(self) -> WlOutput:
        return self

    def __exit__(self, *_: Any) -> None:
        self.release()

    def on_geometry(self, handler: Callable[[int, int, int, int, int, str, str, int], bool]) -> Optional[Callable[[int, int, int, int, int, str, str, int], bool]]:
        """properties of the output"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_mode(self, handler: Callable[[Mode, int, int, int], bool]) -> Optional[Callable[[Mode, int, int, int], bool]]:
        """advertise available modes for the output"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_done(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """sent all information about output"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_scale(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """output scaling properties"""
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

def _unpack_enum_wl_output(name: str, value: int) -> Any:
    if name == "subpixel":
        return WlOutput.Subpixel(value)
    if name == "transform":
        return WlOutput.Transform(value)
    if name == "mode":
        return WlOutput.Mode(value)
    return None
WlOutput.interface.unpack_enum = _unpack_enum_wl_output

class WlRegion(Proxy):
    """region interface"""
    interface: ClassVar[Interface] = Interface(
        name="wl_region",
        requests=[
            WRequest("destroy", []),
            WRequest("add", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            WRequest("subtract", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
        ],
        events=[
        ],
        enums=[
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy region"""
        self._call(OpCode(0), tuple())
        return None

    def add(self, x: int, y: int, width: int, height: int) -> None:
        """add rectangle to region"""
        self._call(OpCode(1), (x, y, width, height,))
        return None

    def subtract(self, x: int, y: int, width: int, height: int) -> None:
        """subtract rectangle from region"""
        self._call(OpCode(2), (x, y, width, height,))
        return None

    def __enter__(self) -> WlRegion:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

class WlSubcompositor(Proxy):
    """sub-surface compositing"""
    interface: ClassVar[Interface] = Interface(
        name="wl_subcompositor",
        requests=[
            WRequest("destroy", []),
            WRequest("get_subsurface", [ArgNewId("id", "wl_subsurface"), ArgObject("surface", "wl_surface"), ArgObject("parent", "wl_surface")]),
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
        """unbind from the subcompositor interface"""
        self._call(OpCode(0), tuple())
        return None

    def get_subsurface(self, surface: WlSurface, parent: WlSurface) -> WlSubsurface:
        """give a surface the role sub-surface"""
        id = self._connection.create_proxy(WlSubsurface)
        self._call(OpCode(1), (id, surface, parent,))
        return id

    def __enter__(self) -> WlSubcompositor:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    class Error(Enum):
        BAD_SURFACE = 0

def _unpack_enum_wl_subcompositor(name: str, value: int) -> Any:
    if name == "error":
        return WlSubcompositor.Error(value)
    return None
WlSubcompositor.interface.unpack_enum = _unpack_enum_wl_subcompositor

class WlSubsurface(Proxy):
    """sub-surface interface to a wl_surface"""
    interface: ClassVar[Interface] = Interface(
        name="wl_subsurface",
        requests=[
            WRequest("destroy", []),
            WRequest("set_position", [ArgInt("x"), ArgInt("y")]),
            WRequest("place_above", [ArgObject("sibling", "wl_surface")]),
            WRequest("place_below", [ArgObject("sibling", "wl_surface")]),
            WRequest("set_sync", []),
            WRequest("set_desync", []),
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
        """remove sub-surface interface"""
        self._call(OpCode(0), tuple())
        return None

    def set_position(self, x: int, y: int) -> None:
        """reposition the sub-surface"""
        self._call(OpCode(1), (x, y,))
        return None

    def place_above(self, sibling: WlSurface) -> None:
        """restack the sub-surface"""
        self._call(OpCode(2), (sibling,))
        return None

    def place_below(self, sibling: WlSurface) -> None:
        """restack the sub-surface"""
        self._call(OpCode(3), (sibling,))
        return None

    def set_sync(self) -> None:
        """set sub-surface to synchronized mode"""
        self._call(OpCode(4), tuple())
        return None

    def set_desync(self) -> None:
        """set sub-surface to desynchronized mode"""
        self._call(OpCode(5), tuple())
        return None

    def __enter__(self) -> WlSubsurface:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    class Error(Enum):
        BAD_SURFACE = 0

def _unpack_enum_wl_subsurface(name: str, value: int) -> Any:
    if name == "error":
        return WlSubsurface.Error(value)
    return None
WlSubsurface.interface.unpack_enum = _unpack_enum_wl_subsurface

# fmt: on