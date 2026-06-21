"""Распространение звука через Dijkstra Map."""
import heapq
from dataclasses import dataclass
from typing import Optional, Tuple, List
from domain.grid import Grid


@dataclass
class SoundMap:
    """Карта распространения звука."""
    intensity: list
    source: Tuple[int, int]
    max_intensity: float = 1.0
    width: int = 0
    height: int = 0
    
    def get_loudness(self, x: int, y: int) -> float:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.intensity[y][x]
        return 0.0
    
    def get_loudest_direction(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Получить направление к самому громкому соседу."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]
        max_loudness = self.get_loudness(x, y)
        best_dir = None
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            loudness = self.get_loudness(nx, ny)
            if loudness > max_loudness:
                max_loudness = loudness
                best_dir = (dx, dy)
        return best_dir


def compute_sound_map(
    grid: Grid, source_x: int, source_y: int,
    intensity: float = 1.0, decay: float = 0.15, max_distance: int = 15
) -> SoundMap:
    """Вычислить карту распространения звука."""
    width = grid.width
    height = grid.height
    sound_map = [[0.0 for _ in range(width)] for _ in range(height)]
    if not (0 <= source_x < width and 0 <= source_y < height):
        return SoundMap(sound_map, (source_x, source_y), intensity, width, height)
    queue = [(-intensity, source_x, source_y)]
    visited = set()
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                 (1, 1), (1, -1), (-1, 1), (-1, -1)]
    while queue:
        neg_loudness, x, y = heapq.heappop(queue)
        current_loudness = -neg_loudness
        if (x, y) in visited or current_loudness < 0.01:
            continue
        visited.add((x, y))
        sound_map[y][x] = max(sound_map[y][x], current_loudness)
        if max(abs(x - source_x), abs(y - source_y)) >= max_distance:
            continue
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if grid.blocks_sight(nx, ny) or (nx, ny) in visited:
                continue
            is_diagonal = dx != 0 and dy != 0
            distance_factor = 1.414 if is_diagonal else 1.0
            new_loudness = current_loudness - (decay * distance_factor)
            if new_loudness > 0.01:
                heapq.heappush(queue, (-new_loudness, nx, ny))
    return SoundMap(sound_map, (source_x, source_y), intensity, width, height)


def get_hearing_threshold(
    enemy_x: int, enemy_y: int,
    sound_map: SoundMap, hearing_sensitivity: float = 0.2
) -> bool:
    """Проверить, слышит ли враг звук."""
    return sound_map.get_loudness(enemy_x, enemy_y) >= hearing_sensitivity