"""Алгоритм поиска пути A*."""
import heapq
from dataclasses import dataclass
from typing import Optional, List, Tuple
from domain.grid import Grid


@dataclass
class Node:
    x: int
    y: int
    g_cost: float = 0.0
    h_cost: float = 0.0
    parent: Optional["Node"] = None
    
    @property
    def f_cost(self) -> float:
        return self.g_cost + self.h_cost
    
    def __lt__(self, other: "Node") -> bool:
        return self.f_cost < other.f_cost
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))


def find_path(
    grid: Grid, start_x: int, start_y: int, goal_x: int, goal_y: int
) -> Optional[List[Tuple[int, int]]]:
    """Найти кратчайший путь от start до goal."""
    if not grid.is_walkable(start_x, start_y) or not grid.is_walkable(goal_x, goal_y):
        return None
    start = Node(start_x, start_y)
    goal = Node(goal_x, goal_y)
    open_set = []
    heapq.heappush(open_set, start)
    closed_set = {}
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while open_set:
        current = heapq.heappop(open_set)
        if current.x == goal.x and current.y == goal.y:
            return _reconstruct_path(current)
        if (current.x, current.y) in closed_set:
            continue
        closed_set[(current.x, current.y)] = current
        for dx, dy in directions:
            nx, ny = current.x + dx, current.y + dy
            if not grid.is_walkable(nx, ny):
                continue
            if (nx, ny) in closed_set:
                continue
            neighbor = Node(nx, ny)
            neighbor.g_cost = current.g_cost + 1.0
            neighbor.h_cost = abs(nx - goal.x) + abs(ny - goal.y)
            neighbor.parent = current
            heapq.heappush(open_set, neighbor)
    return None


def _reconstruct_path(node: Node) -> List[Tuple[int, int]]:
    path = []
    current: Optional[Node] = node
    while current is not None:
        path.append((current.x, current.y))
        current = current.parent
    path.reverse()
    return path[1:] if len(path) > 1 else []