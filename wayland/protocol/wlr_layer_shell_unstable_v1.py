# Auto generated do not edit manually
# fmt: off
# pyright: reportPrivateUsage=false,reportUnusedImport=false
from __future__ import annotations
from enum import Enum, Flag
import typing
from typing import Any, ClassVar
from collections.abc import Callable
from ..base import *
from .xdg_shell import *
from .wayland import *

__all__ = [
    "ZwlrLayerShellV1",
    "ZwlrLayerSurfaceV1",
]

class ZwlrLayerShellV1(Proxy):
    """create surfaces that are layers of the desktop"""
    interface: ClassVar[Interface] = Interface(
        name="zwlr_layer_shell_v1",
        version=5,
        requests=[
            WRequest("get_layer_surface", [ArgNewId("id", "zwlr_layer_surface_v1"), ArgObject("surface", "wl_surface"), ArgObject("output", "wl_output", True), ArgUInt("layer", "layer"), ArgStr("namespace")]),
            WRequest("destroy", []),
        ],
        events=[
        ],
        enums=[
            WEnum(
                name="error",
                values={
                    "role": 0,
                    "invalid_layer": 1,
                    "already_constructed": 2,
                },
            ),
            WEnum(
                name="layer",
                values={
                    "background": 0,
                    "bottom": 1,
                    "top": 2,
                    "overlay": 3,
                },
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def get_layer_surface(self, surface: WlSurface, output: WlOutput | None, layer: Layer, namespace: str) -> ZwlrLayerSurfaceV1:
        """create a layer_surface from a surface"""
        id = self._connection.create_proxy(ZwlrLayerSurfaceV1)
        self._call(OpCode(0), (id, surface, output, layer, namespace,))
        return id

    def destroy(self) -> None:
        """destroy the layer_shell object"""
        if self._is_destroyed or not self._is_attached or self._is_detached or self._connection.is_terminated:
            return None
        self._is_destroyed = True
        self._call(OpCode(1), ())
        return None

    def __enter__(self) -> ZwlrLayerShellV1:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def __del__(self) -> None:
        self.destroy()

    class Error(Enum):
        ROLE = 0
        INVALID_LAYER = 1
        ALREADY_CONSTRUCTED = 2

    class Layer(Enum):
        BACKGROUND = 0
        BOTTOM = 1
        TOP = 2
        OVERLAY = 3

def _unpack_enum_zwlr_layer_shell_v1(name: str, value: int) -> Any:
    if name == "error":
        return ZwlrLayerShellV1.Error(value)
    if name == "layer":
        return ZwlrLayerShellV1.Layer(value)
    return None
ZwlrLayerShellV1.interface.unpack_enum = _unpack_enum_zwlr_layer_shell_v1

PROXIES["zwlr_layer_shell_v1"] = ZwlrLayerShellV1

class ZwlrLayerSurfaceV1(Proxy):
    """layer metadata interface"""
    interface: ClassVar[Interface] = Interface(
        name="zwlr_layer_surface_v1",
        version=5,
        requests=[
            WRequest("set_size", [ArgUInt("width"), ArgUInt("height")]),
            WRequest("set_anchor", [ArgUInt("anchor", "anchor")]),
            WRequest("set_exclusive_zone", [ArgInt("zone")]),
            WRequest("set_margin", [ArgInt("top"), ArgInt("right"), ArgInt("bottom"), ArgInt("left")]),
            WRequest("set_keyboard_interactivity", [ArgUInt("keyboard_interactivity", "keyboard_interactivity")]),
            WRequest("get_popup", [ArgObject("popup", "xdg_popup")]),
            WRequest("ack_configure", [ArgUInt("serial")]),
            WRequest("destroy", []),
            WRequest("set_layer", [ArgUInt("layer", "zwlr_layer_shell_v1.layer")]),
            WRequest("set_exclusive_edge", [ArgUInt("edge", "anchor")]),
        ],
        events=[
            WEvent("configure", [ArgUInt("serial"), ArgUInt("width"), ArgUInt("height")]),
            WEvent("closed", []),
        ],
        enums=[
            WEnum(
                name="keyboard_interactivity",
                values={
                    "none": 0,
                    "exclusive": 1,
                    "on_demand": 2,
                },
            ),
            WEnum(
                name="error",
                values={
                    "invalid_surface_state": 0,
                    "invalid_size": 1,
                    "invalid_anchor": 2,
                    "invalid_keyboard_interactivity": 3,
                    "invalid_exclusive_edge": 4,
                },
            ),
            WEnum(
                name="anchor",
                values={
                    "top": 1,
                    "bottom": 2,
                    "left": 4,
                    "right": 8,
                },
                flag=True,
            ),
        ],
    )

    def __init__(self, id: Id, connection: Connection) -> None:
        super().__init__(id, connection, self.interface)

    def set_size(self, width: int, height: int) -> None:
        """sets the size of the surface"""
        self._call(OpCode(0), (width, height,))
        return None

    def set_anchor(self, anchor: Anchor) -> None:
        """configures the anchor point of the surface"""
        self._call(OpCode(1), (anchor,))
        return None

    def set_exclusive_zone(self, zone: int) -> None:
        """configures the exclusive geometry of this surface"""
        self._call(OpCode(2), (zone,))
        return None

    def set_margin(self, top: int, right: int, bottom: int, left: int) -> None:
        """sets a margin from the anchor point"""
        self._call(OpCode(3), (top, right, bottom, left,))
        return None

    def set_keyboard_interactivity(self, keyboard_interactivity: KeyboardInteractivity) -> None:
        """requests keyboard events"""
        self._call(OpCode(4), (keyboard_interactivity,))
        return None

    def get_popup(self, popup: XdgPopup) -> None:
        """assign this layer_surface as an xdg_popup parent"""
        self._call(OpCode(5), (popup,))
        return None

    def ack_configure(self, serial: int) -> None:
        """ack a configure event"""
        self._call(OpCode(6), (serial,))
        return None

    def destroy(self) -> None:
        """destroy the layer_surface"""
        if self._is_destroyed or not self._is_attached or self._is_detached or self._connection.is_terminated:
            return None
        self._is_destroyed = True
        self._call(OpCode(7), ())
        return None

    def set_layer(self, layer: ZwlrLayerShellV1.Layer) -> None:
        """change the layer of the surface"""
        self._call(OpCode(8), (layer,))
        return None

    def set_exclusive_edge(self, edge: Anchor) -> None:
        """set the edge the exclusive zone will be applied to"""
        self._call(OpCode(9), (edge,))
        return None

    def __enter__(self) -> ZwlrLayerSurfaceV1:
        return self

    def __exit__(self, *_: Any) -> None:
        self.destroy()

    def __del__(self) -> None:
        self.destroy()

    def on_configure(self, handler: Callable[[int, int, int], bool]) -> Callable[[int, int, int], bool] | None:
        """suggest a surface change"""
        _opcode = OpCode(0)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    def on_closed(self, handler: Callable[[], bool]) -> Callable[[], bool] | None:
        """surface should be closed"""
        _opcode = OpCode(1)
        old_handler, self._handlers[_opcode] = self._handlers[_opcode], handler
        return old_handler

    class KeyboardInteractivity(Enum):
        NONE = 0
        EXCLUSIVE = 1
        ON_DEMAND = 2

    class Error(Enum):
        INVALID_SURFACE_STATE = 0
        INVALID_SIZE = 1
        INVALID_ANCHOR = 2
        INVALID_KEYBOARD_INTERACTIVITY = 3
        INVALID_EXCLUSIVE_EDGE = 4

    class Anchor(Flag):
        TOP = 1
        BOTTOM = 2
        LEFT = 4
        RIGHT = 8

def _unpack_enum_zwlr_layer_surface_v1(name: str, value: int) -> Any:
    if name == "keyboard_interactivity":
        return ZwlrLayerSurfaceV1.KeyboardInteractivity(value)
    if name == "error":
        return ZwlrLayerSurfaceV1.Error(value)
    if name == "anchor":
        return ZwlrLayerSurfaceV1.Anchor(value)
    return None
ZwlrLayerSurfaceV1.interface.unpack_enum = _unpack_enum_zwlr_layer_surface_v1

PROXIES["zwlr_layer_surface_v1"] = ZwlrLayerSurfaceV1

# fmt: on
