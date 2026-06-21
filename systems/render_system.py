"""Render System - отрисовка всех сущностей."""
import pygame
import math
from core.ecs import System
from components.transform import TransformComponent
from components.sprite import SpriteComponent
from components.player import PlayerComponent
from components.ai_state import AIStateComponent, EnemyState
from domain.grid import CellType
from domain.fov import compute_fov


class RenderSystem(System):
    def __init__(self, world, screen, grid, camera):
        super().__init__(world)
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
            "player": "images/pl.png",
            "player2": "images/pl1.png",
            "enemy": "images/enemy.png",
            "coin": "images/coin.png",
            "exit": "images/exit.png",
        }
        for name, path in sprite_paths.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self._image_cache[name] = img
            except:
                pass
    
    def update(self, dt: float) -> None:
        self.screen.fill((10, 10, 15))
        self._render_grid()
        self._render_fov_overlay()
        self._render_entities()
        self._render_debug_info()
    
    def _render_grid(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                cell = self.grid.get(x, y)
                px, py = self.grid.to_pixel(x, y)
                screen_x, screen_y = self.camera.apply(px, py)
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
    
    def _render_fov_overlay(self):
        players = self.world.query(PlayerComponent, TransformComponent)
        if not players:
            return
        transform = players[0].get(TransformComponent)
        player_fov = compute_fov(transform.grid_x, transform.grid_y,
            radius=10, grid=self.grid, fov_angle=360.0)
        dark_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 180))
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if (x, y) not in player_fov:
                    px, py = self.grid.to_pixel(x, y)
                    screen_x, screen_y = self.camera.apply(px, py)
                    if 0 <= screen_x < self.screen.get_width() and \
                       0 <= screen_y < self.screen.get_height():
                        self.screen.blit(dark_surface, (screen_x, screen_y))
    
    def _render_entities(self):
        # Враги
        for entity in self.world.query(AIStateComponent, TransformComponent, SpriteComponent):
            transform = entity.get(TransformComponent)
            sprite = entity.get(SpriteComponent)
            ai = entity.get(AIStateComponent)
            state_colors = {
                EnemyState.PATROL: (100, 150, 255),
                EnemyState.INVESTIGATE: (255, 200, 50),
                EnemyState.CHASE: (255, 80, 80),
                EnemyState.SEARCH: (200, 100, 200),
                EnemyState.ALERT: (255, 150, 50),
            }
            color = state_colors.get(ai.state, (200, 200, 200))
            if "enemy" in self._image_cache and sprite.image_path:
                img = self._image_cache["enemy"]
                img_scaled = pygame.transform.scale(img, (sprite.width, sprite.height))
                rotated = pygame.transform.rotate(img_scaled, transform.facing_angle)
                rect = rotated.get_rect(center=(
                    int(transform.x - self.camera.x), int(transform.y - self.camera.y)))
                self.screen.blit(rotated, rect)
            else:
                pygame.draw.circle(self.screen, color,
                    (int(transform.x - self.camera.x), int(transform.y - self.camera.y)), 28)
                end_x = transform.x + math.cos(math.radians(transform.facing_angle)) * 35
                end_y = transform.y - math.sin(math.radians(transform.facing_angle)) * 35
                pygame.draw.line(self.screen, (255, 255, 255),
                    (int(transform.x - self.camera.x), int(transform.y - self.camera.y)),
                    (int(end_x - self.camera.x), int(end_y - self.camera.y)), 3)
        
        # Игрок
        players = self.world.query(PlayerComponent, TransformComponent, SpriteComponent)
        if players:
            player = players[0]
            transform = player.get(TransformComponent)
            sprite = player.get(SpriteComponent)
            player_comp = player.get(PlayerComponent)
            if player_comp.is_alive:
                if "player" in self._image_cache:
                    img = self._image_cache["player"]
                    img_scaled = pygame.transform.scale(img, (sprite.width, sprite.height))
                    rotated = pygame.transform.rotate(img_scaled, transform.facing_angle)
                    rect = rotated.get_rect(center=(
                        int(transform.x - self.camera.x), int(transform.y - self.camera.y)))
                    self.screen.blit(rotated, rect)
                else:
                    pygame.draw.circle(self.screen, (100, 255, 100),
                        (int(transform.x - self.camera.x), int(transform.y - self.camera.y)), 24)
    
    def _render_debug_info(self):
        font = pygame.font.SysFont(None, 24)
        players = self.world.query(PlayerComponent)
        if players:
            player_comp = players[0].get(PlayerComponent)
            text = font.render(f"Монеты: {player_comp.coins}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
            if not player_comp.is_alive:
                game_over = pygame.font.SysFont(None, 72)
                text = game_over.render("ПОЙМАН!", True, (255, 50, 50))
                rect = text.get_rect(center=(
                    self.screen.get_width() // 2, self.screen.get_height() // 2))
                self.screen.blit(text, rect)