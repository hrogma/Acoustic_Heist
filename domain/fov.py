"""Алгоритм поля зрения - Shadowcasting."""
import math
from typing import Set, Tuple
from domain.grid import Grid


_MULTIPLIERS = [
    (1, 0, 0, 1), (0, 1, 1, 0), (0, -1, 1, 0), (-1, 0, 0, 1),
    (-1, 0, 0, -1), (0, -1, -1, 0), (0, 1, -1, 0), (1, 0, 0, -1),
]


def compute_fov(
    origin_x: int, origin_y: int, radius: int, grid: Grid,
    facing_angle: float = 0.0, fov_angle: float = 360.0,
) -> Set[Tuple[int, int]]:
    """Вычислить поле зрения из точки."""
    visible = set()
    visible.add((origin_x, origin_y))
    use_angle_filter = fov_angle < 360.0
    half_fov = fov_angle / 2.0
    
    for octant in range(8):
        _cast_light(octant, 1, 1.0, 0.0, radius, origin_x, origin_y, grid, visible)
    
    if use_angle_filter:
        filtered = set()
        for (x, y) in visible:
            dx = x - origin_x
            dy = y - origin_y
            if dx == 0 and dy == 0:
                filtered.add((x, y))
                continue
            angle = math.degrees(math.atan2(-dy, dx))
            angle = (angle + 360) % 360
            diff = abs(angle - facing_angle)
            if diff > 180:
                diff = 360 - diff
            if diff <= half_fov:
                filtered.add((x, y))
        return filtered
    return visible


def _cast_light(octant, row, start_slope, end_slope, radius, cx, cy, grid, visible):
    """Рекурсивный расчет лучей в одном октанте."""
    if start_slope < end_slope:
        return
    xx, xy, yx, yy = _MULTIPLIERS[octant]
    new_start = 0.0
    for j in range(row, radius + 1):
        dx = -j - 1
        dy = -j
        while dx <= 0:
            dx += 1
            l_x = cx + dx * xx + dy * xy
            l_y = cy + dx * yx + dy * yy
            if l_x < 0 or l_x >= grid.width or l_y < 0 or l_y >= grid.height:
                continue
            left_slope = (dx + 0.5) / (dy - 0.5) if dy != 0.5 else float('inf')
            right_slope = (dx - 0.5) / (dy + 0.5) if dy != -0.5 else float('inf')
            if start_slope < right_slope:
                continue
            elif end_slope > left_slope:
                break
            if dx * dx + dy * dy <= radius * radius:
                visible.add((l_x, l_y))
            if grid.blocks_sight(l_x, l_y):
                if new_start < left_slope:
                    new_start = left_slope
                    _cast_light(octant, j + 1, new_start, left_slope, radius, cx, cy, grid, visible)
                new_start = left_slope
            else:
                new_start = right_slope
        last_x = cx + dx * xx + dy * xy
        last_y = cy + dx * yx + dy * yy
        if 0 <= last_x < grid.width and 0 <= last_y < grid.height:
            if grid.blocks_sight(last_x, last_y):
                _cast_light(octant, j + 1, new_start, end_slope, radius, cx, cy, grid, visible)


def has_line_of_sight(x1: int, y1: int, x2: int, y2: int, grid: Grid) -> bool:
    """Проверить прямую видимость (алгоритм Брезенхэма)."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    x, y = x1, y1
    while True:
        if x == x2 and y == y2:
            return True
        if (x != x1 or y != y1) and (x != x2 or y != y2):
            if grid.blocks_sight(x, y):
                return False
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy