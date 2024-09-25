import asyncio

from wayland.client import ClientConnection


async def main() -> None:
    async with ClientConnection() as conn:
        for desc in conn.all_globals():
            print(f"{desc.name:<2} {desc.version:<2} {desc.iface_name}")
        conn.terminate()


if __name__ == "__main__":
    asyncio.run(main())
