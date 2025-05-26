from __future__ import annotations

from dataclasses import dataclass, field
import contextlib
from typing import Generic, Protocol, TypeVar, runtime_checkable, Iterator


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
        # Only 2D supported for now
        DIM_2D = 2
        if self.dimensions == DIM_2D:
            for x in range(min_coords[0], max_coords[0] + 1):
                for y in range(min_coords[1], max_coords[1] + 1):
                    yield (x, y)
        else:
            raise NotImplementedError("Only 2D supported for now.")

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self):
        return len(self.items)
