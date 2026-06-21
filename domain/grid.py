"""Игровая сетка - модель уровня."""
from enum import Enum


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    FLOOR = 2
    EXIT = 3
    COIN = 4
    NOISE_SOURCE = 5


class Grid:
    """Игровая сетка уровня."""
    
    def __init__(self, width: int, height: int, cell_size: int = 64):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
    
    def get(self, x: int, y: int) -> CellType:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return CellType.WALL
    
    def set(self, x: int, y: int, cell_type: CellType) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = cell_type
    
    def is_walkable(self, x: int, y: int) -> bool:
        cell = self.get(x, y)
        return cell not in (CellType.WALL, CellType.EMPTY)
    
    def blocks_sight(self, x: int, y: int) -> bool:
        return self.get(x, y) == CellType.WALL
    
    def to_pixel(self, grid_x: int, grid_y: int) -> tuple:
        return grid_x * self.cell_size, grid_y * self.cell_size
    
    def to_grid(self, pixel_x: int, pixel_y: int) -> tuple:
        return pixel_x // self.cell_size, pixel_y // self.cell_size
    
    def find_cells(self, cell_type: CellType) -> list:
        result = []
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] == cell_type:
                    result.append((x, y))
        return result


def load_grid_from_string(level_data: str, cell_size: int = 64) -> Grid:
    """Загрузить сетку из строки.
    
    # - стена, . - пол, X - выход, C - монета, E - враг, P - игрок, N - шум
    """
    lines = [line for line in level_data.strip().split("\n") if line.strip()]
    height = len(lines)
    width = max(len(line) for line in lines)
    grid = Grid(width, height, cell_size)
    for y in range(height):
        for x in range(width):
            grid.set(x, y, CellType.WALL)
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == ".":
                grid.set(x, y, CellType.FLOOR)
            elif char == "#":
                grid.set(x, y, CellType.WALL)
            elif char == "X":
                grid.set(x, y, CellType.EXIT)
            elif char == "C":
                grid.set(x, y, CellType.COIN)
            elif char in ("E", "P"):
                grid.set(x, y, CellType.FLOOR)
            elif char == "N":
                grid.set(x, y, CellType.NOISE_SOURCE)
    return grid