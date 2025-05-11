from boids.constants import SCREEN_HEIGHT, SCREEN_WIDTH

blueprint = {
    "Boundary": {
        "bound_top_left": {
            "type": "Vector2",
            "x": {
                "title": "X0",
                "type": "float",
                "min": 0.0,
                "max": SCREEN_WIDTH / 2,
                "default": 0.0,
            },
            "y": {
                "title": "Y0",
                "type": "float",
                "min": 0.0,
                "max": SCREEN_HEIGHT / 2,
                "default": 0.0,
            },
        },
        "bound_bottom_right": {
            "type": "Vector2",
            "x": {
                "title": "X1",
                "type": "float",
                "min": SCREEN_WIDTH / 2,
                "max": SCREEN_WIDTH,
                "default": SCREEN_WIDTH,
            },
            "y": {
                "title": "Y1",
                "type": "float",
                "min": SCREEN_HEIGHT / 2,
                "max": SCREEN_HEIGHT,
                "default": SCREEN_HEIGHT,
            },
        },
    },
    "Boids": {
        "count": {
            "title": "Count",
            "type": "int",
            "min": 1,
            "max": 1000,
            "default": 300,
        },
        "speed": {
            "title": "Speed",
            "type": "float",
            "min": 0.1,
            "max": 10.0,
            "default": 3.5,
        },
        "max_speed": {
            "title": "Max speed",
            "type": "float",
            "min": 0,
            "max": 100,
            "default": 100.0,
        },
        "cohesion": {
            "title": "Cohesion, %",
            "type": "int",
            "min": 1,
            "max": 100,
            "default": 10,
        },
        "alignment": {
            "title": "Alignment, %",
            "type": "int",
            "min": 1,
            "max": 100,
            "default": 50,
        },
        "separation_distance": {
            "title": "Separation distance",
            "type": "int",
            "min": 1,
            "max": 100,
            "default": 50,
        },
        "separation_strength": {
            "title": "Separation strength",
            "type": "int",
            "min": 1,
            "max": 100,
            "default": 50,
        },
        "turn_factor": {
            "title": "Turn factor",
            "type": "float",
            "min": 1,
            "max": 75,
            "default": 50.0,
        },
        "locality_radius": {
            "title": "Locality radius",
            "type": "float",
            "min": 5,
            "max": 1000,
            "default": 100.0,
        },
    },
    "Environment": {
        "wind_direction": {
            "type": "Vector2",
            "x": {
                "title": "Wind X",
                "type": "float",
                "min": -1.0,
                "max": 1.0,
                "default": 0.0,
            },
            "y": {
                "title": "Wind Y",
                "type": "float",
                "min": -1.0,
                "max": 1.0,
                "default": 0.0,
            },
        },
        "wind_strength": {
            "title": "Wind Strength",
            "type": "float",
            "min": 0.0,
            "max": 100.0,
            "default": 0.0,
        },
        "goal": {
            "enabled": {
                "title": "Random goal",
                "type": "bool",
                "default": False,
            },
            "goal_duration_sec": {
                "title": "Goal duration, s.",
                "type": "int",
                "min": 1,
                "max": 30,
                "default": 5,
            },
            "goal_strength": {
                "title": "Goal strength, %",
                "type": "int",
                "min": 1,
                "max": 100,
                "default": 1,
            },
        },
    },
}
