import io
import os
import socket
import tempfile
import unittest
from unittest.mock import Mock

from wayland.protocol.wayland import WlDisplay

from .base import ArgArray, ArgFixed, ArgInt, ArgStr, Connection, Id, Proxy
from .client import ClientConnection


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
    async def asyncSetUp(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = os.path.join(tempdir, "wayland-test")
            client = ClientConnection(path)
            with socket.socket(socket.AF_UNIX) as sock:
                sock.bind(path)
                sock.listen()
                # await client.connect()

    async def test_client_basic(self):
        pass


class ServerConnection(Connection):
    def __init__(self):
        super().__init__()

        dispaly = self.create_proxy_by_interface(
            WlDisplay.interface.swap_events_and_requests()
        )
