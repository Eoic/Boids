from dataclasses import dataclass

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

    if not context.neighbors:
        return center

    for boid in context.neighbors:
        center += boid.position

    center /= len(context.neighbors)

    return (center - context.boid.position) * (context.settings.cohesion / 100)


def separation(context: RuleContext):
    """
    For each neighbor closer than `settings.separation`, compute
    a unit vector pointing away from it, sum them up, and finally
    scale by settings.separation_strength.
    """
    center = Vector2(0, 0)
    radius = context.settings.separation_distance

    for other in context.neighbors:
        offset = context.boid.position - other.position
        distance = offset.length()

        if 0 < distance < radius:
            center += offset.normalize() * ((radius - distance) / radius)

    return center * context.settings.separation_strength


def alignment(context: RuleContext):
    """
    Find the average velocity of all the other boids
    and add a fraction of it to the boid's current velocity.
    """
    center = Vector2(0, 0)

    if not context.neighbors:
        return center

    for boid in context.neighbors:
        center += boid.velocity

    center /= len(context.neighbors)

    return (center - context.boid.velocity) * (context.settings.alignment / 100)


def apply_wind(context: RuleContext):
    if context.settings.wind_direction.length() > 0:
        return context.settings.wind_direction.normalize() * context.settings.wind_strength

    return context.settings.wind_direction


def limit_position(context: RuleContext):
    velocity = Vector2(0, 0)
    margin_top = context.settings.bound_top_left.y
    margin_left = context.settings.bound_top_left.x
    margin_bottom = SCREEN_HEIGHT - context.settings.bound_bottom_right.y
    margin_right = SCREEN_WIDTH - context.settings.bound_bottom_right.x

    if context.boid.position.x < margin_left:
        velocity.x = context.settings.turn_factor
    elif context.boid.position.x > SCREEN_WIDTH - margin_right:
        velocity.x = -context.settings.turn_factor

    if context.boid.position.y < margin_top:
        velocity.y = context.settings.turn_factor
    elif context.boid.position.y > SCREEN_HEIGHT - margin_bottom:
        velocity.y = -context.settings.turn_factor

    return velocity


def chase_goal(context: RuleContext):
    if not context.state.goal_alive:
        return Vector2(0, 0)

    return (context.state.goal_position - context.boid.position) * (context.settings.goal_strength / 100)


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
