from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import Generic, Iterator, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class PointLike(Protocol):
    def __getitem__(self, index: int) -> float:
        raise NotImplementedError

    def __eq__(self, value: object, /) -> bool:
        raise NotImplementedError


T = TypeVar("T", bound=PointLike)


@dataclass
class GridCell(Generic[T]):
    items: list[T] = field(default_factory=list)


class SpatialGrid(Generic[T]):
    def __init__(self, dimensions: int, cell_size: float = 50.0):
        self.dimensions = dimensions
        self.cell_size = cell_size
        self.grid: dict[tuple[int, ...], GridCell[T]] = {}
        self.items: list[T] = []

    def _cell_coords(self, item: T) -> tuple[int, ...]:
        return tuple(int(item[d] // self.cell_size) for d in range(self.dimensions))

    def insert(self, item: T):
        coords = self._cell_coords(item)

        if coords not in self.grid:
            self.grid[coords] = GridCell()

        self.grid[coords].items.append(item)
        self.items.append(item)

    def remove(self, item: T):
        coords = self._cell_coords(item)

        if coords in self.grid:
            with contextlib.suppress(ValueError):
                self.grid[coords].items.remove(item)

        with contextlib.suppress(ValueError):
            self.items.remove(item)

    def search(self, item: T) -> T | None:
        coords = self._cell_coords(item)

        if coords in self.grid:
            for i in self.grid[coords].items:
                if i == item:
                    return i
        return None

    def search_radius(self, query: T, radius: float) -> list[T]:
        min_coords = [int((query[d] - radius) // self.cell_size) for d in range(self.dimensions)]
        max_coords = [int((query[d] + radius) // self.cell_size) for d in range(self.dimensions)]

        return [
            item
            for cell in self._iter_cells(min_coords, max_coords)
            if cell in self.grid
            for item in self.grid[cell].items
            if self._distance_sq(item, query) <= radius * radius
        ]

    def _distance_sq(self, a: T, b: T) -> float:
        return sum((a[d] - b[d]) ** 2 for d in range(self.dimensions))

    def _iter_cells(self, min_coords, max_coords):
        def recurse(dim, current_coords):
            if dim == self.dimensions:
                yield tuple(current_coords)
                return
            for coord in range(min_coords[dim], max_coords[dim] + 1):
                current_coords[dim] = coord
                yield from recurse(dim + 1, current_coords)

        yield from recurse(0, [0] * self.dimensions)
    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self):
        return len(self.items)
