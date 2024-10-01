#!/usr/bin/env python
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from wayland.base import SharedMemory
from wayland.client import ClientConnection
from wayland.protocol.wayland import WlBuffer, WlCompositor, WlShm
from wayland.protocol.wlr_layer_shell_unstable_v1 import (
    ZwlrLayerShellV1,
    ZwlrLayerSurfaceV1,
)


def draw(wl_shm: WlShm, width: int, height: int) -> WlBuffer:
    x_stride, y_stride = 4, 4 * width
    size = width * height * x_stride
    mem = SharedMemory(size)

    for y in range(height):
        for x in range(width):
            offset = y * y_stride + x * x_stride
            if 3 < x < width - 3 and 3 < y < height - 3:
                color = b"\x2f\xbd\xfa\xff"  # BGRA
            else:
                color = b"\x21\x99\xd7\xff"
            mem.buf[offset : offset + x_stride] = color

    with wl_shm.create_pool(mem, size) as pool:
        buf = pool.create_buffer(0, width, height, y_stride, WlShm.Format.XRGB8888)

    @buf.on_release
    def _() -> bool:
        buf.destroy()
        mem.close()
        return False

    return buf


async def main(conn: ClientConnection) -> None:
    wl_shm = conn.get_global(WlShm)
    wl_compositor = conn.get_global(WlCompositor)
    layer_shell = conn.get_global(ZwlrLayerShellV1)

    wl_surf_scale: int = 1
    wl_surf = wl_compositor.create_surface()
    layer_surf = layer_shell.get_layer_surface(
        wl_surf,
        None,
        ZwlrLayerShellV1.Layer.OVERLAY,
        "",
    )
    layer_surf.set_size(200, 100)
    layer_surf.set_anchor(
        ZwlrLayerSurfaceV1.Anchor.RIGHT | ZwlrLayerSurfaceV1.Anchor.BOTTOM
    )
    layer_surf.set_margin(0, 20, 20, 0)
    wl_surf.commit()

    @wl_surf.on_preferred_buffer_scale
    def _(scale: int) -> bool:
        nonlocal wl_surf_scale
        wl_surf_scale = scale
        wl_surf.set_buffer_scale(scale)
        return True

    @layer_surf.on_configure
    def _(serial: int, width: int, height: int) -> bool:
        layer_surf.ack_configure(serial)
        wl_surf.attach(
            draw(wl_shm, width * wl_surf_scale, height * wl_surf_scale), 0, 0
        )
        wl_surf.commit()
        return True


if __name__ == "__main__":
    ClientConnection.run(main)
