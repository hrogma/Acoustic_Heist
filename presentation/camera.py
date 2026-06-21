"""Camera - управление камерой."""


class Camera:
    """Камера, следующая за игроком."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
    
    def follow(self, target_x: float, target_y: float) -> None:
        """Следовать за целью."""
        self.x = target_x - self.screen_width // 2
        self.y = target_y - self.screen_height // 2
    
    def apply(self, x: float, y: float) -> tuple:
        """Применить смещение камеры к координатам."""
        return int(x - self.x), int(y - self.y)