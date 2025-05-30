import math
import os

import numpy as np  # NumPy is highly recommended for efficient array operations
import pygame
from OpenGL import GL as gl
from OpenGL import GLU as glu  # GLU is generally not needed for modern VBO approaches
from pygame.locals import *


# --- Your Vector2 class (assuming you have one) ---
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# --- Global lists to store vertex data ---
# We'll store all vertex coordinates and all vertex colors
all_vertex_positions = []
all_vertex_colors = []

# --- Buffers ID ---
vbo_positions_id = None
vbo_colors_id = None

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"


def initialize_vbos():
    """
    Call this once at the beginning of your program (after OpenGL context is created).
    """
    global vbo_positions_id, vbo_colors_id

    # Generate buffer IDs
    vbo_ids = gl.glGenBuffers(2)  # Generate 2 buffer IDs
    vbo_positions_id = vbo_ids[0]
    vbo_colors_id = vbo_ids[1]

    # It's good practice to initially bind and allocate buffer data
    # even if it's empty or with some initial size.
    # This isn't strictly necessary here if update_vbos is always called before drawing.


def generate_triangle_data(
    center: Vector2,
    size: float,
    color: tuple[float, float, float, float],
    direction: float = 0.0,
):
    """
    This function NO LONGER draws. It appends vertex data to global lists.
    """
    global all_vertex_positions, all_vertex_colors

    for i in range(3):
        angle = direction + 2 * math.pi * i / 3
        x = center.x + math.cos(angle) * size
        y = center.y + math.sin(angle) * size
        all_vertex_positions.extend([x, y])  # Add x, y for this vertex

        # Add the color for this vertex (repeated for each vertex of the triangle)
        all_vertex_colors.extend(color)


def update_vbos():
    """
    Uploads the collected vertex data to the GPU.
    Call this after all triangle data for the current frame has been generated.
    """
    global vbo_positions_id, vbo_colors_id, all_vertex_positions, all_vertex_colors

    if not all_vertex_positions:  # Nothing to draw
        return

    # --- Upload Position Data ---
    # Convert to a NumPy array of type float32
    positions_np = np.array(all_vertex_positions, dtype=np.float32)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_positions_id)
    # Upload data to the currently bound buffer.
    # GL_STATIC_DRAW is a hint that data will be modified once and used many times.
    # GL_DYNAMIC_DRAW if you change it frequently.
    gl.glBufferData(gl.GL_ARRAY_BUFFER, positions_np.nbytes, positions_np, gl.GL_DYNAMIC_DRAW)

    # --- Upload Color Data ---
    colors_np = np.array(all_vertex_colors, dtype=np.float32)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, colors_np.nbytes, colors_np, gl.GL_DYNAMIC_DRAW)

    # Unbind the buffer (good practice, though not strictly necessary if you rebind before use)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)


def batch_render_triangles():
    """
    Draws all triangles whose data is in the VBOs.
    """
    global vbo_positions_id, vbo_colors_id, all_vertex_positions

    if not all_vertex_positions:  # Nothing to draw
        return

    # --- Enable client states: we are sending arrays of data ---
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glEnableClientState(gl.GL_COLOR_ARRAY)

    # --- Point to the position data in the VBO ---
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_positions_id)
    # Describe the vertex data: 2 components (x, y), type float, not normalized,
    # stride 0 (tightly packed), pointer None (data starts at the beginning of the VBO).
    gl.glVertexPointer(2, gl.GL_FLOAT, 0, None)

    # --- Point to the color data in the VBO ---
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_colors_id)
    # Describe the color data: 4 components (r, g, b, a), type float, not normalized,
    # stride 0, pointer None.
    gl.glColorPointer(4, gl.GL_FLOAT, 0, None)

    # --- Draw all triangles ---
    # GL_TRIANGLES: interpret vertex data as triangles
    # 0: starting index in the enabled arrays
    # len(all_vertex_positions) // 2: total number of vertices (since each vertex has 2 components)
    num_vertices = len(all_vertex_positions) // 2
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, num_vertices)

    # --- Disable client states after drawing ---
    gl.glDisableClientState(gl.GL_COLOR_ARRAY)
    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

    # Unbind buffers (optional, but good practice)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)


def clear_triangle_data():
    """
    Clears the data for the next frame. Call this at the end of your main loop.
    """
    global all_vertex_positions, all_vertex_colors
    all_vertex_positions.clear()
    all_vertex_colors.clear()


# --- Main Pygame Loop Example ---
def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    # glu.gluPerspective(45, (display[0] / display[1]), 0.1, 50.0) # Example perspective
    # gl.glTranslatef(0.0, 0.0, -5) # Move camera back

    # For 2D rendering, you might prefer an orthographic projection
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, display[0], 0, display[1], -1, 1)  # Map OGL coords to screen pixels
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    initialize_vbos()  # IMPORTANT: Initialize VBOs once

    triangles_to_render = []
    # Example: Create a list of triangle parameters
    for i in range(1000):  # Let's say 1000 triangles
        triangles_to_render.append(
            {
                "center": Vector2(100 + (i % 30) * 20, 100 + (i // 30) * 20),
                "size": 10.0,
                "color": ((i % 3) / 2.0, ((i + 1) % 3) / 2.0, ((i + 2) % 3) / 2.0, 1.0),
                "direction": (i / 1000.0) * 2 * math.pi,
            }
        )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 1. Clear screen
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 2. Generate data for all triangles for the current frame
        for tri_params in triangles_to_render:
            generate_triangle_data(
                tri_params["center"], tri_params["size"], tri_params["color"], tri_params["direction"]
            )

        # 3. Upload the collected data to VBOs
        update_vbos()

        # 4. Render all triangles from VBOs with one draw call
        batch_render_triangles()

        # 5. Clear the CPU-side lists for the next frame
        clear_triangle_data()

        pygame.display.flip()
        pygame.time.wait(10)

    # Cleanup (optional, OS usually handles it, but good practice)
    global vbo_positions_id, vbo_colors_id
    if vbo_positions_id is not None and vbo_colors_id is not None:
        gl.glDeleteBuffers(2, [vbo_positions_id, vbo_colors_id])

    pygame.quit()


if __name__ == "__main__":
    main()
