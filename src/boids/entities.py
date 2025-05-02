from dataclasses import dataclass, field

from pygame.math import Vector2

from boids.kdtree import KDTree, PointLike


@dataclass
class Boid(PointLike):
    velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    position: Vector2 = field(default_factory=lambda: Vector2(0, 0))

    def __getitem__(self, index: int) -> float:
        return self.position[index]

@dataclass
class State:
    boids: KDTree[Boid]
    running: bool = field(default=True)
    goal_position: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    goal_next_rotation: int = field(default=0)
    goal_alive: bool = field(default=False)

