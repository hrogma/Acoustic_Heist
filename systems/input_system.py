"""Input System - обработка пользовательского ввода."""
import pygame
import math
from core.ecs import System
from components.transform import TransformComponent
from components.noise_emitter import NoiseEmitterComponent
from components.player import PlayerComponent
from core.event_bus import Events


class InputSystem(System):
    def __init__(self, world, event_bus, grid):
        super().__init__(world)
        self.event_bus = event_bus
        self.grid = grid
        self.cell_size = grid.cell_size
    
    def update(self, dt: float) -> None:
        players = self.world.query(PlayerComponent, TransformComponent, NoiseEmitterComponent)
        if not players:
            return
        player = players[0]
        transform = player.get(TransformComponent)
        noise = player.get(NoiseEmitterComponent)
        player_comp = player.get(PlayerComponent)
        if not player_comp.is_alive:
            return
        
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1.0
        
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed_multiplier = 1.8 if is_running else 1.0
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx**2 + dy**2)
            dx /= length
            dy /= length
            noise.is_moving = True
            noise.is_running = is_running
            transform.facing_angle = math.degrees(math.atan2(-dy, dx))
        else:
            noise.is_moving = False
            noise.is_running = False
        
        new_x = transform.x + dx * transform.speed * speed_multiplier * dt
        new_y = transform.y + dy * transform.speed * speed_multiplier * dt
        
        if self._can_move_to(new_x, transform.y):
            transform.x = new_x
        if self._can_move_to(transform.x, new_y):
            transform.y = new_y
        transform.update_grid_position(self.cell_size)
        
        self.event_bus.emit(Events.PLAYER_MOVED,
            x=transform.x, y=transform.y,
            grid_x=transform.grid_x, grid_y=transform.grid_y,
            noise_level=noise.current_noise)
        
        if noise.current_noise > 0:
            self.event_bus.emit(Events.NOISE_EMIT,
                x=transform.grid_x, y=transform.grid_y,
                intensity=noise.current_noise)
    
    def _can_move_to(self, pixel_x: float, pixel_y: float) -> bool:
        size = 24
        corners = [
            (pixel_x - size, pixel_y - size),
            (pixel_x + size, pixel_y - size),
            (pixel_x - size, pixel_y + size),
            (pixel_x + size, pixel_y + size),
        ]
        for cx, cy in corners:
            gx, gy = self.grid.to_grid(int(cx), int(cy))
            if not self.grid.is_walkable(gx, gy):
                return False
        return True