import json
import os
import sys
from copy import deepcopy
from json import JSONDecodeError
from typing import Literal

import imgui

from boids.constants import TOP_MENU_HEIGHT
from boids.settings.schema import schema


class Settings:
    def __init__(self):
        self._settings: dict = deepcopy(schema)

    def get(self, section: str, field: str) -> int | float | bool | tuple[float, float]:
        field_data: dict | None = self._settings.get(section, {}).get("fields", {}).get(field, None)

        if field_data is None:
            raise KeyError(f"Setting '{section}.{field}' does not exist.")

        field_type = field_data.get("type", None)

        if field_type is None:
            raise ValueError("Setting field does not have a specified type.")

        match field_type:
            case "Vector2":
                return (field_data["x"]["value"], field_data["y"]["value"])
            case _:
                return field_data["value"]

    def get_field(self, section: str, field: str):
        field_data: dict | None = self._settings.get(section, {}).get("fields", {}).get(field, None)

        if field_data is None:
            raise KeyError(f"Setting '{section}.{field}' does not exist.")

        return field_data

    def set(self, section: str, field: str, value: float | int | bool | tuple[float, float]):
        if isinstance(value, (tuple, list)):
            self._settings[section]["fields"][field]["x"]["value"] = value[0]
            self._settings[section]["fields"][field]["y"]["value"] = value[1]
        else:
            self._settings[section]["fields"][field]["value"] = value

    def is_setting_enabled(self, section: str, field: str):
        is_enabled = True
        condition_path = self._settings[section]["fields"][field].get("condition")

        if condition_path:
            current = self._settings
            tokens = condition_path.split(".")

            for token in tokens:
                current = current.get(token, {})

            if isinstance(current, bool):
                is_enabled &= current

        return is_enabled

    def dump_dict(self) -> dict:
        dict_settings = {}

        for section, section_data in self._settings.items():
            dict_settings[section] = {}

            if section.startswith("_"):
                dict_settings[section] = section_data
                continue

            for field, field_data in section_data["fields"].items():
                match field_data["type"]:
                    case "Vector2":
                        axes = [field_data[axis]["value"] for axis in ["x", "y"]]
                        dict_settings[section][field] = (axes[0], axes[1])
                    case _:
                        dict_settings[section][field] = field_data["value"]

        return dict_settings

    def load_dict(self, data: dict):
        for section, section_data in data.items():
            for field, field_data in section_data.items():
                self.set(section, field, field_data)

    @staticmethod
    def get_slider(value_type: Literal["int", "float"]):
        match value_type:
            case "int":
                return imgui.slider_int
            case "float":
                return imgui.slider_float
            case _:
                raise ValueError("Unknown type.")

def load_settings() -> Settings:
    if os.path.exists("settings.json"):
        with open("settings.json") as file:
            settings = Settings()

            try:
                settings_dict = json.load(file)
            except JSONDecodeError:
                print("Could not load settings from a file - file is invalid.")
                settings_dict = {}

            settings.load_dict(settings_dict)
            return settings

    return Settings()


def save_settings(settings: Settings):
    with open("settings.json", "w") as file:
        json.dump(settings.dump_dict(), file, indent=4)


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
    is_dirty = False

    for section, section_data in schema.items():
        if section.startswith("_"):
            continue

        if imgui.tree_node(section_data["title"], flags=tree_node_flags):
            imgui.separator()

            for field, value in section_data["fields"].items():
                is_enabled = settings.is_setting_enabled(section, field)

                if not is_enabled:
                    continue

                field_data = settings.get_field(section, field)

                match value["type"]:
                    case "Vector2":
                        axes = []

                        for axis in ["x", "y"]:
                            dirty, axis_value = imgui.slider_float(
                                value[axis]["title"],
                                field_data[axis]["value"],
                                field_data[axis]["min"],
                                field_data[axis]["max"],
                            )

                            axes.append(axis_value)
                            is_dirty |= dirty

                        settings.set(section, field, (axes[0], axes[1]))
                    case "int" | "float":
                        dirty, setting_value = Settings.get_slider(value["type"])(
                            value["title"],
                            field_data["value"],
                            field_data["min"],
                            field_data["max"],
                        )

                        is_dirty |= dirty
                        settings.set(section, field, setting_value)
                    case "bool":
                        dirty, setting_value = imgui.checkbox(value["title"], field_data["value"])
                        is_dirty |= dirty
                        settings.set(section, field, setting_value)
                    case _:
                        raise ValueError("Unknown setting type.")

            imgui.tree_pop()
            imgui.spacing()

    clicked_reset = imgui.button("Reset Settings")

    if clicked_reset:
        settings = Settings()
        is_dirty = True

    if is_dirty:
        save_settings(settings)

    imgui.end()

    return settings
