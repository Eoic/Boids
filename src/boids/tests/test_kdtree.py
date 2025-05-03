from __future__ import annotations

import math
from dataclasses import dataclass

from pygame.math import Vector2

from boids.kdtree import KDTree, PointLike


@dataclass
class Entity(PointLike):
    position: Vector2

    def __getitem__(self, index: int) -> float:
        return self.position[index]

    def __eq__(self, value: Entity, /) -> bool:
        return self.position == value.position

def test_insert():
    tree = KDTree[Vector2](2)
    tree.insert(Entity(Vector2(1, -7)))
    tree.insert(Entity(Vector2(1, -7)))
    item = tree.search(item=Entity(Vector2(1, -7)))
    assert item == Entity(Vector2(1, -7))

def test_iter_duplicate():
    count = 5
    tree_count = 0
    tree = KDTree[Vector2](2)

    for _ in range(count):
        tree.insert(Entity(Vector2(1, 5)))

    for item in tree:
        tree_count += 1
        assert item == Entity(Vector2(1, 5))

    assert tree_count == count

def test_len():
    tree = KDTree[Vector2](2)

    for _ in range(5):
        tree.insert(Entity(Vector2(1, 2)))

    for _ in range(5):
        tree.insert(Entity(Vector2(2, 1)))

    assert len(tree) == 10

def test_remove():
    tree = KDTree[Vector2](2)
    tree.insert(Entity(Vector2(8, 2)))
    tree.insert(Entity(Vector2(8, 2)))
    tree.insert(Entity(Vector2(8, 2)))
    assert tree.search(Entity(Vector2(8, 2))) == Entity(Vector2(8, 2))

    tree.remove(Entity(Vector2(8, 2)))
    assert tree.search(Entity(Vector2(8, 2))) == Entity(Vector2(8, 2))

    tree.remove(Entity(Vector2(8, 2)))
    assert tree.search(Entity(Vector2(8, 2))) == Entity(Vector2(8, 2))

    tree.remove(Entity(Vector2(8, 2)))
    assert tree.search(Entity(Vector2(8, 2))) == None

def test_range_search_unique():
    radius = 5
    points = []
    tree = KDTree[Vector2](2)
    query = Vector2(3, -2)
    origin = Vector2(query.x - radius, query.y + radius)

    for x in range(radius * 2 + 1):
        for y in range(radius * 2 + 1):
            point = Vector2(origin.x + x, origin.y - y)
            is_inside = math.sqrt((point.x - query.x) ** 2 + (point.y - query.y) ** 2) <= radius
            points.append((point, is_inside))
            tree.insert(point)

    inside_points = list(filter(lambda item: item[1], points))
    results = tree.search_radius(query, radius)
    results_set = set(map(lambda item: (item.x, item.y), results))
    expected_set = (set(map(lambda item: (item[0].x, item[0].y), inside_points)))

    assert len(inside_points) == len(results)
    assert results_set == expected_set

