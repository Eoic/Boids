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
    BOUND_COLOR,
    FPS,
    GOAL_COLOR,
    SCREEN_COLOR,
    SCREEN_HEIGHT,
    SCREEN_SIZE,
    SCREEN_WIDTH,
)
from boids.entities import Boid, State
from boids.rules import RuleContext, evaluate_rules
from boids.settings.settings import Settings, load_settings, render_settings
from boids.spatialgrid import SpatialGrid

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"


def _secure_uniform(a: float, b: float) -> float:
    scale = 10**8
    return a + (b - a) * (secrets.randbelow(scale) / scale)


def create_boids(count: int) -> SpatialGrid[Boid]:
    boids = SpatialGrid[Boid](2)

    for _ in range(count):
        angle = _secure_uniform(0, 2 * math.pi)
        speed = _secure_uniform(1.0, 3.0)
        velocity = Vector2(speed, 0).rotate_rad(angle)
        boid = Boid(velocity=velocity)
        boid.position.update(secrets.randbelow(SCREEN_WIDTH + 1), secrets.randbelow(SCREEN_HEIGHT + 1))
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

    if boid.velocity.length() > max_speed:
        return boid.velocity.normalize() * max_speed

    return boid.velocity


def add_perturbation(_boid: Boid, _settings: Settings):
    return Vector2(_secure_uniform(-0.2, 0.2), _secure_uniform(-0.2, 0.2))


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

    new_grid = SpatialGrid[Boid](2)

    for boid in state.boids:
        new_grid.insert(boid)

    state.boids = new_grid


def update_boid_count(state: State, settings: Settings):
    count = cast(int, settings.get("boids", "count"))

    if len(state.boids) == count:
        return

    tree = SpatialGrid[Boid](2)

    for _ in range(count):
        angle = _secure_uniform(0, 2 * math.pi)
        speed = _secure_uniform(1.0, 3.0)
        velocity = Vector2(speed, 0).rotate_rad(angle)

        tree.insert(
            Boid(
                velocity=velocity,
                position=Vector2(
                    x=secrets.randbelow(SCREEN_WIDTH + 1),
                    y=secrets.randbelow(SCREEN_HEIGHT + 1),
                ),
            )
        )

    state.boids = tree


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
            graphics.draw_circle(boid.position, 5, BOID_COLOR)

        if settings.get("boundary", "enabled"):
            top_left = cast(tuple[float, float], settings.get("boundary", "top_left"))
            bottom_right = cast(tuple[float, float], settings.get("boundary", "bottom_right"))
            graphics.draw_rect_outline(top_left, bottom_right, BOUND_COLOR, line_width=2.0)

        if state.goal_alive:
            graphics.draw_circle(state.goal_position, 10, GOAL_COLOR)

        imgui.render()
        renderer.render(imgui.get_draw_data())
        pygame.display.flip()
        delta_time = clock.tick(FPS) / 1000


def setup_state(settings: Settings) -> State:
    count = cast(int, settings.get("boids", "count"))
    boids = create_boids(count)
    state = State(boids=boids)
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
