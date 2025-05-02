
import math

from pygame.math import Vector2

from boids.kdtree import KDTree


def test_insert():
    tree = KDTree[Vector2](2)
    tree.insert(Vector2(1, -7))
    tree.insert(Vector2(1, -7))
    point, count = tree.search(Vector2(1, -7))
    assert point == Vector2(1, -7)
    assert count == 2

def test_delete():
    tree = KDTree[Vector2](2)
    tree.insert(Vector2(8, 2))
    tree.insert(Vector2(8, 2))
    tree.insert(Vector2(8, 2))
    assert tree.search(Vector2(8, 2))[1] == 3

    tree.delete(Vector2(8, 2))
    assert tree.search(Vector2(8, 2))[1] == 2

    tree.delete(Vector2(8, 2))
    assert tree.search(Vector2(8, 2))[1] == 1

    tree.delete(Vector2(8, 2))
    assert tree.search(Vector2(8, 2)) == None

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
    results_set = set(map(lambda item: (item[0].x, item[0].y, item[1]), results))
    expected_set = (set(map(lambda item: (item[0].x, item[0].y, 1), inside_points)))

    assert len(inside_points) == len(results)
    assert results_set == expected_set

