"""Transform Component - позиция и ориентация."""
from dataclasses import dataclass


@dataclass
class TransformComponent:
    x: float = 0.0
    y: float = 0.0
    grid_x: int = 0
    grid_y: int = 0
    facing_angle: float = 0.0
    speed: float = 200.0
    
    def set_grid_position(self, gx: int, gy: int, cell_size: int = 64) -> None:
        self.grid_x = gx
        self.grid_y = gy
        self.x = gx * cell_size + cell_size / 2
        self.y = gy * cell_size + cell_size / 2
    
    def update_grid_position(self, cell_size: int = 64) -> None:
        self.grid_x = int(self.x) // cell_size
        self.grid_y = int(self.y) // cell_size