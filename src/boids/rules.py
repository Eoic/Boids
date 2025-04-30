from dataclasses import dataclass

from pygame.math import Vector2

from boids.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from boids.entities import Boid, State
from boids.settings import Settings


@dataclass(frozen=True)
class RuleContext:
    boid: Boid
    state: State
    settings: Settings

def cohesion(context: RuleContext):
    """
    Calculate velocity that moves the boid by 1/100th towards the center
    of the flock. The center is the average position of all the boids,
    not including itself.
    """
    center = Vector2(0, 0)

    for boid in context.state.boids:
        if boid == context.boid:
            continue

        center = center + boid.position

    boid_count = len(context.state.boids) - 1

    if boid_count > 0:
        center = center / boid_count

    return (center - context.boid.position) * (context.settings.cohesion / 100)

def separation(context: RuleContext):
    """
    Make sure boids do not collide with each other by checking whether
    each boid is withing a threshold distance, and if it is, moving it
    away by the distance between the current boid and the other.
    """
    center = Vector2(0, 0)

    for boid in context.state.boids:
        if boid == context.boid:
            continue

        if context.boid.position.distance_to(boid.position) < context.settings.separation:
            center = center - (boid.position - context.boid.position)

    return center

def alignment(context: RuleContext):
    """
    Find the average velocity of all the other boids
    and add 1/8th of if to the boid's current velocity.
    """
    center = Vector2(0, 0)

    for boid in context.state.boids:
        if boid == context.boid:
            continue

        center = center + boid.velocity

    boid_count = len(context.state.boids) - 1

    if boid_count > 0:
        center = center / boid_count

    return (context.boid.velocity - center) * (context.settings.alignment / 100)

def apply_wind(context: RuleContext):
    return context.settings.wind_direction

def limit_position(context: RuleContext):
    velocity = Vector2(0, 0)
    margin_top =context.settings.bound_top_left.y
    margin_left =context.settings.bound_top_left.x
    margin_bottom = SCREEN_HEIGHT -context.settings.bound_bottom_right.y
    margin_right = SCREEN_WIDTH -context.settings.bound_bottom_right.x

    if context.boid.position.x < margin_left:
        velocity.x =context.settings.turn_factor
    elif context.boid.position.x > SCREEN_WIDTH - margin_right:
        velocity.x = -context.settings.turn_factor

    if context.boid.position.y < margin_top:
        velocity.y =context.settings.turn_factor
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

