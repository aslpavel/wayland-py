#!/usr/bin/env python
from __future__ import annotations
import asyncio
import numpy as np
import numpy.typing as npt
from typing import Callable, Optional, List
from wayland.client import ClientConnection
from wayland.protocol.wayland import WlBuffer, WlShm, WlCompositor, WlSurface
from wayland.protocol.xdg_shell import XdgSurface, XdgToplevel, XdgWmBase
from wayland import SharedMemory

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
        self._xdg_toplevel.on_configure(self._on_tolevel_configure)
        self._wl_surf.commit()

        self._width = 0
        self._height = 0
        self._buf_mem = None
        self._bufs = []
        self.resize(640, 480)

    def resize(self, width: int, height: int):
        if width <= 0 or height <= 0:
            return
        if self._width == width and self._height == height:
            return
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
        self._draw()

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def draw(self, image: npt.NDArray[np.uint8]) -> None:
        image[:, :] = [211, 134, 155, 255]

    async def anmiate(self) -> None:
        await self._conn.sync()  # wait for first xdg_sruface.configure
        while not self._is_closed and not self._conn.is_terminated:
            callback = self._wl_surf.frame()
            done = callback.on_async("done")
            self._draw()
            self._wl_surf.commit()
            await done

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

    def _draw(self) -> None:
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
        self.draw(image)
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
    position: npt.NDArray[np.float64]
    velocity: npt.NDArray[np.float64]

    def __init__(
        self,
        radius: float,
        position: npt.NDArray[np.float64],
        velocity: npt.NDArray[np.float64],
    ) -> None:
        self.radius = radius
        self.position = np.array(position)
        self.velocity = np.array(velocity)

    def tick(self, width: float, height: float) -> None:
        self.position += self.velocity
        x, y = self.position
        dx, dy = self.velocity
        if x < self.radius or x > width - self.radius:
            dx = -dx
        if y < self.radius or y > height - self.radius:
            dy = -dy
        self.velocity = np.array([dx, dy])


class Metaballs(Window):
    __slots__ = ["metaballs"]

    def __init__(self, conn: ClientConnection, metaballs: List[Metaball]):
        super().__init__(conn)
        self.metaballs = metaballs

    def tick(self, width: float, height: float):
        for metaball in self.metaballs:
            metaball.tick(width, height)

    def at(self, points: npt.NDArray[np.float64]):
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
        Metaball(0.3, [1.0, 1.0], [0.3, 0.2]),
        Metaball(1, [1.5, 1.5], [0.1, 0.4]),
        Metaball(1.5, [7.0, 5.0], [-0.25, 0.13]),
    ]
    async with ClientConnection() as conn:
        window = Metaballs(conn, metaballs)
        window.on_close(lambda: conn.terminate())
        # await conn.sync()
        await window.anmiate()


if __name__ == "__main__":
    asyncio.run(main())
