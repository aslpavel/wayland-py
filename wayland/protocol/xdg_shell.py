# Auto generated do not edit manually
# fmt: off
# pyright: reportPrivateUsage=false,reportUnusedImport=false
from __future__ import annotations
from enum import Enum, Flag
import typing
from typing import Any, ClassVar
from collections.abc import Callable
from ..base import *
from .wayland import *

__all__ = [
    "XdgWmBase",
    "XdgPositioner",
    "XdgSurface",
    "XdgToplevel",
    "XdgPopup",
]

class XdgWmBase(Proxy):
    """create desktop-style surfaces"""
    interface: ClassVar[Interface] = Interface(
        name="xdg_wm_base",
        version=6,
        requests=[
            WRequest("destroy", []),
            WRequest("create_positioner", [ArgNewId("id", "xdg_positioner")]),
            WRequest("get_xdg_surface", [ArgNewId("id", "xdg_surface"), ArgObject("surface", "wl_surface")]),
            WRequest("pong", [ArgUInt("serial")]),
        ],
        events=[
            WEvent("ping", [ArgUInt("serial")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "role": 0,
                    "defunct_surfaces": 1,
                    "not_the_topmost_popup": 2,
                    "invalid_popup_parent": 3,
                    "invalid_surface_state": 4,
                    "invalid_positioner": 5,
                    "unresponsive": 6,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy xdg_wm_base"""
        self._call(OpCode(0), tuple())
        return None

    def create_positioner(self) -> XdgPositioner:
        """create a positioner object"""
        id = self._connection.create_proxy(XdgPositioner)
        self._call(OpCode(1), (id,))
        return id

    def get_xdg_surface(self, surface: WlSurface) -> XdgSurface:
        """create a shell surface from a surface"""
        id = self._connection.create_proxy(XdgSurface)
        self._call(OpCode(2), (id, surface,))
        return id

    def pong(self, serial: int) -> None:
        """respond to a ping event"""
        self._call(OpCode(3), (serial,))
        return None

    def __enter__(self) -> XdgWmBase:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_ping(self, handler: Callable[[int], bool]) -> Callable[[int], bool] | None:
        """check if the client is alive"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        ROLE = 0
        DEFUNCT_SURFACES = 1
        NOT_THE_TOPMOST_POPUP = 2
        INVALID_POPUP_PARENT = 3
        INVALID_SURFACE_STATE = 4
        INVALID_POSITIONER = 5
        UNRESPONSIVE = 6

def _unpack_enum_xdg_wm_base(name: str, value: int) -> Any:
    if name == "error":
        return XdgWmBase.Error(value)
    return None
XdgWmBase.interface.unpack_enum = _unpack_enum_xdg_wm_base

PROXIES["xdg_wm_base"] = XdgWmBase

class XdgPositioner(Proxy):
    """child surface positioner"""
    interface: ClassVar[Interface] = Interface(
        name="xdg_positioner",
        version=6,
        requests=[
            WRequest("destroy", []),
            WRequest("set_size", [ArgInt("width"), ArgInt("height")]),
            WRequest("set_anchor_rect", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            WRequest("set_anchor", [ArgUInt("anchor", "anchor")]),
            WRequest("set_gravity", [ArgUInt("gravity", "gravity")]),
            WRequest("set_constraint_adjustment", [ArgUInt("constraint_adjustment", "constraint_adjustment")]),
            WRequest("set_offset", [ArgInt("x"), ArgInt("y")]),
            WRequest("set_reactive", []),
            WRequest("set_parent_size", [ArgInt("parent_width"), ArgInt("parent_height")]),
            WRequest("set_parent_configure", [ArgUInt("serial")]),
        ],
        events=[
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_input": 0,
                },
            ),
            WEnum(
                name="anchor",
                values={
                    "none": 0,
                    "top": 1,
                    "bottom": 2,
                    "left": 3,
                    "right": 4,
                    "top_left": 5,
                    "bottom_left": 6,
                    "top_right": 7,
                    "bottom_right": 8,
                },
            ),
            WEnum(
                name="gravity",
                values={
                    "none": 0,
                    "top": 1,
                    "bottom": 2,
                    "left": 3,
                    "right": 4,
                    "top_left": 5,
                    "bottom_left": 6,
                    "top_right": 7,
                    "bottom_right": 8,
                },
            ),
            WEnum(
                name="constraint_adjustment",
                values={
                    "none": 0,
                    "slide_x": 1,
                    "slide_y": 2,
                    "flip_x": 4,
                    "flip_y": 8,
                    "resize_x": 16,
                    "resize_y": 32,
                },
                flag=True,
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy the xdg_positioner object"""
        self._call(OpCode(0), tuple())
        return None

    def set_size(self, width: int, height: int) -> None:
        """set the size of the to-be positioned rectangle"""
        self._call(OpCode(1), (width, height,))
        return None

    def set_anchor_rect(self, x: int, y: int, width: int, height: int) -> None:
        """set the anchor rectangle within the parent surface"""
        self._call(OpCode(2), (x, y, width, height,))
        return None

    def set_anchor(self, anchor: Anchor) -> None:
        """set anchor rectangle anchor"""
        self._call(OpCode(3), (anchor,))
        return None

    def set_gravity(self, gravity: Gravity) -> None:
        """set child surface gravity"""
        self._call(OpCode(4), (gravity,))
        return None

    def set_constraint_adjustment(self, constraint_adjustment: ConstraintAdjustment) -> None:
        """set the adjustment to be done when constrained"""
        self._call(OpCode(5), (constraint_adjustment,))
        return None

    def set_offset(self, x: int, y: int) -> None:
        """set surface position offset"""
        self._call(OpCode(6), (x, y,))
        return None

    def set_reactive(self) -> None:
        """continuously reconstrain the surface"""
        self._call(OpCode(7), tuple())
        return None

    def set_parent_size(self, parent_width: int, parent_height: int) -> None:
        self._call(OpCode(8), (parent_width, parent_height,))
        return None

    def set_parent_configure(self, serial: int) -> None:
        """set parent configure this is a response to"""
        self._call(OpCode(9), (serial,))
        return None

    def __enter__(self) -> XdgPositioner:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    class Error(Enum):
        INVALID_INPUT = 0

    class Anchor(Enum):
        NONE = 0
        TOP = 1
        BOTTOM = 2
        LEFT = 3
        RIGHT = 4
        TOP_LEFT = 5
        BOTTOM_LEFT = 6
        TOP_RIGHT = 7
        BOTTOM_RIGHT = 8

    class Gravity(Enum):
        NONE = 0
        TOP = 1
        BOTTOM = 2
        LEFT = 3
        RIGHT = 4
        TOP_LEFT = 5
        BOTTOM_LEFT = 6
        TOP_RIGHT = 7
        BOTTOM_RIGHT = 8

    class ConstraintAdjustment(Flag):
        NONE = 0
        SLIDE_X = 1
        SLIDE_Y = 2
        FLIP_X = 4
        FLIP_Y = 8
        RESIZE_X = 16
        RESIZE_Y = 32

def _unpack_enum_xdg_positioner(name: str, value: int) -> Any:
    if name == "error":
        return XdgPositioner.Error(value)
    if name == "anchor":
        return XdgPositioner.Anchor(value)
    if name == "gravity":
        return XdgPositioner.Gravity(value)
    if name == "constraint_adjustment":
        return XdgPositioner.ConstraintAdjustment(value)
    return None
XdgPositioner.interface.unpack_enum = _unpack_enum_xdg_positioner

PROXIES["xdg_positioner"] = XdgPositioner

class XdgSurface(Proxy):
    """desktop user interface surface base interface"""
    interface: ClassVar[Interface] = Interface(
        name="xdg_surface",
        version=6,
        requests=[
            WRequest("destroy", []),
            WRequest("get_toplevel", [ArgNewId("id", "xdg_toplevel")]),
            WRequest("get_popup", [ArgNewId("id", "xdg_popup"), ArgObject("parent", "xdg_surface", True), ArgObject("positioner", "xdg_positioner")]),
            WRequest("set_window_geometry", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            WRequest("ack_configure", [ArgUInt("serial")]),
        ],
        events=[
            WEvent("configure", [ArgUInt("serial")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "not_constructed": 1,
                    "already_constructed": 2,
                    "unconfigured_buffer": 3,
                    "invalid_serial": 4,
                    "invalid_size": 5,
                    "defunct_role_object": 6,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy the xdg_surface"""
        self._call(OpCode(0), tuple())
        return None

    def get_toplevel(self) -> XdgToplevel:
        """assign the xdg_toplevel surface role"""
        id = self._connection.create_proxy(XdgToplevel)
        self._call(OpCode(1), (id,))
        return id

    def get_popup(self, parent: XdgSurface | None, positioner: XdgPositioner) -> XdgPopup:
        """assign the xdg_popup surface role"""
        id = self._connection.create_proxy(XdgPopup)
        self._call(OpCode(2), (id, parent, positioner,))
        return id

    def set_window_geometry(self, x: int, y: int, width: int, height: int) -> None:
        """set the new window geometry"""
        self._call(OpCode(3), (x, y, width, height,))
        return None

    def ack_configure(self, serial: int) -> None:
        """ack a configure event"""
        self._call(OpCode(4), (serial,))
        return None

    def __enter__(self) -> XdgSurface:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int], bool]) -> Callable[[int], bool] | None:
        """suggest a surface change"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        NOT_CONSTRUCTED = 1
        ALREADY_CONSTRUCTED = 2
        UNCONFIGURED_BUFFER = 3
        INVALID_SERIAL = 4
        INVALID_SIZE = 5
        DEFUNCT_ROLE_OBJECT = 6

def _unpack_enum_xdg_surface(name: str, value: int) -> Any:
    if name == "error":
        return XdgSurface.Error(value)
    return None
XdgSurface.interface.unpack_enum = _unpack_enum_xdg_surface

PROXIES["xdg_surface"] = XdgSurface

class XdgToplevel(Proxy):
    """toplevel surface"""
    interface: ClassVar[Interface] = Interface(
        name="xdg_toplevel",
        version=6,
        requests=[
            WRequest("destroy", []),
            WRequest("set_parent", [ArgObject("parent", "xdg_toplevel", True)]),
            WRequest("set_title", [ArgStr("title")]),
            WRequest("set_app_id", [ArgStr("app_id")]),
            WRequest("show_window_menu", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgInt("x"), ArgInt("y")]),
            WRequest("move", [ArgObject("seat", "wl_seat"), ArgUInt("serial")]),
            WRequest("resize", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgUInt("edges", "resize_edge")]),
            WRequest("set_max_size", [ArgInt("width"), ArgInt("height")]),
            WRequest("set_min_size", [ArgInt("width"), ArgInt("height")]),
            WRequest("set_maximized", []),
            WRequest("unset_maximized", []),
            WRequest("set_fullscreen", [ArgObject("output", "wl_output", True)]),
            WRequest("unset_fullscreen", []),
            WRequest("set_minimized", []),
        ],
        events=[
            WEvent("configure", [ArgInt("width"), ArgInt("height"), ArgArray("states")]),
            WEvent("close", []),
            WEvent("configure_bounds", [ArgInt("width"), ArgInt("height")]),
            WEvent("wm_capabilities", [ArgArray("capabilities")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_resize_edge": 0,
                    "invalid_parent": 1,
                    "invalid_size": 2,
                },
            ),
            WEnum(
                name="resize_edge",
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
            ),
            WEnum(
                name="state",
                values={
                    "maximized": 1,
                    "fullscreen": 2,
                    "resizing": 3,
                    "activated": 4,
                    "tiled_left": 5,
                    "tiled_right": 6,
                    "tiled_top": 7,
                    "tiled_bottom": 8,
                    "suspended": 9,
                },
            ),
            WEnum(
                name="wm_capabilities",
                values={
                    "window_menu": 1,
                    "maximize": 2,
                    "fullscreen": 3,
                    "minimize": 4,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy the xdg_toplevel"""
        self._call(OpCode(0), tuple())
        return None

    def set_parent(self, parent: XdgToplevel | None) -> None:
        """set the parent of this surface"""
        self._call(OpCode(1), (parent,))
        return None

    def set_title(self, title: str) -> None:
        """set surface title"""
        self._call(OpCode(2), (title,))
        return None

    def set_app_id(self, app_id: str) -> None:
        """set application ID"""
        self._call(OpCode(3), (app_id,))
        return None

    def show_window_menu(self, seat: WlSeat, serial: int, x: int, y: int) -> None:
        """show the window menu"""
        self._call(OpCode(4), (seat, serial, x, y,))
        return None

    def move(self, seat: WlSeat, serial: int) -> None:
        """start an interactive move"""
        self._call(OpCode(5), (seat, serial,))
        return None

    def resize(self, seat: WlSeat, serial: int, edges: ResizeEdge) -> None:
        """start an interactive resize"""
        self._call(OpCode(6), (seat, serial, edges,))
        return None

    def set_max_size(self, width: int, height: int) -> None:
        """set the maximum size"""
        self._call(OpCode(7), (width, height,))
        return None

    def set_min_size(self, width: int, height: int) -> None:
        """set the minimum size"""
        self._call(OpCode(8), (width, height,))
        return None

    def set_maximized(self) -> None:
        """maximize the window"""
        self._call(OpCode(9), tuple())
        return None

    def unset_maximized(self) -> None:
        """unmaximize the window"""
        self._call(OpCode(10), tuple())
        return None

    def set_fullscreen(self, output: WlOutput | None) -> None:
        """set the window as fullscreen on an output"""
        self._call(OpCode(11), (output,))
        return None

    def unset_fullscreen(self) -> None:
        """unset the window as fullscreen"""
        self._call(OpCode(12), tuple())
        return None

    def set_minimized(self) -> None:
        """set the window as minimized"""
        self._call(OpCode(13), tuple())
        return None

    def __enter__(self) -> XdgToplevel:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int, int, bytes], bool]) -> Callable[[int, int, bytes], bool] | None:
        """suggest a surface change"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_close(self, handler: Callable[[], bool]) -> Callable[[], bool] | None:
        """surface wants to be closed"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_configure_bounds(self, handler: Callable[[int, int], bool]) -> Callable[[int, int], bool] | None:
        """recommended window geometry bounds"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_wm_capabilities(self, handler: Callable[[bytes], bool]) -> Callable[[bytes], bool] | None:
        """compositor capabilities"""
        _opcode = OpCode(3)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_RESIZE_EDGE = 0
        INVALID_PARENT = 1
        INVALID_SIZE = 2

    class ResizeEdge(Enum):
        NONE = 0
        TOP = 1
        BOTTOM = 2
        LEFT = 4
        TOP_LEFT = 5
        BOTTOM_LEFT = 6
        RIGHT = 8
        TOP_RIGHT = 9
        BOTTOM_RIGHT = 10

    class State(Enum):
        MAXIMIZED = 1
        FULLSCREEN = 2
        RESIZING = 3
        ACTIVATED = 4
        TILED_LEFT = 5
        TILED_RIGHT = 6
        TILED_TOP = 7
        TILED_BOTTOM = 8
        SUSPENDED = 9

    class WmCapabilities(Enum):
        WINDOW_MENU = 1
        MAXIMIZE = 2
        FULLSCREEN = 3
        MINIMIZE = 4

def _unpack_enum_xdg_toplevel(name: str, value: int) -> Any:
    if name == "error":
        return XdgToplevel.Error(value)
    if name == "resize_edge":
        return XdgToplevel.ResizeEdge(value)
    if name == "state":
        return XdgToplevel.State(value)
    if name == "wm_capabilities":
        return XdgToplevel.WmCapabilities(value)
    return None
XdgToplevel.interface.unpack_enum = _unpack_enum_xdg_toplevel

PROXIES["xdg_toplevel"] = XdgToplevel

class XdgPopup(Proxy):
    """short-lived, popup surfaces for menus"""
    interface: ClassVar[Interface] = Interface(
        name="xdg_popup",
        version=6,
        requests=[
            WRequest("destroy", []),
            WRequest("grab", [ArgObject("seat", "wl_seat"), ArgUInt("serial")]),
            WRequest("reposition", [ArgObject("positioner", "xdg_positioner"), ArgUInt("token")]),
        ],
        events=[
            WEvent("configure", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            WEvent("popup_done", []),
            WEvent("repositioned", [ArgUInt("token")]),
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "invalid_grab": 0,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """remove xdg_popup interface"""
        self._call(OpCode(0), tuple())
        return None

    def grab(self, seat: WlSeat, serial: int) -> None:
        """make the popup take an explicit grab"""
        self._call(OpCode(1), (seat, serial,))
        return None

    def reposition(self, positioner: XdgPositioner, token: int) -> None:
        """recalculate the popup's location"""
        self._call(OpCode(2), (positioner, token,))
        return None

    def __enter__(self) -> XdgPopup:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int, int, int, int], bool]) -> Callable[[int, int, int, int], bool] | None:
        """configure the popup surface"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_popup_done(self, handler: Callable[[], bool]) -> Callable[[], bool] | None:
        """popup interaction is done"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_repositioned(self, handler: Callable[[int], bool]) -> Callable[[int], bool] | None:
        """signal the completion of a repositioned request"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_GRAB = 0

def _unpack_enum_xdg_popup(name: str, value: int) -> Any:
    if name == "error":
        return XdgPopup.Error(value)
    return None
XdgPopup.interface.unpack_enum = _unpack_enum_xdg_popup

PROXIES["xdg_popup"] = XdgPopup

# fmt: on
