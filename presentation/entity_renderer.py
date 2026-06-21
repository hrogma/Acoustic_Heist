"""Entity Renderer - отрисовка сущностей БЕЗ отладочных линий."""
import pygame
from components.transform import TransformComponent
from components.sprite import SpriteComponent
from components.player import PlayerComponent
from components.ai_state import AIStateComponent, EnemyState


class EntityRenderer:
    """Рендеринг игровых сущностей."""
    
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera
        self._image_cache = {}
        self._load_sprites()
    
    def _load_sprites(self):
        sprite_paths = {
            "player": "images/pl.png",
            "player2": "images/pl1.png",
            "enemy": "images/enemy.png",
        }
        for name, path in sprite_paths.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self._image_cache[name] = img
            except Exception:
                pass
    
    def render_entities(self, world):
        """Отрисовать все сущности."""
        self._render_enemies(world)
        self._render_player(world)
    
    def _render_enemies(self, world):
        """Отрисовать врагов - ТОЛЬКО спрайты или круги, БЕЗ линий."""
        for entity in world.query(AIStateComponent, TransformComponent, SpriteComponent):
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
            
            screen_x, screen_y = self.camera.apply(transform.x, transform.y)
            
            if "enemy" in self._image_cache and sprite.image_path:
                img = self._image_cache["enemy"]
                img_scaled = pygame.transform.scale(img, (sprite.width, sprite.height))
                rotated = pygame.transform.rotate(img_scaled, transform.facing_angle)
                rect = rotated.get_rect(center=(int(screen_x), int(screen_y)))
                self.screen.blit(rotated, rect)
            else:
                # Просто круг БЕЗ линий направления
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), 28)
    
    def _render_player(self, world):
        """Отрисовать игрока - ТОЛЬКО спрайт или круг, БЕЗ линий."""
        players = world.query(PlayerComponent, TransformComponent, SpriteComponent)
        if not players:
            return
        
        player = players[0]
        transform = player.get(TransformComponent)
        sprite = player.get(SpriteComponent)
        player_comp = player.get(PlayerComponent)
        
        if not player_comp.is_alive:
            return
        
        screen_x, screen_y = self.camera.apply(transform.x, transform.y)
        
        if "player" in self._image_cache:
            img = self._image_cache["player"]
            img_scaled = pygame.transform.scale(img, (sprite.width, sprite.height))
            rotated = pygame.transform.rotate(img_scaled, transform.facing_angle)
            rect = rotated.get_rect(center=(int(screen_x), int(screen_y)))
            self.screen.blit(rotated, rect)
        else:
            # Просто круг БЕЗ линий направления
            pygame.draw.circle(self.screen, (100, 255, 100), (int(screen_x), int(screen_y)), 24)