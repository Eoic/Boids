import math

import OpenGL.GL as gl
from pygame import Vector2

from boids.constants import TOP_MENU_HEIGHT


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
