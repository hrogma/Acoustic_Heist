"""Render System - отрисовка всех сущностей БЕЗ отладочных линий."""
import pygame
from core.ecs import System
from components.transform import TransformComponent
from components.player import PlayerComponent
from domain.fov import compute_fov
from presentation.grid_renderer import GridRenderer
from presentation.entity_renderer import EntityRenderer


class RenderSystem(System):
    def __init__(self, world, screen, grid, camera):
        super().__init__(world)
        self.screen = screen
        self.grid = grid
        self.camera = camera
        self.cell_size = grid.cell_size
        self.grid_renderer = GridRenderer(screen, grid, camera)
        self.entity_renderer = EntityRenderer(screen, camera)
    
    def update(self, dt: float) -> None:
        self.screen.fill((10, 10, 15))
        self.grid_renderer.render()
        self._render_fov_overlay()
        self.entity_renderer.render_entities(self.world)
        self._render_debug_info()
    
    def _render_fov_overlay(self):
        """Отрисовать затемнение вне поля зрения игрока."""
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
    
    def _render_debug_info(self):
        """Отрисовать отладочную информацию - ТОЛЬКО текст, БЕЗ линий."""
        font = pygame.font.SysFont(None, 24)
        players = self.world.query(PlayerComponent)
        if players:
            player_comp = players[0].get(PlayerComponent)
            text = font.render(f"Монеты: {player_comp.coins}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))