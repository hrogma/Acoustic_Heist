"""Perception Component - зрение и слух."""
from dataclasses import dataclass, field
from typing import Set, Tuple, Optional


@dataclass
class PerceptionComponent:
    vision_range: int = 6
    vision_angle: float = 90.0
    hearing_range: int = 8
    hearing_sensitivity: float = 0.2
    current_fov: Set[Tuple[int, int]] = field(default_factory=set)
    last_known_player_pos: Optional[Tuple[int, int]] = None
    
    def can_see(self, x: int, y: int) -> bool:
        return (x, y) in self.current_fov