
import math

from pygame.math import Vector2

from boids.kdtree import KDTree


def test_range_search():
    radius = 5
    points = []
    tree = KDTree(2)
    query = Vector2(3, -2)
    origin = Vector2(query.x - radius, query.y + radius)

    for x in range(radius * 2 + 1):
        for y in range(radius * 2 + 1):
            point = Vector2(origin.x + x, origin.y - y)
            is_inside = math.sqrt((point.x - query.x) ** 2 + (point.y - query.y) ** 2) <= radius
            points.append((point, is_inside))
            tree.insert(point)

    inside_points = list(filter(lambda item: item[1], points))
    results = tree.search(query, radius)
    results_set = set(map(lambda item: (item.x, item.y,), results))
    reference_set = (set(map(lambda item: (item[0].x, item[0].y), inside_points)))
    assert len(inside_points) == len(results)
    assert results_set == reference_set

