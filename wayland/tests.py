# pyright: reportPrivateUsage=false
from __future__ import annotations

import asyncio
import io
import os
import socket
import tempfile
import unittest
from typing import Any, Callable, Dict, Set, Tuple
from unittest.mock import Mock

from .base import (
    ArgArray,
    ArgFixed,
    ArgInt,
    ArgStr,
    Connection,
    FdFile,
    Id,
    Proxy,
    SharedMemory,
)
from .client import ClientConnection
from .protocol.wayland import *


class TestArgs(unittest.TestCase):
    conn: Mock

    def setUp(self) -> None:
        self.conn = Mock(spec=Connection)

    def test_int(self) -> None:
        file = io.BytesIO()
        arg = ArgInt("arg")
        arg.pack(file, 127)
        self.assertEqual(file.getvalue(), b"\x7f\x00\x00\x00")
        file.seek(0)
        self.assertEqual(arg.unpack(file, self.conn), 127)

    def test_fixed(self) -> None:
        file = io.BytesIO()
        arg = ArgFixed("arg")
        arg.pack(file, 127.31)
        self.assertEqual(file.getvalue(), b"O\x7f\x00\x00")
        file.seek(0)
        self.assertAlmostEqual(arg.unpack(file, self.conn), 127.31, 2)

    def test_str(self) -> None:
        file = io.BytesIO()
        arg = ArgStr("arg")
        arg.pack(file, "string")
        self.assertEqual(file.getvalue(), b"\x07\x00\x00\x00string\x00\x00")
        file.seek(0)
        self.assertEqual(arg.unpack(file, self.conn), "string")

    def test_array(self) -> None:
        file = io.BytesIO()
        arg = ArgArray("arg")
        arg.pack(file, b"string")
        self.assertEqual(file.getvalue(), b"\x06\x00\x00\x00string\x00\x00")
        file.seek(0)
        self.assertEqual(arg.unpack(file, self.conn), b"string")


class TestClient(unittest.IsolatedAsyncioTestCase):
    async def test_client_basic(self) -> None:
        def bind(proxy: Proxy) -> None:
            binds.add(proxy._interface.name)

        binds: Set[str] = set()
        server, client = await create_connection_pair({"wl_compositor": bind})
        _compositor = client.get_global(WlCompositor)
        await client.sync()
        self.assertEqual(binds, {"wl_compositor"})

        client.terminate()
        server.terminate()

    async def test_create_buffer(self) -> None:
        def wl_shm_bind(proxy: Proxy) -> None:
            def on_create_pool(pool: Proxy, fd: FdFile, size: int) -> bool:
                def on_create_buffer(
                    buff: Proxy,
                    offset: int,
                    width: int,
                    height: int,
                    stride: int,
                    fmt: WlShm.Format,
                ) -> bool:
                    state.buff = buff
                    return True

                pool.on("destroy", ignore)
                pool.on("create_buffer", on_create_buffer)
                state.buff_mem = SharedMemory(size, fd)
                fd.close()
                return False

            proxy("format", WlShm.Format.XRGB8888)
            proxy.on("create_pool", on_create_pool)

        def wl_compositor_bind(proxy: Proxy) -> None:
            def on_create_surface(proxy: Proxy) -> bool:
                def on_attach(buff: Proxy, x: int, y: int) -> bool:
                    state.attached = True
                    return True

                def on_commit() -> bool:
                    state.commited = True
                    return True

                state.surf = proxy
                state.surf.on("attach", on_attach)
                state.surf.on("commit", on_commit)
                return False

            proxy.on("create_surface", on_create_surface)

        class State:
            surf: Proxy
            buff: Proxy
            buff_mem: SharedMemory
            attached: bool
            commited: bool

        state = State()
        state.attached = False
        state.commited = False
        server, client = await create_connection_pair(
            {
                "wl_compositor": wl_compositor_bind,
                "wl_shm": wl_shm_bind,
            }
        )

        wl_compositor = client.get_global(WlCompositor)
        wl_shm = client.get_global(WlShm)
        wl_surf = wl_compositor.create_surface()
        buff_mem = SharedMemory(16)
        with wl_shm.create_pool(buff_mem, 16) as pool:
            buff = pool.create_buffer(0, 2, 2, 8, WlShm.Format.XRGB8888)
        buff_mem.buf[:] = b"x" * 16
        wl_surf.attach(buff, 0, 0)
        wl_surf.commit()
        await client.sync()

        self.assertTrue(state.attached)
        self.assertTrue(state.commited)
        self.assertEqual(bytes(state.buff_mem.buf), b"x" * 16)

        client.terminate()
        server.terminate()


def ignore(*_: Any) -> bool:
    return True


async def create_connection_pair(
    binds: Dict[str, Callable[[Proxy], Any]],
) -> Tuple[ServerConnection, ClientConnection]:
    """Create wayland server/client connection pair"""
    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "wayland-test")
        client = ClientConnection(path)
        with socket.socket(socket.AF_UNIX) as sock:
            sock.bind(path)
            sock.listen()
            server = ServerConnection(sock, binds)
            connect = asyncio.gather(client.connect(), server.connect())
            try:
                await connect
            finally:
                connect.cancel()
    return server, client


class ServerConnection(Connection):
    display: Proxy
    serial: int
    server_sock: socket.socket
    binds: Dict[str, Callable[[Proxy], Any]]

    def __init__(
        self,
        server_sock: socket.socket,
        binds: Dict[str, Callable[[Proxy], Any]],
    ):
        super().__init__(is_server=True)
        self.binds = binds
        self.server_sock = server_sock
        self.serial = 0

        display = self._new_id_recv(Id(1), "wl_display")
        display.on("get_registry", self.on_get_registry)
        display.on("sync", self.on_sync)
        self.display = display

    def on_get_registry(self, registry: Proxy) -> bool:
        registry.on("bind", self.on_bind)
        for index, name in enumerate(self.binds):
            registry("global", index, name, 128)
        return True

    def on_bind(self, name: int, iface: str, ver: int, proxy: Proxy) -> bool:
        assert proxy._interface.name == iface
        self.binds[iface](proxy)
        return True

    def on_sync(self, callback: Proxy) -> bool:
        callback("done", self.serial_next())
        self._delete_proxy(callback)
        return True

    def serial_next(self) -> int:
        self.serial += 1
        return self.serial

    async def _create_socket(self) -> socket.socket:
        loop = asyncio.get_running_loop()
        accept = loop.create_future()
        fd = self.server_sock.fileno()
        try:
            loop.add_reader(fd, lambda: accept.set_result(None))
            await accept
        finally:
            loop.remove_reader(fd)
        sock, _ = self.server_sock.accept()
        return sock
