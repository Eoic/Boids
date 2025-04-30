from dataclasses import dataclass, field

from pygame.math import Vector2


@dataclass
class Boid:
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))

@dataclass
class State:
    boids: list[Boid]
    running: bool = field(default=True)
    goal_position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    goal_next_rotation: int = field(default=0)
    goal_alive: bool = field(default=False)

