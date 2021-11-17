#!/usr/bin/env python
import asyncio
from typing import Optional, Tuple
from wayland.client import ClientConnection
from wayland.protocol.wayland import WlBuffer, WlShm, WlCompositor
from wayland.protocol.xdg_shell import XdgWmBase
from wayland import SharedMemory


def draw(wl_shm: WlShm, width: int, height: int) -> WlBuffer:
    stride = width * 4
    size = stride * height
    buf_mem = SharedMemory(size)

    for y in range(height):
        for x in range(width):
            offset = y * stride + x * 4
            if (x + int(y / 8) * 8) % 16 < 8:
                buf_mem.buf[offset : offset + 4] = b"\x66\x66\x66\xff"
            else:
                buf_mem.buf[offset : offset + 4] = b"\xee\xee\xee\xff"

    with wl_shm.create_pool(buf_mem, size) as pool:
        buf = pool.create_buffer(0, width, height, stride, WlShm.Format.XRGB8888)

    @buf.on_release
    def _() -> bool:
        buf.destroy()
        buf_mem.close()
        return False

    return buf


async def main() -> None:
    # globals
    conn = await ClientConnection().connect()
    wl_shm = conn.get_global(WlShm)
    wl_compositor = conn.get_global(WlCompositor)
    xdg_wm_base = conn.get_global(XdgWmBase)

    # surface
    wl_surf = wl_compositor.create_surface()
    xdg_surf = xdg_wm_base.get_xdg_surface(wl_surf)
    xdg_toplevel = xdg_surf.get_toplevel()
    xdg_toplevel.set_title("wayland-py-basic")
    wl_surf.commit()

    # handlers
    @xdg_wm_base.on_ping
    def _(serial: int) -> bool:
        xdg_wm_base.pong(serial)
        return True

    @xdg_toplevel.on_close
    def _() -> bool:
        conn.terminate()
        return True

    size: Optional[Tuple[int, int]] = None

    @xdg_toplevel.on_configure
    def _(new_width: int, new_height: int, _: bytes) -> bool:
        nonlocal size
        new_size: Optional[Tuple[int, int]] = None
        if size is None:
            new_size = (new_width or 640, new_height or 480)
        elif new_width != 0 and new_height != 0 and size != (new_width, new_height):
            new_size = (new_width, new_height)
        if new_size is not None:
            size = new_size
            width, height = size
            wl_surf.attach(draw(wl_shm, width, height), 0, 0)
        return True

    @xdg_surf.on_configure
    def _(serial: int) -> bool:
        xdg_surf.ack_configure(serial)
        wl_surf.commit()
        return True

    await conn.on_terminated()


if __name__ == "__main__":
    asyncio.run(main())
