from boids.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from boids.entities import State
from boids.graphics import draw_line
from boids.settings.settings import Settings


def render_debug_info(state: State, settings: Settings):
    x_lines = int(SCREEN_WIDTH // state.boids.cell_size)
    y_lines = int(SCREEN_HEIGHT // state.boids.cell_size)

    draw_line(
        start=(0, 0),
        end=(SCREEN_WIDTH, 0),
        color=(1.0, 1.0, 1.0, 0.05),
        line_width=0.5,
    )

    draw_line(
        start=(0.5, 0),
        end=(0.5, SCREEN_HEIGHT),
        color=(1.0, 1.0, 1.0, 0.05),
        line_width=0.5,
    )

    for x in range(x_lines + 1):
        draw_line(
            start=(x * state.boids.cell_size, 0),
            end=(x * state.boids.cell_size, SCREEN_WIDTH),
            color=(1.0, 1.0, 1.0, 0.05),
            line_width=0.5,
        )

    for y in range(y_lines + 1):
        draw_line(
            start=(0, y * state.boids.cell_size),
            end=(SCREEN_WIDTH, y * state.boids.cell_size),
            color=(1.0, 1.0, 1.0, 0.05),
            line_width=0.5,
        )
