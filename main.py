"""Acoustic Heist - стелс-игра на Python.

Архитектура: ECS + EventBus + MVC
Алгоритмы: Shadowcasting (FOV), A* (Pathfinding), Dijkstra Map (Sound)
"""
import sys
import os

# Добавить корень проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from core.ecs import World
from core.event_bus import EventBus, Events

from components.transform import TransformComponent
from components.sprite import SpriteComponent
from components.perception import PerceptionComponent
from components.ai_state import AIStateComponent
from components.noise_emitter import NoiseEmitterComponent
from components.collectible import CollectibleComponent, CollectibleType
from components.player import PlayerComponent

from systems.input_system import InputSystem
from systems.detection_system import DetectionSystem
from systems.ai_system import AISystem
from systems.collision_system import CollisionSystem
from systems.camera_system import CameraSystem
from systems.render_system import RenderSystem

from domain.grid import load_grid_from_string
from levels.level1 import LEVEL_1, PATROL_POINTS_1


class Game:
    """Главный класс игры."""
    
    SCREEN_WIDTH = 956
    SCREEN_HEIGHT = 716
    CELL_SIZE = 64
    FPS = 60
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Acoustic Heist")
        
        # Загрузить иконку
        try:
            icon = pygame.image.load("images/icon.png")
            pygame.display.set_icon(icon)
        except Exception:
            pass
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Загрузить фоновую музыку
        try:
            pygame.mixer.init()
            bg_sound = pygame.mixer.Sound("sounds/bg.mp3")
            bg_sound.set_volume(0.3)
            bg_sound.play(-1)
        except Exception as e:
            print(f"Не удалось загрузить музыку: {e}")
        
        # Инициализация ядра
        self.world = World()
        self.event_bus = EventBus()
        
        # Загрузить уровень
        self.grid = load_grid_from_string(LEVEL_1, self.CELL_SIZE)
        
        # Создать системы
        self.camera = CameraSystem(self.world, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.detection_system = DetectionSystem(self.world, self.event_bus, self.grid)
        self.input_system = InputSystem(self.world, self.event_bus, self.grid)
        self.ai_system = AISystem(self.world, self.event_bus, self.grid, self.detection_system)
        self.collision_system = CollisionSystem(self.world, self.event_bus, self.grid)
        self.render_system = RenderSystem(self.world, self.screen, self.grid, self.camera)
        
        # Создать сущности уровня
        self._create_level_entities()
        
        # Подписаться на события
        self.event_bus.subscribe(Events.LEVEL_COMPLETED, self._on_level_completed)
        self.event_bus.subscribe(Events.PLAYER_DIED, self._on_player_died)
        
        self.running = True
        self.game_state = "playing"  # playing, won, lost
    
    def _create_level_entities(self):
        """Создать сущности из данных уровня."""
        # Найти позицию игрока
        player_pos = self._find_char(LEVEL_1, "P")
        if player_pos:
            player = self.world.create_entity()
            player.add(TransformComponent())
            player.get(TransformComponent).set_grid_position(
                player_pos[0], player_pos[1], self.CELL_SIZE)
            player.get(TransformComponent).speed = 200.0
            player.add(SpriteComponent(image_path="images/pl.png", width=64, height=64))
            player.add(PlayerComponent())
            player.add(PerceptionComponent(vision_range=10, vision_angle=360.0))
            player.add(NoiseEmitterComponent())
            self.world.register(player, TransformComponent)
            self.world.register(player, SpriteComponent)
            self.world.register(player, PlayerComponent)
            self.world.register(player, PerceptionComponent)
            self.world.register(player, NoiseEmitterComponent)
        
        # Найти врагов
        enemy_positions = []
        lines = [line for line in LEVEL_1.strip().split("\n") if line.strip()]
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == "E":
                    enemy_positions.append((x, y))
        
        for idx, pos in enumerate(enemy_positions):
            enemy = self.world.create_entity()
            enemy.add(TransformComponent())
            enemy.get(TransformComponent).set_grid_position(pos[0], pos[1], self.CELL_SIZE)
            enemy.get(TransformComponent).speed = 140.0
            enemy.add(SpriteComponent(image_path="images/enemy.png", width=64, height=64))
            enemy.add(PerceptionComponent(
                vision_range=7, vision_angle=120.0, hearing_sensitivity=0.15))
            patrol_pts = PATROL_POINTS_1.get(idx, [])
            enemy.add(AIStateComponent(patrol_points=patrol_pts))
            self.world.register(enemy, TransformComponent)
            self.world.register(enemy, SpriteComponent)
            self.world.register(enemy, PerceptionComponent)
            self.world.register(enemy, AIStateComponent)
        
        # Создать монеты
        coin_positions = []
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == "C":
                    coin_positions.append((x, y))
        
        for pos in coin_positions:
            coin = self.world.create_entity()
            coin.add(TransformComponent())
            coin.get(TransformComponent).set_grid_position(pos[0], pos[1], self.CELL_SIZE)
            coin.add(SpriteComponent(image_path="images/coin.png", width=32, height=32))
            coin.add(CollectibleComponent(type=CollectibleType.COIN, value=1))
            self.world.register(coin, TransformComponent)
            self.world.register(coin, SpriteComponent)
            self.world.register(coin, CollectibleComponent)
    
    def _find_char(self, level_data: str, char: str):
        lines = [line for line in level_data.strip().split("\n") if line.strip()]
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                if c == char:
                    return (x, y)
        return None
    
    def _on_level_completed(self, **kwargs):
        self.game_state = "won"
        print("Уровень пройден!")
    
    def _on_player_died(self, **kwargs):
        self.game_state = "lost"
        print("Игрок пойман!")
    
    def run(self):
        """Главный игровой цикл."""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self._restart()
            
            if self.game_state == "playing":
                self.input_system.update(dt)
                self.detection_system.update(dt)
                self.ai_system.update(dt)
                self.collision_system.update(dt)
            
            self.camera.update(dt)
            self.render_system.update(dt)
            
            if self.game_state == "won":
                self._render_end_screen("ПОБЕДА!", (100, 255, 100))
            elif self.game_state == "lost":
                self._render_end_screen("ПОЙМАН!", (255, 50, 50))
            
            pygame.display.flip()
        
        pygame.quit()
    
    def _render_end_screen(self, text: str, color: tuple):
        font = pygame.font.SysFont(None, 72)
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect(center=(
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        self.screen.blit(text_surface, rect)
        small_font = pygame.font.SysFont(None, 32)
        hint = small_font.render(
            "Нажмите R для рестарта или ESC для выхода", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(hint, hint_rect)
    
    def _restart(self):
        """Перезапустить уровень."""
        self.world = World()
        self.event_bus = EventBus()
        self._create_level_entities()
        self.camera = CameraSystem(self.world, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.detection_system = DetectionSystem(self.world, self.event_bus, self.grid)
        self.input_system = InputSystem(self.world, self.event_bus, self.grid)
        self.ai_system = AISystem(
            self.world, self.event_bus, self.grid, self.detection_system)
        self.collision_system = CollisionSystem(self.world, self.event_bus, self.grid)
        self.render_system = RenderSystem(
            self.world, self.screen, self.grid, self.camera)
        self.event_bus.subscribe(Events.LEVEL_COMPLETED, self._on_level_completed)
        self.event_bus.subscribe(Events.PLAYER_DIED, self._on_player_died)
        self.game_state = "playing"


if __name__ == "__main__":
    game = Game()
    game.run()