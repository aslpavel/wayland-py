#!/usr/bin/env python
import asyncio
from typing import Any, Callable
from wayland.client import (
    WL_BUFFER,
    WL_COMPOSITOR,
    WL_SHM,
    WL_SHM_POOL,
    WL_SURFACE,
    XDG_SURFACE,
    XDG_TOPLEVEL,
    XDG_WM_BASE,
    Connection,
    SharedMemory,
)


async def main() -> None:
    # globals
    conn = await Connection().connect()
    wl_shm = conn.get_global(WL_SHM)
    wl_compositor = conn.get_global(WL_COMPOSITOR)
    xdg_wm_base = conn.get_global(XDG_WM_BASE)

    # surface
    wl_surf = conn.create_proxy(WL_SURFACE)
    wl_compositor("create_surface", wl_surf)
    xdg_surf = conn.create_proxy(XDG_SURFACE)
    xdg_wm_base("get_xdg_surface", xdg_surf, wl_surf)
    xdg_toplevel = conn.create_proxy(XDG_TOPLEVEL)
    xdg_surf("get_toplevel", xdg_toplevel)
    xdg_toplevel("set_title", "wayland-py")
    wl_surf("commit")

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
    pool = conn.create_proxy(WL_SHM_POOL)
    wl_shm("create_pool", pool, buf_mem, size)
    buf = conn.create_proxy(WL_BUFFER)
    pool("create_buffer", buf, 0, width, height, stride, 1)
    pool("destroy")

    def on_configure(serial: int) -> bool:
        print("draw")
        xdg_surf("ack_configure", serial)
        wl_surf("attach", buf, 0, 0)
        wl_surf("commit")
        return True

    xdg_surf.on("configure", on_configure)

    await conn.on_terminated()


def print_message(msg: str) -> Callable[..., bool]:
    def print_message_handler(*args: Any) -> bool:
        print(msg, args)
        return True

    return print_message_handler


if __name__ == "__main__":
    asyncio.run(main())
