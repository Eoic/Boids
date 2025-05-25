from dataclasses import dataclass
from typing import cast

from pygame.math import Vector2

from boids.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from boids.entities import Boid, State
from boids.settings.settings import Settings


@dataclass(frozen=True)
class RuleContext:
    boid: Boid
    neighbors: list[Boid]
    state: State
    settings: Settings


def cohesion(context: RuleContext):
    """
    Calculate velocity that moves the boid by a fraction towards the center
    of the flock. The center is the average position of all the boids,
    not including itself.
    """

    center = Vector2(0, 0)
    cohesion_strength = cast(int, context.settings.get("boids", "cohesion"))

    if not context.neighbors:
        return center

    for boid in context.neighbors:
        center += boid.position

    center /= len(context.neighbors)

    return (center - context.boid.position) * (cohesion_strength / 100)


def separation(context: RuleContext):
    """
    For each neighbor closer than `settings.separation`, compute
    a unit vector pointing away from it, sum them up, and finally
    scale by settings.separation_strength.
    """
    center = Vector2(0, 0)
    radius = cast(int, context.settings.get("boids", "separation_distance"))
    strength = cast(int, context.settings.get("boids", "separation_strength"))

    for other in context.neighbors:
        offset = context.boid.position - other.position
        distance = offset.length()

        if 0 < distance < radius:
            center += offset.normalize() * ((radius - distance) / radius)

    return center * strength


def alignment(context: RuleContext):
    """
    Find the average velocity of all the other boids
    and add a fraction of it to the boid's current velocity.
    """
    center = Vector2(0, 0)

    if not context.neighbors:
        return center

    alignment_strength = cast(int, context.settings.get("boids", "alignment"))

    for boid in context.neighbors:
        center += boid.velocity

    center /= len(context.neighbors)

    return (center - context.boid.velocity) * (alignment_strength / 100)


def apply_wind(context: RuleContext):
    wind_direction_raw = cast(tuple, context.settings.get("environment", "wind_direction"))
    wind_direction = Vector2(wind_direction_raw[0], wind_direction_raw[1])
    wind_strength = cast(float, context.settings.get("environment", "wind_strength"))

    if wind_direction.length() > 0:
        return wind_direction.normalize() * wind_strength

    return wind_direction


def limit_position(context: RuleContext):
    velocity = Vector2(0, 0)

    if not context.settings.get("boundary", "enabled"):
        context.boid.position.x %= SCREEN_WIDTH
        context.boid.position.y %= SCREEN_HEIGHT
        return velocity

    top_left = cast(tuple, context.settings.get("boundary", "top_left"))
    bottom_right = cast(tuple, context.settings.get("boundary", "bottom_right"))
    turn_factor = cast(float, context.settings.get("boids", "turn_factor"))
    margin_top = top_left[1]
    margin_left = top_left[0]
    margin_right = SCREEN_WIDTH - bottom_right[0]
    margin_bottom = SCREEN_HEIGHT - bottom_right[1]

    if context.boid.position.x < margin_left:
        velocity.x = turn_factor
    elif context.boid.position.x > SCREEN_WIDTH - margin_right:
        velocity.x = -turn_factor

    if context.boid.position.y < margin_top:
        velocity.y = turn_factor
    elif context.boid.position.y > SCREEN_HEIGHT - margin_bottom:
        velocity.y = -turn_factor

    return velocity


def chase_goal(context: RuleContext):
    if not context.state.goal_alive:
        return Vector2(0, 0)

    goal_strength = cast(int, context.settings.get("goal", "strength"))
    return (context.state.goal_position - context.boid.position) * (goal_strength / 100)


rules = [
    cohesion,
    separation,
    alignment,
    apply_wind,
    chase_goal,
    limit_position,
]


def evaluate_rules(context: RuleContext) -> Vector2:
    velocity = Vector2(0, 0)

    for rule in rules:
        velocity += rule(context)

    return velocity
