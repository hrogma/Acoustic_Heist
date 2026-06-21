"""Detection System - обнаружение игрока врагами."""
from core.ecs import System
from core.event_bus import Events
from components.transform import TransformComponent
from components.perception import PerceptionComponent
from components.player import PlayerComponent
from domain.fov import compute_fov, has_line_of_sight
from domain.sound import compute_sound_map, SoundMap


class DetectionSystem(System):
    def __init__(self, world, event_bus, grid):
        super().__init__(world)
        self.event_bus = event_bus
        self.grid = grid
        self.current_sound_map: SoundMap = None
        self.event_bus.subscribe(Events.NOISE_EMIT, self._on_noise_emit)
    
    def update(self, dt: float) -> None:
        players = self.world.query(PlayerComponent, TransformComponent)
        if not players:
            return
        player = players[0]
        player_transform = player.get(TransformComponent)
        player_comp = player.get(PlayerComponent)
        if not player_comp.is_alive:
            return
        
        enemies = self.world.query(PerceptionComponent, TransformComponent)
        player_pos = (player_transform.grid_x, player_transform.grid_y)
        
        for enemy in enemies:
            perception = enemy.get(PerceptionComponent)
            enemy_transform = enemy.get(TransformComponent)
            perception.current_fov = compute_fov(
                origin_x=enemy_transform.grid_x,
                origin_y=enemy_transform.grid_y,
                radius=perception.vision_range,
                grid=self.grid,
                facing_angle=enemy_transform.facing_angle,
                fov_angle=perception.vision_angle)
            
            if perception.can_see(player_pos[0], player_pos[1]):
                if has_line_of_sight(
                    enemy_transform.grid_x, enemy_transform.grid_y,
                    player_pos[0], player_pos[1], self.grid):
                    perception.last_known_player_pos = player_pos
                    self.event_bus.emit(Events.ENEMY_SPOTTED_PLAYER,
                        enemy_id=enemy.id, player_pos=player_pos)
    
    def _on_noise_emit(self, x: int, y: int, intensity: float) -> None:
        self.current_sound_map = compute_sound_map(
            grid=self.grid, source_x=x, source_y=y, intensity=intensity)
    
    def get_sound_map(self) -> SoundMap:
        return self.current_sound_map