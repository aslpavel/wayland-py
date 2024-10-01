#!/usr/bin/env python
from __future__ import annotations

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from wayland.client import ClientConnection


async def main() -> None:
    async with ClientConnection() as conn:
        name_width = max(len(desc.iface_name) for desc in conn.all_globals())
        for desc in conn.all_globals():
            print(f"{desc.iface_name:<{name_width}} {desc.version:<2} {desc.name}")
        conn.terminate()


if __name__ == "__main__":
    asyncio.run(main())
