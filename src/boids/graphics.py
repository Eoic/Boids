import math

import numpy as np
import OpenGL.GL as gl
from pygame import Vector2

from boids.constants import TOP_MENU_HEIGHT


def draw_line(
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[float, float, float, float],
    line_width: float = 1.0,
):
    gl.glLineWidth(line_width)
    gl.glColor4f(*color)
    gl.glBegin(gl.GL_LINES)
    gl.glVertex2f(start[0], start[1] + TOP_MENU_HEIGHT)
    gl.glVertex2f(end[0], end[1] + TOP_MENU_HEIGHT)
    gl.glEnd()


def draw_circle(center: Vector2, radius: float, color: tuple[float, float, float, float], segments: int = 32):
    gl.glColor4f(*color)
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(center.x, center.y)

    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = center.x + math.cos(angle) * radius
        y = center.y + math.sin(angle) * radius
        gl.glVertex2f(x, y)

    gl.glEnd()


def draw_triangle(
    center: Vector2,
    size: float,
    color: tuple[float, float, float, float],
    direction: float = 0.0,
):
    gl.glColor4f(*color)
    gl.glBegin(gl.GL_TRIANGLES)

    for i in range(3):
        angle = direction + 2 * math.pi * i / 3
        x = center.x + math.cos(angle) * size
        y = center.y + math.sin(angle) * size
        gl.glVertex2f(x, y)

    gl.glEnd()


def set_orthographic_projection(screen_size: tuple[int, int]):
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, screen_size[0], screen_size[1], 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()


def clear_screen(color: tuple[float, float, float, float]):
    gl.glClearColor(*color)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)


def draw_filled_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    color: tuple[float, float, float],
):
    gl.glColor3f(*color)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x + width, y)
    gl.glVertex2f(x + width, y + height)
    gl.glVertex2f(x, y + height)
    gl.glEnd()


def draw_rect_outline(
    top_left: tuple[float, float],
    bottom_right: tuple[float, float],
    color: tuple[float, float, float, float],
    line_width: float = 1.0,
):
    gl.glLineWidth(line_width)
    gl.glColor4f(*color)
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex2f(top_left[0], top_left[1] + TOP_MENU_HEIGHT)
    gl.glVertex2f(bottom_right[0], top_left[1] + TOP_MENU_HEIGHT)
    gl.glVertex2f(*bottom_right)
    gl.glVertex2f(top_left[0], bottom_right[1])
    gl.glEnd()


def hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[float, float, float, float]:
    """
    Converts a color from HSL (Hue, Saturation, Lightness) color space to RGBA (Red, Green, Blue, Alpha).

    Args:
        hue (float): The hue component of the color, in the range [0.0, 1.0].
        saturation (float): The saturation component of the color, in the range [0.0, 1.0].
        lightness (float): The lightness component of the color, in the range [0.0, 1.0].

    Returns:
        (tuple[float, float, float, float]): A tuple representing the RGBA components, each in the range [0.0, 1.0].
    """

    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1

        if t > 1:
            t -= 1

        if t < 1 / 6:
            return p + (q - p) * 6 * t

        if t < 1 / 2:
            return q

        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6

        return p

    if saturation == 0:
        r = g = b = lightness
    else:
        q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
        p = 2 * lightness - q
        r = hue_to_rgb(p, q, hue + 1 / 3)
        g = hue_to_rgb(p, q, hue)
        b = hue_to_rgb(p, q, hue - 1 / 3)

    return (r, g, b, 1.0)


class BatchRenderer:
    def __init__(self):
        self._vertices = []
        self._colors = []

        ids = gl.glGenBuffers(2)
        self.vbo_positions_id = ids[0]
        self.vbo_colors_id = ids[1]

    def render(self):
        self._update()
        self._draw()
        self._dispose()

    def push_triangle(
        self,
        center: tuple[float, float],
        size: float,
        color: tuple[float, float, float, float],
        direction: float
    ):
        center_x, center_y = center

        for i in range(3):
            angle = direction + 2 * math.pi * i / 3
            x = center_x + math.cos(angle) * size
            y = center_y + math.sin(angle) * size
            self._push_vertex((x, y), color)

    def cleanup(self):
        if self.vbo_positions_id is not None and self.vbo_colors_id is not None:
            gl.glDeleteBuffers(2, [self.vbo_positions_id, self.vbo_colors_id])
            self.vbo_positions_id = None
            self.vbo_colors_id = None

    def _push_vertex(
        self,
        position: tuple[float, float],
        color: tuple[float, float, float, float],
    ):
        self._vertices.extend(position)
        self._colors.extend(color)

    def _update(self):
        if not self._vertices:
            return

        positions_np = np.array(self._vertices, dtype=np.float32)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_positions_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, positions_np.nbytes, positions_np, gl.GL_DYNAMIC_DRAW)

        colors_np = np.array(self._colors, dtype=np.float32)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_colors_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, colors_np.nbytes, colors_np, gl.GL_DYNAMIC_DRAW)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def _draw(self):
        if not self._vertices:
            return

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_positions_id)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_colors_id)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, None)

        vertices_count = len(self._vertices) // 2
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, vertices_count)

        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def _dispose(self):
        self._vertices.clear()
        self._colors.clear()

