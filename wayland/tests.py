import io
import unittest
from unittest.mock import Mock
from .base import ArgArray, ArgFixed, ArgInt, ArgStr, Connection


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
