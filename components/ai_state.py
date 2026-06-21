"""AI State Component - конечный автомат."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple


class EnemyState(Enum):
    PATROL = "patrol"
    INVESTIGATE = "investigate"
    CHASE = "chase"
    SEARCH = "search"
    ALERT = "alert"


@dataclass
class AIStateComponent:
    state: EnemyState = EnemyState.PATROL
    patrol_points: List[Tuple[int, int]] = field(default_factory=list)
    current_patrol_index: int = 0
    target_position: Optional[Tuple[int, int]] = None
    path: List[Tuple[int, int]] = field(default_factory=list)
    path_index: int = 0
    state_timer: float = 0.0
    chase_timer: float = 0.0
    alert_cooldown: float = 0.0
    investigate_timeout: float = 5.0
    chase_timeout: float = 3.0
    search_timeout: float = 8.0
    
    def change_state(self, new_state: EnemyState) -> None:
        if self.state != new_state:
            self.state = new_state
            self.state_timer = 0.0
            self.path = []
            self.path_index = 0
    
    def update_timer(self, dt: float) -> None:
        self.state_timer += dt
        if self.alert_cooldown > 0:
            self.alert_cooldown -= dt