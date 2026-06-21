"""Grid Renderer - отрисовка сетки уровня."""
import pygame
from domain.grid import CellType


class GridRenderer:
    """Рендеринг игровой сетки."""
    
    def __init__(self, screen, grid, camera):
        self.screen = screen
        self.grid = grid
        self.camera = camera
        self.cell_size = grid.cell_size
        self._image_cache = {}
        self.colors = {
            CellType.EMPTY: (20, 20, 30),
            CellType.WALL: (60, 60, 80),
            CellType.FLOOR: (40, 45, 55),
            CellType.EXIT: (50, 180, 80),
            CellType.COIN: (220, 180, 40),
            CellType.NOISE_SOURCE: (180, 80, 80),
        }
        self._load_sprites()
    
    def _load_sprites(self):
        sprite_paths = {
            "coin": "images/coin.png",
            "exit": "images/exit.png",
        }
        for name, path in sprite_paths.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self._image_cache[name] = img
            except Exception:
                pass
    
    def render(self):
        """Отрисовать сетку."""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get(x, y)
                px, py = self.grid.to_pixel(x, y)
                screen_x, screen_y = self.camera.apply(px, py)
                
                # Оптимизация: не рендерить то, что за экраном
                if screen_x + self.cell_size < 0 or screen_x > self.screen.get_width():
                    continue
                if screen_y + self.cell_size < 0 or screen_y > self.screen.get_height():
                    continue
                
                color = self.colors.get(cell, (40, 40, 40))
                pygame.draw.rect(self.screen, color,
                    (screen_x, screen_y, self.cell_size, self.cell_size))
                
                if cell == CellType.WALL:
                    pygame.draw.rect(self.screen, (40, 40, 50),
                        (screen_x, screen_y, self.cell_size, self.cell_size), 1)
                elif cell == CellType.EXIT:
                    if "exit" in self._image_cache:
                        self.screen.blit(self._image_cache["exit"], (screen_x, screen_y))
                    else:
                        font = pygame.font.SysFont(None, 48)
                        text = font.render("X", True, (255, 255, 255))
                        self.screen.blit(text, (screen_x + 20, screen_y + 15))
                elif cell == CellType.COIN:
                    if "coin" in self._image_cache:
                        self.screen.blit(self._image_cache["coin"],
                            (screen_x + 16, screen_y + 16))
                    else:
                        pygame.draw.circle(self.screen, (255, 215, 0),
                            (screen_x + self.cell_size // 2, screen_y + self.cell_size // 2), 12)