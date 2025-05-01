from __future__ import annotations

from dataclasses import dataclass, field

from pygame.math import Vector2


@dataclass
class KDNode:
    data: Vector2
    left: KDNode | None = field(default=None)
    right: KDNode | None = field(default=None)

class KDTree:
    def __init__(self, dimensions: int):
        self.dimensions: int = dimensions
        self.root: KDNode = None

    def insert(self, point: Vector2) -> KDNode:
        self.root = self._insert(point, self.root, 0)

    def _insert(self, point: Vector2, node: KDNode | None, dimension: int) -> KDNode:
        if node is None:
            node = KDNode(data=point)
        elif (point[dimension] < node.data[dimension]):
            node.left = self._insert(point, node.left, (dimension + 1) % self.dimensions)
        else:
            node.right = self._insert(point, node.right, (dimension + 1) % self.dimensions)

        return node

    def display(self, node=None, depth=0):
        if node is None:
            node = self.root

        if node is None:
            print("(Empty tree)")
            return

        axis = depth % self.dimensions
        indent = "  " * depth
        print(f"{indent}|- {node.data} (axis={axis})")

        if node.left:
            self.display(node.left,  depth + 1)

        if node.right:
            self.display(node.right, depth + 1)

