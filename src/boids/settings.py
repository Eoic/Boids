import sys
from dataclasses import dataclass, field

import imgui
from pygame.math import Vector2

from boids.constants import SCREEN_HEIGHT, SCREEN_WIDTH, TOP_MENU_HEIGHT


@dataclass
class Settings:
    # Boundary
    bound_top_left: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    bound_bottom_right: Vector2 = field(default_factory=lambda: Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))

    # Environment
    goal: bool = field(default=False)
    goal_strength: int = field(default=1)
    goal_duration_sec: int = field(default=5)
    wind_direction: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    wind_strength: int = field(default=0)

    # Boids
    count: int = field(default=300)
    speed: float = field(default=3.5)
    cohesion: int = field(default=10)
    alignment: int = field(default=50)
    separation_distance: int = field(default=50)
    separation_strength: float = field(default=50.0)
    max_speed: float = field(default=100)
    turn_factor: float = field(default=50)
    locality_radius: float = field(default=100)


def render_settings(settings: Settings) -> Settings:
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, _ = imgui.menu_item("Quit", "Cmd+Q", False, True)

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
        _, settings.bound_top_left.x = imgui.slider_float("X0", settings.bound_top_left.x, 0.0, SCREEN_WIDTH / 2)
        _, settings.bound_top_left.y = imgui.slider_float("Y0", settings.bound_top_left.y, 0.0, SCREEN_HEIGHT / 2)
        _, settings.bound_bottom_right.x = imgui.slider_float(
            "X1", settings.bound_bottom_right.x, SCREEN_WIDTH / 2, SCREEN_WIDTH
        )
        _, settings.bound_bottom_right.y = imgui.slider_float(
            "Y1", settings.bound_bottom_right.y, SCREEN_HEIGHT / 2, SCREEN_HEIGHT
        )
        imgui.tree_pop()
        imgui.spacing()

    if imgui.tree_node("Boids", flags=tree_node_flags):
        imgui.separator()
        _, settings.count = imgui.slider_int("Count", settings.count, 1, 1000)
        _, settings.speed = imgui.slider_float("Speed", settings.speed, 0.1, 10.0)
        _, settings.max_speed = imgui.slider_float("Max speed", settings.max_speed, 0, 100)
        _, settings.cohesion = imgui.slider_int("Cohesion, %", settings.cohesion, 1, 100)
        _, settings.alignment = imgui.slider_int("Alignment, %", settings.alignment, 1, 100)
        _, settings.separation_distance = imgui.slider_int("Separation distance", settings.separation_distance, 1, 100)
        _, settings.separation_strength = imgui.slider_int("Separation strength", settings.separation_strength, 1, 100)
        _, settings.turn_factor = imgui.slider_float("Turn factor", settings.turn_factor, 1, 75)
        _, settings.locality_radius = imgui.slider_float("Locality radius", settings.locality_radius, 5, 1000)
        imgui.tree_pop()
        imgui.spacing()

    if imgui.tree_node("Environment", flags=tree_node_flags):
        imgui.separator()
        imgui.text("Wind")
        _, settings.wind_direction.x = imgui.slider_float("X", settings.wind_direction.x, -1.0, 1.0)
        _, settings.wind_direction.y = imgui.slider_float("Y", settings.wind_direction.y, -1.0, 1.0)
        _, settings.wind_strength = imgui.slider_float("Strength", settings.wind_strength, 0.0, 100.0)
        _, settings.goal = imgui.checkbox("Random goal", settings.goal)

        if settings.goal:
            _, settings.goal_duration_sec = imgui.slider_int("Goal duration, s.", settings.goal_duration_sec, 1, 30)
            _, settings.goal_strength = imgui.slider_int("Goal strength, %", settings.goal_strength, 1, 100)

        imgui.tree_pop()
        imgui.spacing()

    clicked_reset = imgui.button("Reset Settings")

    if clicked_reset:
        settings = Settings()

    imgui.end()

    return settings
