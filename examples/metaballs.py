#!/usr/bin/env python
from __future__ import annotations
import asyncio
import math
import time
import numpy as np
import numpy.linalg as la
import numpy.typing as npt
from typing import Callable, Optional, List, Tuple
from wayland import SharedMemory
from wayland.client import ClientConnection
from wayland.protocol.wayland import WlBuffer, WlShm, WlCompositor, WlSurface
from wayland.protocol.xdg_shell import XdgSurface, XdgToplevel, XdgWmBase

COLOR_SIZE = 4  # WlShm.Format.XRGB8888
INT32_MAX = (1 << 31) - 1


class Window:
    __slots__ = [
        "_conn",
        "_wl_surf",
        "_xdg_surf",
        "_xdg_toplevel",
        "_buf_mem",
        "_buf_index",
        "_bufs",
        "_width",
        "_height",
        "_is_closed",
    ]
    _conn: ClientConnection
    _wl_surf: WlSurface
    _xdg_surf: XdgSurface
    _xdg_toplevel: XdgToplevel
    _buf_mem: Optional[SharedMemory]
    _buf_index: int
    _bufs: List[WlBuffer]
    _width: int
    _height: int
    _is_closed: bool

    def __init__(self, conn: ClientConnection) -> None:
        self._conn = conn
        self._is_closed = False
        wl_compositor = conn.get_global(WlCompositor)
        xdg_wm_base = conn.get_global(XdgWmBase)

        self._wl_surf = wl_compositor.create_surface()
        self._xdg_surf = xdg_wm_base.get_xdg_surface(self._wl_surf)
        self._xdg_surf.on_configure(self._on_xdg_surf_configure)
        self._xdg_toplevel = self._xdg_surf.get_toplevel()
        self._xdg_toplevel.set_app_id("metaballs")
        self._xdg_toplevel.on_configure(self._on_tolevel_configure)
        self._wl_surf.commit()

        self._width = 0
        self._height = 0
        self._buf_mem = None
        self._bufs = []
        self.resize(640, 480)

    def resize(self, width: int, height: int) -> bool:
        if width <= 0 or height <= 0:
            return False
        if self._width == width and self._height == height:
            return False
        self._width = width
        self._height = height

        # free buffers
        if self._buf_mem:
            self._buf_mem.close()
        for buf in self._bufs:
            buf.destroy()
        self._bufs.clear()

        # allocate buffers
        count = 2
        size = self._width * self._height * COLOR_SIZE
        self._buf_mem = SharedMemory(size * count)
        wl_shm = self._conn.get_global(WlShm)
        with wl_shm.create_pool(self._buf_mem, size * count) as pool:
            for index in range(count):
                buf = pool.create_buffer(
                    size * index,
                    self._width,
                    self._height,
                    self._width * COLOR_SIZE,
                    WlShm.Format.XRGB8888,
                )
                self._bufs.append(buf)
                buf.on_release(self._on_buf_release(index))
        self._buf_index = 0
        self.draw()
        return True

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def render(self, image: npt.NDArray[np.uint8], now: Optional[int] = None) -> None:
        image[:, :] = [211, 134, 155, 255]

    async def animate(self) -> None:
        await self._conn.sync()  # wait for first xdg_sruface.configure
        now: Optional[int] = None
        while not self._is_closed and not self._conn.is_terminated:
            callback = self._wl_surf.frame()
            done = callback.on_async("done")
            self.draw(now)
            self._wl_surf.commit()
            now = (await done)[0]

    def on_close(self, handler: Callable[[], None]) -> None:
        @self._xdg_toplevel.on_close
        def _() -> bool:
            self.close()
            handler()
            return False

    def close(self) -> None:
        is_closed, self._is_closed = self._is_closed, True
        if is_closed:
            return

        if self._buf_mem:
            self._buf_mem.close()
            self._buf_mem = None
        for buf in self._bufs:
            buf.destroy()
        self._bufs.clear()

        self._xdg_toplevel.destroy()
        self._xdg_surf.destroy()
        self._wl_surf.destroy()

    def draw(self, now: Optional[int] = None) -> None:
        size = self._width * self._height * COLOR_SIZE
        if self._buf_mem is None or not self._bufs:
            return
        buf = self._bufs[self._buf_index]
        image: npt.NDArray[np.uint8] = np.ndarray(
            shape=(self._height, self._width, COLOR_SIZE),
            dtype=np.uint8,
            buffer=self._buf_mem.buf,
            offset=size * self._buf_index,
        )
        self._buf_index = (self._buf_index + 1) % len(self._bufs)
        self.render(image, now)
        self._wl_surf.attach(buf, 0, 0)
        self._wl_surf.damage_buffer(0, 0, INT32_MAX, INT32_MAX)

    def _on_buf_release(self, index: int) -> Callable[[], bool]:
        def _on_buf_release() -> bool:
            self._buf_index = index
            return True

        return _on_buf_release

    def _on_tolevel_configure(self, width: int, height: int, _: bytes) -> bool:
        self.resize(width, height)
        return True

    def _on_xdg_surf_configure(self, serial: int) -> bool:
        self._xdg_surf.ack_configure(serial)
        self._wl_surf.commit()
        return True


class Metaball:
    __slots__ = ["position", "velocity", "radius"]
    radius: float
    position: Tuple[float, float]
    velocity: Tuple[float, float]

    def __init__(
        self,
        radius: float,
        position: Tuple[float, float],
        velocity: Tuple[float, float],
    ) -> None:
        self.radius = radius
        self.position = position
        self.velocity = velocity

    def tick(self, width: float, height: float, delta: int) -> None:
        x, y = self.position
        dx, dy = self.velocity

        scale = delta / 64
        x += dx * scale
        y += dy * scale

        if x < self.radius or x > width - self.radius:
            dx = math.copysign(dx, width / 2 - x)
        if y < self.radius or y > height - self.radius:
            dy = math.copysign(dy, height / 2 - y)

        self.position = x, y
        self.velocity = dx, dy


# B, G, R, A
BLACK = np.array([0, 0, 0, 0], dtype=np.uint8)
BLUE = np.array([0x78, 0x66, 0x07, 0xFF], dtype=np.uint8)
YELLOW = np.array([0x21, 0x99, 0xD7, 0xFF], dtype=np.uint8)
WIDTH = 10.0


class Metaballs(Window):
    __slots__ = ["metaballs", "_grid", "_now"]
    metaballs: List[Metaball]
    _grid: npt.NDArray[np.float64]
    _now: Optional[int]

    def __init__(self, conn: ClientConnection, metaballs: List[Metaball]):
        self.metaballs = metaballs
        self._grid = np.array([], dtype=np.uint8)
        self._now = None
        super().__init__(conn)

    def tick(self, delta: int):
        width = WIDTH
        height = width / self.width * self.height
        for metaball in self.metaballs:
            metaball.tick(height, width, delta)

    def render(self, image: npt.NDArray[np.uint8], now: Optional[int] = None) -> None:
        if self._grid.shape[:2] != image.shape[:2]:
            self._grid = self._make_grid()

        delta = now - self._now if now and self._now else 16
        self._now = now
        self.tick(delta)

        render_start = time.time()
        values = self.at(self._grid)
        image[..., :] = BLACK
        image[values >= 0.9] = YELLOW
        image[values >= 1.1] = BLUE
        render_time = time.time() - render_start

        print(
            "\x1b[Kfps={:.2f} render={:.2f}ms\r".format(
                1000 / delta, render_time * 1000
            ),
            end="",
        )

    def _make_grid(self) -> npt.NDArray[np.float64]:
        width = WIDTH
        height = width / self.width * self.height
        xs: npt.NDArray[np.float64] = np.broadcast_to(
            np.linspace(0, width, self.width), (self.height, self.width)
        )
        ys: npt.NDArray[np.float64] = np.broadcast_to(
            np.linspace(0, height, self.height)[..., np.newaxis],
            (self.height, self.width),
        )
        return np.stack((ys, xs), axis=-1)

    def at(self, points: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """Isosurface of 0 represent metaballs

        Function defined as f(point) = \\sum radii_i/||coors_i - point||_2 - 1
        radii: (balls_count, 1) radii of metaballs
        coords: (balls_count, 2) coordinates of metaballs
        points: (points_shape, coord) coordinate of a point where we computing value
        """
        radii = np.array([metaball.radius for metaball in self.metaballs])
        coords = np.array([metaball.position for metaball in self.metaballs])
        positions_flat = points.reshape(-1, 1, 2)
        mballs = radii / la.norm(coords - positions_flat, axis=-1).clip(1e-6, None)
        return np.sum(mballs, axis=-1).reshape(points.shape[:-1])


async def main() -> None:
    metaballs = [
        Metaball(0.3, (1.0, 1.0), (0.3, 0.2)),
        Metaball(1, (1.5, 1.5), (0.1, 0.4)),
        Metaball(1.5, (7.0, 5.0), (-0.25, 0.13)),
    ]
    async with ClientConnection() as conn:
        window = Metaballs(conn, metaballs)
        window.on_close(lambda: conn.terminate())
        await window.animate()


if __name__ == "__main__":
    asyncio.run(main())
