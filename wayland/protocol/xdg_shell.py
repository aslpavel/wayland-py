# Auto generated do not edit manually
# fmt: off
# pyright: reportPrivateUsage=false
from enum import Enum
from typing import Callable, ClassVar, Optional
from ..base import *
from .wayland import *

__all__ = [
    "xdg_wm_base",
    "xdg_positioner",
    "xdg_surface",
    "xdg_toplevel",
    "xdg_popup",
]

class xdg_wm_base(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_wm_base",
        requests=[
            ("destroy", []),
            ("create_positioner", [ArgNewId("id", "xdg_positioner")]),
            ("get_xdg_surface", [ArgNewId("id", "xdg_surface"), ArgObject("surface", "wl_surface")]),
            ("pong", [ArgUInt("serial")]),
        ],
        events=[
            ("ping", [ArgUInt("serial")]),
        ],
        enums={
            "error": {
                "role": 0,
                "defunct_surfaces": 1,
                "not_the_topmost_popup": 2,
                "invalid_popup_parent": 3,
                "invalid_surface_state": 4,
                "invalid_positioner": 5,
            },
        },
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def create_positioner(self) -> "xdg_positioner":
        _opcode = OpCode(1)
        id = self._connection.create_proxy(xdg_positioner)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_xdg_surface(self, surface: "wl_surface") -> "xdg_surface":
        _opcode = OpCode(2)
        id = self._connection.create_proxy(xdg_surface)
        _data, _fds = self._interface.pack(_opcode, (id, surface,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def pong(self, serial: int) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_ping(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class enum_error(Enum):
        role = 0
        defunct_surfaces = 1
        not_the_topmost_popup = 2
        invalid_popup_parent = 3
        invalid_surface_state = 4
        invalid_positioner = 5

class xdg_positioner(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_positioner",
        requests=[
            ("destroy", []),
            ("set_size", [ArgInt("width"), ArgInt("height")]),
            ("set_anchor_rect", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            ("set_anchor", [ArgUInt("anchor", "anchor")]),
            ("set_gravity", [ArgUInt("gravity", "gravity")]),
            ("set_constraint_adjustment", [ArgUInt("constraint_adjustment")]),
            ("set_offset", [ArgInt("x"), ArgInt("y")]),
            ("set_reactive", []),
            ("set_parent_size", [ArgInt("parent_width"), ArgInt("parent_height")]),
            ("set_parent_configure", [ArgUInt("serial")]),
        ],
        events=[
        ],
        enums={
            "error": {
                "invalid_input": 0,
            },
            "anchor": {
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
            "gravity": {
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
            "constraint_adjustment": {
                "none": 0,
                "slide_x": 1,
                "slide_y": 2,
                "flip_x": 4,
                "flip_y": 8,
                "resize_x": 16,
                "resize_y": 32,
            },
        },
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_size(self, width: int, height: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_anchor_rect(self, x: int, y: int, width: int, height: int) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_anchor(self, anchor: "enum_anchor") -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (anchor,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_gravity(self, gravity: "enum_gravity") -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (gravity,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_constraint_adjustment(self, constraint_adjustment: int) -> None:
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, (constraint_adjustment,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_offset(self, x: int, y: int) -> None:
        _opcode = OpCode(6)
        _data, _fds = self._interface.pack(_opcode, (x, y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_reactive(self) -> None:
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
        _opcode = OpCode(9)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    class enum_error(Enum):
        invalid_input = 0

    class enum_anchor(Enum):
        none = 0
        top = 1
        bottom = 2
        left = 3
        right = 4
        top_left = 5
        bottom_left = 6
        top_right = 7
        bottom_right = 8

    class enum_gravity(Enum):
        none = 0
        top = 1
        bottom = 2
        left = 3
        right = 4
        top_left = 5
        bottom_left = 6
        top_right = 7
        bottom_right = 8

    class enum_constraint_adjustment(Enum):
        none = 0
        slide_x = 1
        slide_y = 2
        flip_x = 4
        flip_y = 8
        resize_x = 16
        resize_y = 32

class xdg_surface(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_surface",
        requests=[
            ("destroy", []),
            ("get_toplevel", [ArgNewId("id", "xdg_toplevel")]),
            ("get_popup", [ArgNewId("id", "xdg_popup"), ArgObject("parent", "xdg_surface"), ArgObject("positioner", "xdg_positioner")]),
            ("set_window_geometry", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            ("ack_configure", [ArgUInt("serial")]),
        ],
        events=[
            ("configure", [ArgUInt("serial")]),
        ],
        enums={
            "error": {
                "not_constructed": 1,
                "already_constructed": 2,
                "unconfigured_buffer": 3,
            },
        },
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def get_toplevel(self) -> "xdg_toplevel":
        _opcode = OpCode(1)
        id = self._connection.create_proxy(xdg_toplevel)
        _data, _fds = self._interface.pack(_opcode, (id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def get_popup(self, parent: "xdg_surface", positioner: "xdg_positioner") -> "xdg_popup":
        _opcode = OpCode(2)
        id = self._connection.create_proxy(xdg_popup)
        _data, _fds = self._interface.pack(_opcode, (id, parent, positioner,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return id

    def set_window_geometry(self, x: int, y: int, width: int, height: int) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (x, y, width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def ack_configure(self, serial: int) -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_configure(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class enum_error(Enum):
        not_constructed = 1
        already_constructed = 2
        unconfigured_buffer = 3

class xdg_toplevel(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_toplevel",
        requests=[
            ("destroy", []),
            ("set_parent", [ArgObject("parent", "xdg_toplevel")]),
            ("set_title", [ArgStr("title")]),
            ("set_app_id", [ArgStr("app_id")]),
            ("show_window_menu", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgInt("x"), ArgInt("y")]),
            ("move", [ArgObject("seat", "wl_seat"), ArgUInt("serial")]),
            ("resize", [ArgObject("seat", "wl_seat"), ArgUInt("serial"), ArgUInt("edges", "resize_edge")]),
            ("set_max_size", [ArgInt("width"), ArgInt("height")]),
            ("set_min_size", [ArgInt("width"), ArgInt("height")]),
            ("set_maximized", []),
            ("unset_maximized", []),
            ("set_fullscreen", [ArgObject("output", "wl_output")]),
            ("unset_fullscreen", []),
            ("set_minimized", []),
        ],
        events=[
            ("configure", [ArgInt("width"), ArgInt("height"), ArgArray("states")]),
            ("close", []),
        ],
        enums={
            "resize_edge": {
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
            "state": {
                "maximized": 1,
                "fullscreen": 2,
                "resizing": 3,
                "activated": 4,
                "tiled_left": 5,
                "tiled_right": 6,
                "tiled_top": 7,
                "tiled_bottom": 8,
            },
        },
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_parent(self, parent: "xdg_toplevel") -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (parent,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_title(self, title: str) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (title,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_app_id(self, app_id: str) -> None:
        _opcode = OpCode(3)
        _data, _fds = self._interface.pack(_opcode, (app_id,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def show_window_menu(self, seat: "wl_seat", serial: int, x: int, y: int) -> None:
        _opcode = OpCode(4)
        _data, _fds = self._interface.pack(_opcode, (seat, serial, x, y,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def move(self, seat: "wl_seat", serial: int) -> None:
        _opcode = OpCode(5)
        _data, _fds = self._interface.pack(_opcode, (seat, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def resize(self, seat: "wl_seat", serial: int, edges: "enum_resize_edge") -> None:
        _opcode = OpCode(6)
        _data, _fds = self._interface.pack(_opcode, (seat, serial, edges,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_max_size(self, width: int, height: int) -> None:
        _opcode = OpCode(7)
        _data, _fds = self._interface.pack(_opcode, (width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_min_size(self, width: int, height: int) -> None:
        _opcode = OpCode(8)
        _data, _fds = self._interface.pack(_opcode, (width, height,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_maximized(self) -> None:
        _opcode = OpCode(9)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def unset_maximized(self) -> None:
        _opcode = OpCode(10)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_fullscreen(self, output: "wl_output") -> None:
        _opcode = OpCode(11)
        _data, _fds = self._interface.pack(_opcode, (output,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def unset_fullscreen(self) -> None:
        _opcode = OpCode(12)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def set_minimized(self) -> None:
        _opcode = OpCode(13)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_configure(self, handler: Callable[[int, int, bytes], bool]) -> Optional[Callable[[int, int, bytes], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_close(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class enum_resize_edge(Enum):
        none = 0
        top = 1
        bottom = 2
        left = 4
        top_left = 5
        bottom_left = 6
        right = 8
        top_right = 9
        bottom_right = 10

    class enum_state(Enum):
        maximized = 1
        fullscreen = 2
        resizing = 3
        activated = 4
        tiled_left = 5
        tiled_right = 6
        tiled_top = 7
        tiled_bottom = 8

class xdg_popup(Proxy):
    interface: ClassVar[Interface] = Interface(
        name="xdg_popup",
        requests=[
            ("destroy", []),
            ("grab", [ArgObject("seat", "wl_seat"), ArgUInt("serial")]),
            ("reposition", [ArgObject("positioner", "xdg_positioner"), ArgUInt("token")]),
        ],
        events=[
            ("configure", [ArgInt("x"), ArgInt("y"), ArgInt("width"), ArgInt("height")]),
            ("popup_done", []),
            ("repositioned", [ArgUInt("token")]),
        ],
        enums={
            "error": {
                "invalid_grab": 0,
            },
        },
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def destroy(self) -> None:
        _opcode = OpCode(0)
        _data, _fds = self._interface.pack(_opcode, tuple())
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def grab(self, seat: "wl_seat", serial: int) -> None:
        _opcode = OpCode(1)
        _data, _fds = self._interface.pack(_opcode, (seat, serial,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def reposition(self, positioner: "xdg_positioner", token: int) -> None:
        _opcode = OpCode(2)
        _data, _fds = self._interface.pack(_opcode, (positioner, token,))
        self._connection._message_submit(Message(self._id, _opcode, _data, _fds))
        return None

    def on_configure(self, handler: Callable[[int, int, int, int], bool]) -> Optional[Callable[[int, int, int, int], bool]]:
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_popup_done(self, handler: Callable[[], bool]) -> Optional[Callable[[], bool]]:
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_repositioned(self, handler: Callable[[int], bool]) -> Optional[Callable[[int], bool]]:
        _opcode = OpCode(2)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class enum_error(Enum):
        invalid_grab = 0

# fmt: on