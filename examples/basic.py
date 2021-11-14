#!/usr/bin/env python
import asyncio
from typing import Any, Callable
from wayland.client import ClientConnection
from wayland.protocol.wayland import WlShm, WlCompositor
from wayland.protocol.xdg_shell import XdgWmBase
from wayland import SharedMemory


async def main() -> None:
    # globals
    conn = await ClientConnection().connect()
    wl_shm = conn.get_global(WlShm)
    wl_compositor = conn.get_global(WlCompositor)
    xdg_wm_base = conn.get_global(XdgWmBase)

    # still alive
    def pong(serial: int) -> bool:
        print("ping")
        xdg_wm_base.pong(serial)
        return True

    xdg_wm_base.on_ping(pong)

    # surface
    wl_surf = wl_compositor.create_surface()
    xdg_surf = xdg_wm_base.get_xdg_surface(wl_surf)
    xdg_toplevel = xdg_surf.get_toplevel()
    xdg_toplevel.set_title("wayland-py")
    wl_surf.commit()

    # memory buffer
    width = 640
    height = 480
    stride = width * 4
    size = stride * height
    buf_mem = SharedMemory(size)

    # draw
    for y in range(height):
        for x in range(width):
            offset = y * stride + x * 4
            if (x + int(y / 8) * 8) % 16 < 8:
                buf_mem.buf[offset : offset + 4] = b"\x66\x66\x66\xff"
            else:
                buf_mem.buf[offset : offset + 4] = b"\xee\xee\xee\xff"

    # create wl_buffer
    pool = wl_shm.create_pool(buf_mem, size)
    buf = pool.create_buffer(0, width, height, stride, WlShm.Format.xrgb8888)
    pool.destroy()

    # handle updates
    def on_configure(serial: int) -> bool:
        print("draw")
        xdg_surf.ack_configure(serial)
        wl_surf.attach(buf, 0, 0)
        wl_surf.commit()
        return True

    xdg_surf.on_configure(on_configure)

    await conn.on_terminated()


def print_message(msg: str) -> Callable[..., bool]:
    def print_message_handler(*args: Any) -> bool:
        print(msg, args)
        return True

    return print_message_handler


if __name__ == "__main__":
    asyncio.run(main())
