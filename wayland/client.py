# pyright: reportPrivateUsage=false
from __future__ import annotations

import os
import socket
import sys
from typing import NamedTuple, TypeVar

from .base import Connection, Id, Proxy
from .protocol.wayland import WlDisplay, WlRegistry, WlShm

P = TypeVar("P", bound="Proxy")


class Global(NamedTuple):
    iface_name: str
    version: int
    proxy: Proxy | None  # None means has not been allocated


class ClientConnection(Connection):
    def __init__(self, path: str | None = None):
        super().__init__()

        if path is not None:
            self._path: str = path
        else:
            runtime_dir = os.getenv("XDG_RUNTIME_DIR")
            if runtime_dir is None:
                raise RuntimeError("XDG_RUNTIME_DIR is not set")
            display = os.getenv("WAYLAND_DISPLAY", "wayland-0")
            self._path: str = os.path.join(runtime_dir, display)

        self._shm_formats: set[WlShm.Format] = set()

        # `WlDisplay` always exists and corresponds to id=1
        self._display: WlDisplay = self.create_proxy(WlDisplay)
        self._display._is_attached = True  # display is always attached
        self._display.on_error(self._on_display_error)
        self._display.on_delete_id(self._on_display_delete_id)

        self._registry_globals: dict[int, Global] = {}
        self._registry: WlRegistry = self._display.get_registry()
        self._registry.on_global(self._on_registry_global)
        self._registry.on_global_remove(self._on_registry_global_remove)

    @property
    def display(self) -> WlDisplay:
        return self._display

    @property
    def shm_formats(self) -> set[WlShm.Format]:
        return self._shm_formats

    def get_global(self, proxy_type: type[P]) -> P:
        """Get global by proxy type"""
        proxies = self.get_globals(proxy_type)
        if not proxies:
            raise RuntimeError(f"no globals provide: {proxy_type.interface.name}")
        elif len(proxies) > 1:
            raise RuntimeError(
                f"multiple globals {proxy_type.interface.name}, use `get_globals`"
            )
        return proxies[0]

    def get_globals(self, proxy_type: type[P]) -> list[P]:
        """Get global by proxy type"""
        if (interface := getattr(proxy_type, "interface", None)) is None:
            raise TypeError("cannot get untyped proxy")

        # find/bind proxies by interface name
        globals: list[P] = []
        globals_new: dict[int, Global] = {}
        for num_name, (iface_name, version, proxy) in self._registry_globals.items():
            if iface_name != interface.name:
                continue
            if proxy is None:
                proxy = self.create_proxy(proxy_type)
                self._registry.bind(num_name, iface_name, version, proxy)
                self._proxy_setup(proxy)
                globals_new[num_name] = Global(iface_name, version, proxy)
            if not isinstance(proxy, proxy_type):
                raise ValueError("global has already been bound by untyped proxy")
            globals.append(proxy)
        if globals_new:
            self._registry_globals.update(globals_new)

        return globals

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
            f"\x1b[91m[error]: proxy='{proxy}' code='{code}' message='{message}'\x1b[m",
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
        self._registry_globals[name] = Global(interface, version, None)
        return True

    def _on_registry_global_remove(self, target_name: int) -> bool:
        """Unregister name from registry globals"""
        entry = self._registry_globals.pop(target_name, None)
        if entry is not None and (proxy := entry.proxy) is not None:
            self._proxies.pop(proxy._id)
            proxy._detach("global removed: {interface}")
        return True
