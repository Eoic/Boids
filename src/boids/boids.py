import os
import random

import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer
from pygame import Vector2

from boids import graphics
from boids.constants import (
    BOID_COLOR,
    BOUND_COLOR,
    FPS,
    GOAL_COLOR,
    SCREEN_HEIGHT,
    SCREEN_SIZE,
    SCREEN_WIDTH,
)
from boids.entities import Boid, State
from boids.kdtree import KDTree
from boids.rules import RuleContext, evaluate_rules
from boids.settings import Settings, render_settings

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"

def create_boids(count: int) -> KDTree[Boid]:
    boids = KDTree[Boid](2)

    for _ in range(count):
        boid = Boid()

        boid.position.update(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )

        boids.insert(boid)

    return boids

def update_goal(state: State, settings: Settings):
    if settings.goal:
        if not state.goal_alive:
            state.goal_position = Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            state.goal_next_rotation = pygame.time.get_ticks() + settings.goal_duration_sec * 1000
            state.goal_alive = True

        if pygame.time.get_ticks() - state.goal_next_rotation >= 0:
            state.goal_position = Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            state.goal_next_rotation = pygame.time.get_ticks() + settings.goal_duration_sec * 1000
    elif state.goal_alive:
        state.goal_alive = False

def limit_velocity(boid: Boid, settings: Settings):
    if boid.velocity.length() > settings.max_speed:
        return boid.velocity.normalize() * settings.max_speed

    return boid.velocity

def update_boids(state: State, settings: Settings, delta_time: float):
    for boid in state.boids:
        context = RuleContext(boid, state, settings)
        boid.velocity += evaluate_rules(context)
        boid.velocity = limit_velocity(boid, settings)
        boid.position += (boid.velocity * settings.speed * delta_time)

def update_boid_count(state: State, settings: Settings):
    delta = settings.count - len(state.boids)

    if delta < 0:
        pending_remove = []

        # Pick boids to remove.
        for i, item in enumerate(state.boids):
            if i >= -delta - 1:
                break

            pending_remove.append(item)

        for item in pending_remove:
            state.boids.remove(item)

        return

    for _ in range(delta):
        boid = Boid()

        boid.position.update(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )

        state.boids.insert(boid)


def process_events(renderer: PygameRenderer, state: State):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        renderer.process_event(event)

def render(renderer: PygameRenderer, clock: pygame.time.Clock):
    delta_time = 0
    settings = Settings()
    state = setup_state(settings)

    while state.running:
        process_events(renderer, state)
        renderer.process_inputs()
        imgui.new_frame()

        settings = render_settings(settings)
        update_boid_count(state, settings)
        update_goal(state, settings)
        update_boids(state, settings, delta_time)

        gl.glClearColor(0.08, 0.1, 0.12, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        graphics.set_orthographic_projection(SCREEN_SIZE)

        for boid in state.boids:
            graphics.draw_circle(boid.position, 5, BOID_COLOR)

        graphics.draw_rect_outline(settings.bound_top_left, settings.bound_bottom_right, BOUND_COLOR, line_width=2.0)

        if state.goal_alive:
            graphics.draw_circle(state.goal_position, 10, GOAL_COLOR)

        imgui.render()
        renderer.render(imgui.get_draw_data())
        pygame.display.flip()
        delta_time = clock.tick(FPS) / 1000

def setup_state(settings: Settings) -> State:
    boids = create_boids(settings.count)
    state = State(boids=boids)
    return state

def main():
    pygame.init()
    pygame.display.set_caption("Boids")
    pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF | pygame.OPENGL)
    imgui.create_context()
    renderer = PygameRenderer()
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    io = imgui.get_io()
    io.display_size = SCREEN_SIZE
    clock = pygame.time.Clock()
    render(renderer, clock)
    pygame.quit()

