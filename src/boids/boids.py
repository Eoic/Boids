import math
import os
import secrets
from typing import cast

import imgui
import pygame
from imgui.integrations.pygame import PygameRenderer
from OpenGL import GL
from pygame import Vector2

from boids import graphics
from boids.constants import (
    BOID_COLOR,
    BOID_DIMENSIONS,
    BOID_MAX_INIT_SPEED,
    BOID_MAX_SPEED_COLOR_HUE,
    BOID_MIN_INIT_SPEED,
    BOID_MIN_SPEED_COLOR_HUE,
    BOID_SIZE,
    BOID_SPEED_HUE_RANGE,
    BOUND_COLOR,
    BOUND_WIDTH,
    FPS,
    GOAL_COLOR,
    GOAL_SIZE,
    PERTURBATION_MAX,
    PERTURBATION_MIN,
    SCREEN_COLOR,
    SCREEN_HEIGHT,
    SCREEN_SIZE,
    SCREEN_WIDTH,
)
from boids.entities import Boid, State
from boids.rules import RuleContext, evaluate_rules
from boids.settings.settings import Settings, load_settings, render_settings
from boids.spatialgrid import SpatialGrid
from boids.utils import clamp

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"


def _secure_uniform(a: float, b: float) -> float:
    scale = 10**8
    return a + (b - a) * (secrets.randbelow(scale) / scale)


def create_boids(count: int) -> SpatialGrid[Boid]:
    boids = SpatialGrid[Boid](BOID_DIMENSIONS)

    for _ in range(count):
        angle = _secure_uniform(0, 2 * math.pi)
        speed = _secure_uniform(BOID_MIN_INIT_SPEED, BOID_MAX_INIT_SPEED)
        velocity = Vector2(speed, 0).rotate_rad(angle)

        boid = Boid(
            velocity=velocity,
            position=Vector2(
                x=secrets.randbelow(SCREEN_WIDTH + 1),
                y=secrets.randbelow(SCREEN_HEIGHT + 1),
            ),
        )

        boids.insert(boid)

    return boids


def update_goal(state: State, settings: Settings):
    if settings.get("goal", "enabled"):
        goal_duration = cast(int, settings.get("goal", "duration_sec"))

        if not state.goal_alive:
            state.goal_position = Vector2(secrets.randbelow(SCREEN_WIDTH + 1), secrets.randbelow(SCREEN_HEIGHT + 1))
            state.goal_next_rotation = pygame.time.get_ticks() + goal_duration * 1000
            state.goal_alive = True

        if pygame.time.get_ticks() - state.goal_next_rotation >= 0:
            state.goal_position = Vector2(secrets.randbelow(SCREEN_WIDTH + 1), secrets.randbelow(SCREEN_HEIGHT + 1))
            state.goal_next_rotation = pygame.time.get_ticks() + goal_duration * 1000
    elif state.goal_alive:
        state.goal_alive = False


def limit_velocity(boid: Boid, settings: Settings):
    max_speed = cast(float, settings.get("boids", "max_speed"))
    boid.speed = boid.velocity.length()

    if boid.speed > max_speed:
        max_velocity = boid.velocity.normalize() * max_speed
        boid.speed = max_velocity.length()
        return max_velocity

    return boid.velocity


def colorize(boid: Boid, settings: Settings):
    is_enabled = settings.get("boids", "colorize_velocity")

    if not is_enabled:
        return BOID_COLOR

    radians = math.atan2(boid.velocity.y, boid.velocity.x)
    hue = (math.degrees(radians) + (0 if radians > 0 else 360)) / 360

    return graphics.hsl_to_rgb(hue, 0.8, 0.5)


def add_perturbation(_boid: Boid, _settings: Settings):
    return Vector2(
        _secure_uniform(PERTURBATION_MIN, PERTURBATION_MAX),
        _secure_uniform(PERTURBATION_MIN, PERTURBATION_MAX),
    )


def update_boids(state: State, settings: Settings, delta_time: float):
    speed = cast(float, settings.get("boids", "speed"))
    locality = cast(float, settings.get("boids", "locality_radius"))

    for boid in state.boids:
        neighbors = state.boids.search_radius(boid, locality)
        context = RuleContext(boid=boid, state=state, settings=settings, neighbors=neighbors)
        boid.velocity += evaluate_rules(context)
        boid.velocity += add_perturbation(boid, settings)
        boid.velocity = limit_velocity(boid, settings)
        boid.position += boid.velocity * speed * delta_time
        boid.color = colorize(boid, settings)

    new_grid = SpatialGrid[Boid](BOID_DIMENSIONS)

    for boid in state.boids:
        new_grid.insert(boid)

    state.boids = new_grid


def update_boid_count(state: State, settings: Settings):
    count = cast(int, settings.get("boids", "count"))

    if len(state.boids) == count:
        return

    state.boids = create_boids(count)


def process_events(renderer: PygameRenderer, state: State):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        renderer.process_event(event)


def render(renderer: PygameRenderer, clock: pygame.time.Clock):
    delta_time = 0
    settings = load_settings()
    state = setup_state(settings)

    while state.running:
        process_events(renderer, state)
        renderer.process_inputs()
        imgui.new_frame()

        settings = render_settings(settings)
        update_boid_count(state, settings)
        update_goal(state, settings)
        update_boids(state, settings, delta_time)

        graphics.clear_screen(SCREEN_COLOR)
        graphics.set_orthographic_projection(SCREEN_SIZE)

        for boid in state.boids:
            graphics.draw_triangle(boid.position, BOID_SIZE, boid.color, math.atan2(boid.velocity.y, boid.velocity.x))

        if settings.get("boundary", "enabled"):
            top_left = cast(tuple[float, float], settings.get("boundary", "top_left"))
            bottom_right = cast(tuple[float, float], settings.get("boundary", "bottom_right"))
            graphics.draw_rect_outline(top_left, bottom_right, BOUND_COLOR, line_width=BOUND_WIDTH)

        if state.goal_alive:
            graphics.draw_circle(state.goal_position, GOAL_SIZE, GOAL_COLOR)

        imgui.render()
        renderer.render(imgui.get_draw_data())
        pygame.display.flip()
        delta_time = clock.tick(FPS) / 1000


def setup_state(settings: Settings) -> State:
    count = cast(int, settings.get("boids", "count"))
    state = State(boids=create_boids(count))
    return state


def main():
    pygame.init()
    pygame.display.set_caption("Boids")
    pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF | pygame.OPENGL)
    imgui.create_context()
    renderer = PygameRenderer()
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    io = imgui.get_io()
    io.display_size = SCREEN_SIZE
    clock = pygame.time.Clock()
    render(renderer, clock)
    pygame.quit()
