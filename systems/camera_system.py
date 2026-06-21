"""Camera System - управление камерой."""
from core.ecs import System
from components.transform import TransformComponent
from components.player import PlayerComponent
from presentation.camera import Camera


class CameraSystem(System):
    def __init__(self, world, screen_width: int, screen_height: int):
        super().__init__(world)
        self.camera = Camera(screen_width, screen_height)
    
    def update(self, dt: float) -> None:
        players = self.world.query(PlayerComponent, TransformComponent)
        if not players:
            return
        transform = players[0].get(TransformComponent)
        self.camera.follow(transform.x, transform.y)
    
    def get_camera(self) -> Camera:
        return self.camera