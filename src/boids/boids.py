import random
from dataclasses import dataclass, field

import pygame

FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

@dataclass
class Boid:
    velocity: pygame.math.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    position: pygame.math.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))

def rule_one(target_boid: Boid, boids: list[Boid]):
    """
    Calculate velocity that moves the boid by 1/100th towards the center
    of the flock. The center is the average position of all the boids,
    not including itself.
    """
    center: pygame.Vector2 = pygame.Vector2(0, 0)

    for boid in boids:
        if boid == target_boid:
            continue

        center = center + boid.position

    center = center / (len(boids) - 1)
    return (center - target_boid.position) / 100

def rule_two(target_boid: Boid, boids: list[Boid], threshold: int = 100):
    """
    Make sure boids do not collide with each other by checking whether
    each boid is withing a threshold distance, and if it is, moving it
    away by the distance between the current boid and the other.
    """
    center: pygame.Vector2 = pygame.Vector2(0, 0)

    for boid in boids:
        if boid == target_boid:
            continue

        if target_boid.position.distance_to(boid.position) < threshold:
            center = center - (boid.position - target_boid.position)

    return center

def rule_three(target_boid: Boid, boids: list[Boid]):
    """
    Find the average velocity of all the other boids
    and add 1/8th of if to the boid's current velocity.
    """
    center: pygame.Vector2 = pygame.Vector2(0, 0)

    for boid in boids:
        if boid == target_boid:
            continue

        center = center + boid.velocity

    center = center / (len(boids) - 1)
    return (target_boid.velocity - center) / 8

def setup_boids(count: int) -> list[Boid]:
    boids: list[Boid] = []

    for _ in range(count):
        boid = Boid()

        boid.position.update(
            random.randint(0, SCREEN_WIDTH),
            random.randint(0, SCREEN_HEIGHT)
        )

        boids.append(boid)

    return boids

def update_boids(boids: list[Boid]):
    for boid in boids:
        v1 = rule_one(boid, boids)
        v2 = rule_two(boid, boids)
        v3 = rule_three(boid, boids)
        boid.velocity = boid.velocity + v1 + v2 + v3
        boid.position = boid.position + boid.velocity

def render(boids: list[Boid], screen: pygame.Surface, clock: pygame.time.Clock):
    is_running = True
    delta_time = 0

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        screen.fill(color="gray")

        for boid in boids:
            pygame.draw.circle(screen, "red", boid.position, 10)

        update_boids(boids)
        pygame.display.flip()
        delta_time = clock.tick(FPS) / 1000

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    boids = setup_boids(1000)
    render(boids, screen, clock)
    pygame.quit()

