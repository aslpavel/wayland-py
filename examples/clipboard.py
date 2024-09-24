#!/usr/bin/env python
from __future__ import annotations

import asyncio

from wayland.client import ClientConnection
from wayland.protocol.wayland import WlDataDeviceManager, WlSeat


async def main() -> None:
    async with ClientConnection() as conn:
        await conn.sync()
        seat = conn.get_global(WlSeat)
        ddm = conn.get_global(WlDataDeviceManager)
        _data_device = ddm.get_data_device(seat)

        await asyncio.sleep(10)
        await conn.sync()
        conn.terminate()


if __name__ == "__main__":
    asyncio.run(main())
