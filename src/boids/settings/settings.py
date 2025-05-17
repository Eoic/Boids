import sys
from copy import deepcopy
from typing import Any

import imgui
from pygame import Vector2

from boids.constants import TOP_MENU_HEIGHT
from boids.settings.spec import spec

# @dataclass
# class Settings:
#     # Boundary
#     bound_top_left: Vector2 = field(default_factory=lambda: Vector2(0, 0))
#     bound_bottom_right: Vector2 = field(default_factory=lambda: Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))

#     # Environment
#     goal: bool = field(default=False)
#     goal_strength: int = field(default=1)
#     goal_duration_sec: int = field(default=5)
#     wind_direction: Vector2 = field(default_factory=lambda: Vector2(0, 0))
#     wind_strength: int = field(default=0)

#     # Boids
#     count: int = field(default=300)
#     speed: float = field(default=3.5)
#     cohesion: int = field(default=10)
#     alignment: int = field(default=50)
#     separation_distance: int = field(default=50)
#     separation_strength: float = field(default=50.0)
#     max_speed: float = field(default=100)
#     turn_factor: float = field(default=50)
#     locality_radius: float = field(default=100)
#     is_dirty: bool = field(default=True)


# def build_settings() -> dict:
#     settings = deepcopy(spec)

# for item in spec:
#     for key, desc in item["section"].items():
#         match desc["type"]:
#             case "Vector2":
#                 for axis in ["x", "y"]:
#                     settings[key][axis] = desc[axis]["default"]
#             case "float" | "int" | "bool":
#                 settings[key] = desc["default"]
#             case _:
#                 raise ValueError("Unknown setting type.")

# return settings


class Settings:
    def __init__(self):
        self._settings = deepcopy(spec)

    def get(self, section: str, field: str):
        field = self._settings[section]["fields"][field]
        field_type = field["type"]

        match field["type"]:
            case "Vector2":
                return Vector2(field["x"]["value"], field["y"]["value"])
            case _:
                return field["value"]

    def set(self, section: str, field: str):
        pass


def load_settings() -> dict:
    return deepcopy(spec)


def is_setting_visible(settings, section_key, key):
    is_visible = True
    condition_path = settings[section_key]["fields"][key].get("condition")

    if condition_path:
        current = settings
        tokens = condition_path.split(".")

        for token in tokens:
            current = current.get(token, {})

        if isinstance(current, bool):
            is_visible &= current

    return is_visible


def render_settings(settings: dict) -> dict:
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

    for section_key, node in spec.items():
        if imgui.tree_node(node["title"], flags=tree_node_flags):
            imgui.separator()

            for key, value in node["fields"].items():
                is_visible = is_setting_visible(settings, section_key, key)

                if not is_visible:
                    continue

                match value["type"]:
                    case "Vector2":
                        for axis in ["x", "y"]:
                            _, settings[section_key]["fields"][key][axis]["value"] = imgui.slider_float(
                                value[axis]["title"],
                                settings[section_key]["fields"][key][axis]["value"],
                                settings[section_key]["fields"][key][axis]["min"],
                                settings[section_key]["fields"][key][axis]["max"],
                            )
                    case "int":
                        _, settings[section_key]["fields"][key]["value"] = imgui.slider_int(
                            value["title"],
                            settings[section_key]["fields"][key]["value"],
                            settings[section_key]["fields"][key]["min"],
                            settings[section_key]["fields"][key]["max"],
                        )
                    case "float":
                        _, settings[section_key]["fields"][key]["value"] = imgui.slider_float(
                            value["title"],
                            settings[section_key]["fields"][key]["value"],
                            settings[section_key]["fields"][key]["min"],
                            settings[section_key]["fields"][key]["max"],
                        )
                    case "bool":
                        _, settings[section_key]["fields"][key]["value"] = imgui.checkbox(
                            value["title"],
                            settings[section_key]["fields"][key]["value"],
                        )
                    case _:
                        raise ValueError("Unknown setting type.")

            imgui.tree_pop()
            imgui.spacing()

    clicked_reset = imgui.button("Reset Settings")

    if clicked_reset:
        settings = build_settings()

    # if settings.is_dirty:
    #     save_settings(settings)

    imgui.end()

    return settings
