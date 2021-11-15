# Auto generated do not edit manually
# fmt: off
# pyright: reportPrivateUsage=false
from __future__ import annotations
from enum import Enum, Flag
from typing import Any, Callable, ClassVar, Optional
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
    interface: ClassVar[Interface] = Interface(
        name="xdg_wm_base",
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
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy xdg_wm_base"""
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def create_positioner(self) -> XdgPositioner:
        """create a positioner object"""
        _opcode = OpCode(1)
        id = self._connection.create_proxy(XdgPositioner)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_xdg_surface(self, surface: WlSurface) -> XdgSurface:
        """create a shell surface from a surface"""
        _opcode = OpCode(2)
        id = self._connection.create_proxy(XdgSurface)
        _data, _fds = self._interface.pack(_opcode, (id, surface,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def pong(self, serial: int) -> None:
        """respond to a ping event"""
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> XdgWmBase:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_ping(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
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

class XdgPositioner(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_positioner",
        requests=[
            WRequest("destroy", []),
            WRequest("set_size", [ArgInt("width"), ArgInt("height")]),
            WRequest("set_anchor_rect", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            WRequest("set_anchor", [ArgUInt("anchor", "anchor")]),
            WRequest("set_gravity", [ArgUInt("gravity", "gravity")]),
            WRequest("set_constraint_adjustment", [ArgUInt("constraint_adjustment")]),
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
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_size(self, width: int, height: int) -> None:
        """set the size of the to-be positioned rectangle"""
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_anchor_rect(self, x: int, y: int, width: int, height: int) -> None:
        """set the anchor rectangle within the parent surface"""
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_anchor(self, anchor: Anchor) -> None:
        """set anchor rectangle anchor"""
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (anchor,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_gravity(self, gravity: Gravity) -> None:
        """set child surface gravity"""
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (gravity,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_constraint_adjustment(self, constraint_adjustment: int) -> None:
        """set the adjustment to be done when constrained"""
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, (constraint_adjustment,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_offset(self, x: int, y: int) -> None:
        """set surface position offset"""
        _opcode = OpCode(6)
        _data, _fds = self._interface.pack(_opcode, (x, y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_reactive(self) -> None:
        """continuously reconstrain the surface"""
        _opcode = OpCode(7)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_parent_size(self, parent_width: int, parent_height: int) -> None:
        _opcode = OpCode(8)
        _data, _fds = self._interface.pack(_opcode, (parent_width, parent_height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_parent_configure(self, serial: int) -> None:
        """set parent configure this is a response to"""
        _opcode = OpCode(9)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
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

class XdgSurface(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_surface",
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
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy the xdg_surface"""
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def get_toplevel(self) -> XdgToplevel:
        """assign the xdg_toplevel surface role"""
        _opcode = OpCode(1)
        id = self._connection.create_proxy(XdgToplevel)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_popup(self, parent: Optional[XdgSurface], positioner: XdgPositioner) -> XdgPopup:
        """assign the xdg_popup surface role"""
        _opcode = OpCode(2)
        id = self._connection.create_proxy(XdgPopup)
        _data, _fds = self._interface.pack(_opcode, (id, parent, positioner,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def set_window_geometry(self, x: int, y: int, width: int, height: int) -> None:
        """set the new window geometry"""
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def ack_configure(self, serial: int) -> None:
        """ack a configure event"""
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> XdgSurface:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """suggest a surface change"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        NOT_CONSTRUCTED = 1
        ALREADY_CONSTRUCTED = 2
        UNCONFIGURED_BUFFER = 3

class XdgToplevel(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_toplevel",
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
        ],
        enums=[
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
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        """destroy the xdg_toplevel"""
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_parent(self, parent: Optional[XdgToplevel]) -> None:
        """set the parent of this surface"""
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (parent,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_title(self, title: str) -> None:
        """set surface title"""
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (title,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_app_id(self, app_id: str) -> None:
        """set application ID"""
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (app_id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def show_window_menu(self, seat: WlSeat, serial: int, x: int, y: int) -> None:
        """show the window menu"""
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (seat, serial, x, y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def move(self, seat: WlSeat, serial: int) -> None:
        """start an interactive move"""
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, (seat, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def resize(self, seat: WlSeat, serial: int, edges: ResizeEdge) -> None:
        """start an interactive resize"""
        _opcode = OpCode(6)
        _data, _fds = self._interface.pack(_opcode, (seat, serial, edges,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_max_size(self, width: int, height: int) -> None:
        """set the maximum size"""
        _opcode = OpCode(7)
        _data, _fds = self._interface.pack(_opcode, (width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_min_size(self, width: int, height: int) -> None:
        """set the minimum size"""
        _opcode = OpCode(8)
        _data, _fds = self._interface.pack(_opcode, (width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_maximized(self) -> None:
        """maximize the window"""
        _opcode = OpCode(9)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def unset_maximized(self) -> None:
        """unmaximize the window"""
        _opcode = OpCode(10)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_fullscreen(self, output: Optional[WlOutput]) -> None:
        """set the window as fullscreen on an output"""
        _opcode = OpCode(11)
        _data, _fds = self._interface.pack(_opcode, (output,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def unset_fullscreen(self) -> None:
        """unset the window as fullscreen"""
        _opcode = OpCode(12)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_minimized(self) -> None:
        """set the window as minimized"""
        _opcode = OpCode(13)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> XdgToplevel:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int, int, bytes], bool]) -> Optional[Callable[[int, int, bytes], bool]]:
        """suggest a surface change"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_close(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """surface wants to be closed"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

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

class XdgPopup(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_popup",
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
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def grab(self, seat: WlSeat, serial: int) -> None:
        """make the popup take an explicit grab"""
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (seat, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def reposition(self, positioner: XdgPositioner, token: int) -> None:
        """recalculate the popup's location"""
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (positioner, token,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def __enter__(self) -> XdgPopup:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int], bool]]:
        """configure the popup surface"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_popup_done(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        """popup interaction is done"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_repositioned(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        """signal the completion of a repositioned request"""
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class Error(Enum):
        INVALID_GRAB = 0

# fmt: on