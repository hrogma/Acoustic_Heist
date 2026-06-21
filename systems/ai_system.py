"""AI System - искусственный интеллект врагов."""
import math
import random
from core.ecs import System
from core.event_bus import Events
from components.transform import TransformComponent
from components.ai_state import AIStateComponent, EnemyState
from components.perception import PerceptionComponent
from components.player import PlayerComponent
from domain.pathfinding import find_path
from domain.sound import get_hearing_threshold


class AISystem(System):
    def __init__(self, world, event_bus, grid, detection_system):
        super().__init__(world)
        self.event_bus = event_bus
        self.grid = grid
        self.cell_size = grid.cell_size
        self.detection_system = detection_system
        self.event_bus.subscribe(Events.ENEMY_SPOTTED_PLAYER, self._on_enemy_spotted)
        self.event_bus.subscribe(Events.NOISE_EMIT, self._on_noise_emit)
    
    def update(self, dt: float) -> None:
        players = self.world.query(PlayerComponent, TransformComponent)
        if not players:
            return
        player = players[0]
        player_transform = player.get(TransformComponent)
        player_pos = (player_transform.grid_x, player_transform.grid_y)
        
        enemies = self.world.query(AIStateComponent, TransformComponent, PerceptionComponent)
        for enemy in enemies:
            ai = enemy.get(AIStateComponent)
            transform = enemy.get(TransformComponent)
            perception = enemy.get(PerceptionComponent)
            ai.update_timer(dt)
            
            if ai.state == EnemyState.PATROL:
                self._handle_patrol(ai, transform, dt)
            elif ai.state == EnemyState.INVESTIGATE:
                self._handle_investigate(ai, transform, dt)
            elif ai.state == EnemyState.CHASE:
                self._handle_chase(ai, transform, player_pos, dt)
            elif ai.state == EnemyState.SEARCH:
                self._handle_search(ai, transform, dt)
            elif ai.state == EnemyState.ALERT:
                self._handle_alert(ai, dt)
    
    def _handle_patrol(self, ai, transform, dt):
        if not ai.patrol_points:
            return
        if not ai.path or ai.path_index >= len(ai.path):
            target = ai.patrol_points[ai.current_patrol_index]
            path = find_path(self.grid, transform.grid_x, transform.grid_y,
                            target[0], target[1])
            if path:
                ai.path = path
                ai.path_index = 0
            else:
                ai.current_patrol_index = (ai.current_patrol_index + 1) % len(ai.patrol_points)
                return
        self._move_along_path(ai, transform, dt)
        if ai.path_index >= len(ai.path):
            ai.current_patrol_index = (ai.current_patrol_index + 1) % len(ai.patrol_points)
    
    def _handle_investigate(self, ai, transform, dt):
        if not ai.target_position:
            ai.change_state(EnemyState.PATROL)
            return
        if not ai.path or ai.path_index >= len(ai.path):
            path = find_path(self.grid, transform.grid_x, transform.grid_y,
                            ai.target_position[0], ai.target_position[1])
            if path:
                ai.path = path
                ai.path_index = 0
            else:
                ai.change_state(EnemyState.PATROL)
                return
        self._move_along_path(ai, transform, dt)
        if ai.state_timer >= ai.investigate_timeout or ai.path_index >= len(ai.path):
            ai.change_state(EnemyState.PATROL)
    
    def _handle_chase(self, ai, transform, player_pos, dt):
        ai.target_position = player_pos
        if not ai.path or ai.path_index >= len(ai.path) or ai.state_timer % 0.5 < dt:
            path = find_path(self.grid, transform.grid_x, transform.grid_y,
                            player_pos[0], player_pos[1])
            if path:
                ai.path = path
                ai.path_index = 0
        self._move_along_path(ai, transform, dt)
        ai.chase_timer += dt
        if ai.chase_timer >= ai.chase_timeout:
            ai.change_state(EnemyState.SEARCH)
            ai.chase_timer = 0.0
    
    def _handle_search(self, ai, transform, dt):
        if not ai.path or ai.path_index >= len(ai.path):
            for _ in range(10):
                rx = transform.grid_x + random.randint(-5, 5)
                ry = transform.grid_y + random.randint(-5, 5)
                if self.grid.is_walkable(rx, ry):
                    path = find_path(self.grid, transform.grid_x, transform.grid_y, rx, ry)
                    if path:
                        ai.path = path
                        ai.path_index = 0
                        break
        self._move_along_path(ai, transform, dt)
        if ai.state_timer >= ai.search_timeout:
            ai.change_state(EnemyState.PATROL)
    
    def _handle_alert(self, ai, dt):
        if ai.state_timer >= 0.5:
            ai.change_state(EnemyState.CHASE)
    
    def _move_along_path(self, ai, transform, dt):
        if not ai.path or ai.path_index >= len(ai.path):
            return
        target_cell = ai.path[ai.path_index]
        target_x = target_cell[0] * self.cell_size + self.cell_size / 2
        target_y = target_cell[1] * self.cell_size + self.cell_size / 2
        dx = target_x - transform.x
        dy = target_y - transform.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 5:
            ai.path_index += 1
            return
        if distance > 0:
            dx /= distance
            dy /= distance
            transform.facing_angle = math.degrees(math.atan2(-dy, dx))
            enemy_speed = transform.speed * 0.7
            transform.x += dx * enemy_speed * dt
            transform.y += dy * enemy_speed * dt
            transform.update_grid_position(self.cell_size)
    
    def _on_enemy_spotted(self, enemy_id: int, player_pos: tuple) -> None:
        for enemy in self.world.query(AIStateComponent):
            if enemy.id == enemy_id:
                ai = enemy.get(AIStateComponent)
                if ai.state not in (EnemyState.CHASE, EnemyState.ALERT):
                    ai.change_state(EnemyState.ALERT)
                break
    
    def _on_noise_emit(self, x: int, y: int, intensity: float) -> None:
        sound_map = self.detection_system.get_sound_map()
        if not sound_map:
            return
        for enemy in self.world.query(AIStateComponent, TransformComponent, PerceptionComponent):
            ai = enemy.get(AIStateComponent)
            transform = enemy.get(TransformComponent)
            perception = enemy.get(PerceptionComponent)
            if ai.state in (EnemyState.CHASE, EnemyState.ALERT):
                continue
            if get_hearing_threshold(transform.grid_x, transform.grid_y,
                                    sound_map, perception.hearing_sensitivity):
                ai.target_position = (x, y)
                ai.change_state(EnemyState.INVESTIGATE)