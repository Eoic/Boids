from __future__ import annotations

from dataclasses import dataclass, field

from pygame.math import Vector2

from boids.kdtree import KDTree, PointLike


@dataclass
class Boid(PointLike):
    color: tuple[float, float, float, float] | None = field(default=None)
    color_applied: bool = field(default=False)
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))

    def __getitem__(self, index: int) -> float:
        return self.position[index]

    def __eq__(self, value: Boid, /) -> bool:
        return self.position == value.position

@dataclass
class State:
    boids: KDTree[Boid]
    running: bool = field(default=True)
    goal_position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    goal_next_rotation: int = field(default=0)
    goal_alive: bool = field(default=False)
    allocated_colors: list[tuple[float, float, float, float]] = field(default=[])

