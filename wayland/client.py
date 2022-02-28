# pyright: reportPrivateUsage=false
from __future__ import annotations
import os
import sys
import socket
from typing import Optional, Set, TypeVar, Type, Dict, Tuple
from .base import Connection, Interface, Proxy, Id
from .protocol.wayland import WlDisplay, WlRegistry, WlShm

P = TypeVar("P", bound="Proxy")


class ClientConnection(Connection):
    _path: str
    _display: WlDisplay
    _registry: WlRegistry
    # interface_name -> (name, version, proxy)
    _registry_globals: Dict[str, Tuple[int, int, Optional[Proxy]]]
    _shm_formats: Set[WlShm.Format]

    def __init__(self, path: Optional[str] = None):
        super().__init__()

        if path is not None:
            self._path = path
        else:
            runtime_dir = os.getenv("XDG_RUNTIME_DIR")
            if runtime_dir is None:
                raise RuntimeError("XDG_RUNTIME_DIR is not set")
            display = os.getenv("WAYLAND_DISPLAY", "wayland-0")
            self._path = os.path.join(runtime_dir, display)

        self._shm_formats = set()

        self._display = self.create_proxy(WlDisplay)
        self._display._is_attached = True  # display is always attached
        self._display.on_error(self._on_display_error)
        self._display.on_delete_id(self._on_display_delete_id)

        self._registry_globals = {}
        self._registry = self._display.get_registry()
        self._registry.on_global(self._on_registry_global)
        self._registry.on_global_remove(self._on_registry_global_remove)

    @property
    def display(self) -> WlDisplay:
        return self._display

    @property
    def shm_formats(self) -> Set[WlShm.Format]:
        return self._shm_formats

    def get_global(self, proxy_type: Type[P]) -> P:
        """Get global by proxy type"""
        if not hasattr(proxy_type, "interface"):
            raise TypeError("cannot get untyped proxy")
        interface = proxy_type.interface
        entry = self._registry_globals.get(interface.name)
        if entry is None:
            raise RuntimeError(f"no globals provide: {interface}")
        name, version, proxy = entry
        if proxy is None:
            proxy = self.create_proxy(proxy_type)
            self._registry.bind(name, interface.name, version, proxy)
            self._proxy_setup(proxy)
            self._registry_globals[interface.name] = (name, version, proxy)
        if not isinstance(proxy, proxy_type):
            raise ValueError("global has already been bound by untyped proxy")
        return proxy

    def get_global_by_interface(self, interface: Interface) -> Proxy:
        """Get global exposing interface"""
        entry = self._registry_globals.get(interface.name)
        if entry is None:
            raise RuntimeError(f"no globals provide: {interface}")
        name, version, proxy = entry
        if proxy is None:
            proxy = self.create_proxy_by_interface(interface)
            self._registry.bind(name, interface.name, version, proxy)
            self._proxy_setup(proxy)
            self._registry_globals[interface.name] = (name, version, proxy)
        return proxy

    async def connect(self) -> ClientConnection:
        await super().connect()
        await self.sync()
        return self

    async def sync(self) -> None:
        """Ensures all requests are processed

        This function can be used as a barrier to ensure all previous
        requests and resulting events have been handled.
        """
        callback = self.display.sync()
        await callback.on_async("done")

    async def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        sock.connect(self._path)
        return sock

    def _proxy_setup(self, proxy: Proxy) -> None:
        """Do additional proxy setup based on its type"""
        if proxy._interface.name == "xdg_wm_base":

            def pong(serial: int) -> bool:
                proxy("pong", serial)
                return True

            proxy.on("ping", pong)

        elif proxy._interface.name == "wl_shm":

            def format(fmt: WlShm.Format) -> bool:
                self._shm_formats.add(fmt)
                return True

            proxy.on("format", format)

    def _on_display_error(self, proxy: Proxy, code: int, message: str) -> bool:
        """Handle for `wl_display.error` event"""
        print(
            f"\x1b[91mERROR: proxy='{proxy}' code='{code}' message='{message}'\x1b[m",
            file=sys.stderr,
        )
        self.terminate()
        return True

    def _on_display_delete_id(self, id_int: int) -> bool:
        """Unregister proxy"""
        self._delete_proxy(Id(id_int))
        return True

    def _on_registry_global(self, name: int, interface: str, version: int) -> bool:
        """Register name in registry globals"""
        self._registry_globals[interface] = (name, version, None)
        return True

    def _on_registry_global_remove(self, target_name: int) -> bool:
        """Unregister name from registry globals"""
        for interface, (name, _, proxy) in self._registry_globals.items():
            if target_name == name:
                self._registry_globals.pop(interface)
                if proxy is not None:
                    self._proxies.pop(proxy._id)
                    proxy._detach("global removed")
                break
        return True
