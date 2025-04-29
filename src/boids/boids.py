import math
import os
import random
import sys
from dataclasses import dataclass, field

import imgui
import OpenGL.GL as gl
import pygame
from imgui.integrations.pygame import PygameRenderer
from pygame import Vector2

FPS = 60
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
TOP_MENU_HEIGHT = 19

os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"

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

def set_orthographic_projection(width: int, height: int):
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, width, height, 0, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

def draw_filled_rect(x: float, y: float, width: float, height: float, color: tuple[float, float, float]):
    gl.glColor3f(*color)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x + width, y)
    gl.glVertex2f(x + width, y + height)
    gl.glVertex2f(x, y + height)
    gl.glEnd()

def draw_rect_outline(top_left: Vector2, bottom_right: Vector2, color: tuple[float, float, float], line_width: float = 1.0):
    gl.glLineWidth(line_width)
    gl.glColor3f(*color)
    gl.glBegin(gl.GL_LINE_LOOP)
    gl.glVertex2f(top_left.x, top_left.y + TOP_MENU_HEIGHT)
    gl.glVertex2f(bottom_right.x, top_left.y + TOP_MENU_HEIGHT)
    gl.glVertex2f(*bottom_right.xy)
    gl.glVertex2f(top_left.x, bottom_right.y)
    gl.glEnd()

@dataclass
class Boid:
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))

@dataclass
class State:
    boids: list[Boid]
    goal_position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    goal_next_rotation: int = field(default=0)
    goal_alive: bool = field(default=False)

@dataclass
class Settings:
    # Boundary
    cage_top_left: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    cage_bottom_right: Vector2 = field(default_factory=lambda: Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
    # Environment
    goal: bool = field(default=False)
    goal_strength: int = field(default=1)
    goal_duration_sec: bool = field(default=15)
    # Boids
    boid_count: int = field(default=50)
    boid_speed: float = field(default=2.5)
    center_mass_strength: int = field(default=1)
    avg_velocity_strength: int = field(default=8)
    separation_threshold: int = field(default=35)

def rule_one(target_boid: Boid, boids: list[Boid], settings: Settings):
    """
    Calculate velocity that moves the boid by 1/100th towards the center
    of the flock. The center is the average position of all the boids,
    not including itself.
    """
    center = Vector2(0, 0)

    for boid in boids:
        if boid == target_boid:
            continue

        center = center + boid.position

    center = center / (len(boids) - 1)
    return (center - target_boid.position) * (settings.center_mass_strength / 100)

def rule_two(target_boid: Boid, boids: list[Boid], settings: Settings):
    """
    Make sure boids do not collide with each other by checking whether
    each boid is withing a threshold distance, and if it is, moving it
    away by the distance between the current boid and the other.
    """
    center = Vector2(0, 0)

    for boid in boids:
        if boid == target_boid:
            continue

        if target_boid.position.distance_to(boid.position) < settings.separation_threshold:
            center = center - (boid.position - target_boid.position)

    return center

def rule_three(target_boid: Boid, boids: list[Boid], settings: Settings):
    """
    Find the average velocity of all the other boids
    and add 1/8th of if to the boid's current velocity.
    """
    center = Vector2(0, 0)

    for boid in boids:
        if boid == target_boid:
            continue

        center = center + boid.velocity

    center = center / (len(boids) - 1)
    return (target_boid.velocity - center) * (settings.avg_velocity_strength / 100)

def apply_wind(_boid: Boid):
        return Vector2(0, 0)

def constrain_position(boid: Boid, settings: Settings, turn_factor: float = 50):
    velocity = Vector2(0, 0)
    margin_top = settings.cage_top_left.y
    margin_left = settings.cage_top_left.x
    margin_bottom = SCREEN_HEIGHT - settings.cage_bottom_right.y
    margin_right = SCREEN_WIDTH - settings.cage_bottom_right.x

    if boid.position.x < margin_left:
        velocity.x = turn_factor
    elif boid.position.x > SCREEN_WIDTH - margin_right:
        velocity.x = -turn_factor

    if boid.position.y < margin_top:
        velocity.y = turn_factor
    elif boid.position.y > SCREEN_HEIGHT - margin_bottom:
        velocity.y = -turn_factor

    return velocity

def pull_towards_goal(boid: Boid, goal: Vector2):
    return (goal - boid.position) / 100

def limit_velocity(boid: Boid, max_speed: float = 100):
    if boid.velocity.length() > max_speed:
        return boid.velocity.normalize() * max_speed

    return boid.velocity

def create_boids(count: int) -> list[Boid]:
    boids: list[Boid] = []

    for _ in range(count):
        boid = Boid()

        boid.position.update(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )

        boids.append(boid)

    return boids

def update_goal(state: State, settings: Settings):
    if settings.goal:
        if not state.goal_alive:
            state.goal_position = Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

        state.goal_next_rotation = pygame.time.get_ticks() + settings.goal_duration_sec * 1000
        state.goal_alive = True

        if pygame.time.get_ticks() - state.goal_next_rotation >= 0:
            state.goal_position = Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
    elif state.goal_alive:
        state.goal_alive = False

def update_boids(boids: list[Boid], settings: Settings, delta_time: float):
    for boid in boids:
        v1 = rule_one(boid, boids, settings)
        v2 = rule_two(boid, boids, settings)
        v3 = rule_three(boid, boids, settings)
        v4 = apply_wind(boid)
        vn = constrain_position(boid, settings)
        boid.velocity += v1 + v2 + v3 + v4 + vn
        boid.velocity = limit_velocity(boid)
        boid.position += (boid.velocity * settings.boid_speed * delta_time)

def render_settings(settings: Settings) -> Settings:
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)

            if clicked_quit:
                sys.exit(0)

            imgui.end_menu()

        imgui.end_main_menu_bar()

    imgui.set_next_window_position(10, 12 + TOP_MENU_HEIGHT)
    imgui.set_next_window_size(0, 0)
    imgui.begin("Settings", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)
    tree_node_flags = imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_FRAME_PADDING

    if imgui.tree_node("Boundary", flags=tree_node_flags):
        imgui.separator()
        _changed, settings.cage_top_left.x = imgui.slider_float("X0", settings.cage_top_left.x, 0.0, SCREEN_WIDTH / 2)
        _changed, settings.cage_top_left.y = imgui.slider_float("Y0", settings.cage_top_left.y, 0.0, SCREEN_HEIGHT/ 2)
        _changed, settings.cage_bottom_right.x = imgui.slider_float("X1", settings.cage_bottom_right.x, SCREEN_WIDTH / 2, SCREEN_WIDTH)
        _changed, settings.cage_bottom_right.y = imgui.slider_float("Y1", settings.cage_bottom_right.y, SCREEN_HEIGHT / 2, SCREEN_HEIGHT)
        imgui.tree_pop()
        imgui.spacing()

    if imgui.tree_node("Boids", flags=tree_node_flags):
        imgui.separator()
        _changed, settings.boid_count = imgui.slider_int("Boid count", settings.boid_count, 1, 1000)
        _changed, settings.boid_speed = imgui.slider_float("Boid speed", settings.boid_speed, 0.1, 10.0)
        _changed, settings.center_mass_strength = imgui.slider_int("Center of mass strength, %", settings.center_mass_strength, 1, 100)
        _changed, settings.avg_velocity_strength = imgui.slider_int("Average velocity strength, %", settings.avg_velocity_strength, 1, 100)
        _changed, settings.separation_threshold = imgui.slider_int("Separation threshold dist.", settings.separation_threshold, 1, 100)
        imgui.tree_pop()
        imgui.spacing()

    if imgui.tree_node("Environment", flags=tree_node_flags):
        imgui.separator()
        changed, settings.goal = imgui.checkbox("Random goal", settings.goal)

        if settings.goal:
            _changed, settings.goal_duration_sec = imgui.slider_int("Goal duration, s.", settings.goal_duration_sec, 1, 30)
            _changed, settings.goal_strength = imgui.slider_int("Goal strength, %", settings.goal_strength, 1, 100)

        imgui.tree_pop()
        imgui.spacing()

    clicked_reset = imgui.button("Reset Settings")

    if clicked_reset:
        settings = Settings()

    imgui.end()

    return settings

def render(_screen: pygame.Surface, impl: PygameRenderer, clock: pygame.time.Clock):
    settings = Settings()
    state = setup_state(settings)
    is_running = True
    delta_time = 0

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            impl.process_event(event)

        impl.process_inputs()
        imgui.new_frame()

        settings = render_settings(settings)
        update_boids(state.boids, settings, delta_time)

        gl.glClearColor(0.08, 0.1, 0.12, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        set_orthographic_projection(SCREEN_WIDTH, SCREEN_HEIGHT)

        for boid in state.boids:
            draw_circle(boid.position, 5, (0.86, 0.08, 0.24, 1.0))

        draw_rect_outline(settings.cage_top_left, settings.cage_bottom_right, (0.53, 0.01, 0.2), line_width=2.0)

        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()
        delta_time = clock.tick(FPS) / 1000

def setup_state(settings: Settings) -> State:
    boids = create_boids(settings.boid_count)
    state = State(boids=boids)
    return state

def main():
    pygame.init()
    pygame.display.set_caption("Boids")
    screen = pygame.display.set_mode(SIZE, pygame.DOUBLEBUF | pygame.OPENGL)
    imgui.create_context()
    impl = PygameRenderer()
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    io = imgui.get_io()
    io.display_size = SIZE
    clock = pygame.time.Clock()
    render(screen, impl, clock)
    pygame.quit()

