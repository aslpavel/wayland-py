#!/usr/bin/env python
from __future__ import annotations

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from wayland.client import ClientConnection


async def main() -> None:
    async with ClientConnection() as conn:
        for desc in conn.all_globals():
            print(f"{desc.name:<2} {desc.version:<2} {desc.iface_name}")
        conn.terminate()


if __name__ == "__main__":
    asyncio.run(main())
