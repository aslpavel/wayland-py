from __future__ import annotations
import asyncio
import io
import os
import socket
import tempfile
from typing import Any, Callable, List, Set, Tuple
import unittest
from unittest.mock import Mock

from .base import ArgArray, ArgFixed, ArgInt, ArgStr, Connection, Id, Proxy
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
    async def test_client_basic(self):
        def bind(name: int, iface: str, ver: int, proxy: Proxy):
            binds.add(iface)

        binds: Set[str] = set()
        server, client = await create_connection_pair(["wl_compositor"], bind)
        _compositor = client.get_global(WlCompositor)
        await client.sync()
        self.assertEqual(binds, {"wl_compositor"})
        client.terminate()
        server.terminate()


async def create_connection_pair(
    names: List[str],
    bind: Callable[[int, str, int, Proxy], Any],
) -> Tuple[ServerConnection, ClientConnection]:
    """Create wayland server/client connection pair"""
    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "wayland-test")
        client = ClientConnection(path)
        with socket.socket(socket.AF_UNIX) as sock:
            sock.bind(path)
            sock.listen()
            server = ServerConnection(sock, names, bind)
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
    names: List[str]
    bind: Callable[[int, str, int, Proxy], Any]

    def __init__(
        self,
        server_sock: socket.socket,
        names: List[str],
        bind: Callable[[int, str, int, Proxy], Any],
    ):
        super().__init__(is_server=True)
        self.names = names
        self.bind = bind
        self.server_sock = server_sock
        self.serial = 0

        display = self._new_id_recv(Id(1), "wl_display")
        display.on("get_registry", self.on_get_registry)
        display.on("sync", self.on_sync)
        self.display = display

    def on_get_registry(self, registry: Proxy) -> bool:
        registry.on("bind", self.on_bind)
        for index, name in enumerate(self.names):
            registry("global", index, name, 128)
        return True

    def on_bind(self, name: int, iface: str, ver: int, proxy: Proxy):
        self.bind(name, iface, ver, proxy)
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
