"""Collision System - обработка столкновений."""
import math
from core.ecs import System
from core.event_bus import Events
from components.transform import TransformComponent
from components.collectible import CollectibleComponent
from components.player import PlayerComponent
from components.ai_state import AIStateComponent
from domain.grid import CellType


class CollisionSystem(System):
    def __init__(self, world, event_bus, grid):
        super().__init__(world)
        self.event_bus = event_bus
        self.grid = grid
    
    def update(self, dt: float) -> None:
        self._check_collectibles()
        self._check_exit()
        self._check_enemy_collision()
    
    def _check_collectibles(self):
        players = self.world.query(PlayerComponent, TransformComponent)
        collectibles = self.world.query(CollectibleComponent, TransformComponent)
        if not players:
            return
        player = players[0]
        player_transform = player.get(TransformComponent)
        player_comp = player.get(PlayerComponent)
        for item in collectibles:
            item_transform = item.get(TransformComponent)
            dx = player_transform.x - item_transform.x
            dy = player_transform.y - item_transform.y
            if math.sqrt(dx**2 + dy**2) < 40:
                collectible = item.get(CollectibleComponent)
                player_comp.coins += collectible.value
                self.event_bus.emit(Events.COIN_COLLECTED, value=collectible.value)
                self.grid.set(item_transform.grid_x, item_transform.grid_y, CellType.FLOOR)
                self.world.destroy_entity(item.id)
    
    def _check_exit(self):
        players = self.world.query(PlayerComponent, TransformComponent)
        if not players:
            return
        player_transform = players[0].get(TransformComponent)
        if self.grid.get(player_transform.grid_x, player_transform.grid_y) == CellType.EXIT:
            self.event_bus.emit(Events.LEVEL_COMPLETED)
    
    def _check_enemy_collision(self):
        players = self.world.query(PlayerComponent, TransformComponent)
        enemies = self.world.query(AIStateComponent, TransformComponent)
        if not players:
            return
        player = players[0]
        player_transform = player.get(TransformComponent)
        player_comp = player.get(PlayerComponent)
        for enemy in enemies:
            enemy_transform = enemy.get(TransformComponent)
            dx = player_transform.x - enemy_transform.x
            dy = player_transform.y - enemy_transform.y
            if math.sqrt(dx**2 + dy**2) < 48:
                player_comp.is_alive = False
                self.event_bus.emit(Events.PLAYER_DIED)
                break