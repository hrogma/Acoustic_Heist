"""Camera System - управление камерой."""
from core.ecs import System
from components.transform import TransformComponent
from components.player import PlayerComponent


class CameraSystem(System):
    def __init__(self, world, screen_width: int, screen_height: int):
        super().__init__(world)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
    
    def update(self, dt: float) -> None:
        players = self.world.query(PlayerComponent, TransformComponent)
        if not players:
            return
        transform = players[0].get(TransformComponent)
        self.x = transform.x - self.screen_width // 2
        self.y = transform.y - self.screen_height // 2
    
    def apply(self, x: float, y: float) -> tuple:
        """Применить смещение камеры к координатам."""
        return int(x - self.x), int(y - self.y)