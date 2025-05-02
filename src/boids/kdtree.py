from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class PointLike(Protocol):
    def __getitem__(self, index: int) -> float: ...

T = TypeVar('T', bound=PointLike)

@dataclass
class KDNode(Generic[T]):
    data: T
    count: int = field(default=1)
    left: KDNode[T] | None = field(default=None)
    right: KDNode[T] | None = field(default=None)

class KDTree(Generic[T]):
    def __init__(self, dimensions: int):
        self.size: int = 0
        self.is_dirty = False
        self.dimensions: int = dimensions
        self.root: KDNode[T] = None

    def insert(self, point: T):
        self.is_dirty = True
        self.root = self._insert(point, self.root, 0)

    def remove(self, point: T):
        self.is_dirty = True
        self.root = self._remove(self.root, point, depth=0)

    def search(self, point: T) -> tuple[T, int] | None:
        needle = self._search(point, self.root, 0)

        if needle is None:
            return None

        return (needle.data, needle.count)

    def search_radius(self, query: T, radius: float) -> list[tuple[T, int]]:
        results: list[tuple[T, int]] = []
        self._search_radius(self.root, query, radius, 0, results)
        return results

    def display(self, node: KDNode[T]=None, depth: int=0):
        if node is None:
            node = self.root

        if node is None:
            print("(Empty tree)")
            return

        axis = depth % self.dimensions
        indent = "  " * depth
        print(f"{indent}|- {node.data} (axis={axis})")

        if node.left:
            self.display(node.left, depth + 1)

        if node.right:
            self.display(node.right, depth + 1)

    def _traverse(self, node: KDNode[T] | None):
        if node is None:
            return

        yield from self._traverse(node.left)

        for _ in range(node.count):
            yield node.data

        yield from self._traverse(node.right)

    def _search(self, point: T, node: KDNode[T] | None, depth: int) -> KDNode[T] | None:
        if node is None:
            return None

        if point == node.data:
            return node

        axis = depth % self.dimensions

        if point[axis] < node.data[axis]:
            return self._search(point, node.left, depth + 1)
        else:
            return self._search(point, node.right, depth + 1)

    def _find_min(self, node: KDNode[T], axis: int, depth: int=0):
        if node is None:
            return None

        current_axis = depth % self.dimensions

        if current_axis == axis:
            if node.left is None:
                return node

            return self._find_min(node.left, axis, depth + 1)
        else:
            left_min  = self._find_min(node.left, axis, depth + 1)
            right_min = self._find_min(node.right, axis, depth + 1)

            return min(
                [n for n in [node, left_min, right_min] if n is not None],
                key=lambda n: n.data[axis]
            )

    def _remove(self, node: KDNode[T], point: T, depth: int) -> KDNode[T]:
        if node is None:
            return None

        axis = depth % self.dimensions

        if point == node.data:
            if node.count > 1:
                node.count -= 1
                return node

            if node.right:
                min_node = self._find_min(node.right, axis, depth + 1)
                node.data = min_node.data
                node.count = min_node.count
                min_node.count = 1
                node.right = self._remove(node.right, min_node.data, depth + 1)
            elif node.left:
                min_node = self._find_min(node.left, axis, depth + 1)
                node.data = min_node.data
                node.count = min_node.count
                min_node.count = 1
                node.right = self._remove(node.left, min_node.data, depth + 1)
                node.left = None
            else:
                return None
        elif point[axis] < node.data[axis]:
            node.left = self._remove(node.left, point, depth + 1)
        else:
            node.right = self._remove(node.right, point, depth + 1)

        return node

    def _insert(self, point: T, node: KDNode[T] | None, dimension: int) -> KDNode[T]:
        if node is None:
            node = KDNode[T](data=point)
        elif point == node.data:
             node.count += 1
        elif point[dimension] < node.data[dimension]:
            node.left = self._insert(point, node.left, (dimension + 1) % self.dimensions)
        else:
            node.right = self._insert(point, node.right, (dimension + 1) % self.dimensions)

        return node

    def _search_radius(
        self,
        node: KDNode[T] | None,
        query: T,
        radius: float,
        depth: int,
        results: list[tuple[T, int]]
    ):
        if node is None:
            return

        axis = depth % self.dimensions
        data = node.data
        distance = sum((data[i] - query[i]) ** 2 for i in range(self.dimensions))

        if distance <= radius * radius:
            results.append((data, node.count))

        delta = abs(query[axis] - data[axis])
        args = [query, radius, depth + 1, results]

        if delta <= radius:
            self._search_radius(node.left, *args)
            self._search_radius(node.right, *args)
        elif delta < 0:
            self._search_radius(node.left, *args)
        else:
            self._search_radius(node.right, *args)

    def __iter__(self):
        yield from self._traverse(self.root)

    def __len__(self):
        if not self.is_dirty:
            return self.size

        count = 0

        for _ in self:
            count += 1

        self.size = count
        self.is_dirty = False

        return count

