"""Event Bus - паттерн для слабой связанности систем."""
from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """Централизованная шина событий."""
    
    def __init__(self):
        self._listeners = defaultdict(list)
    
    def subscribe(self, event_name: str, callback: Callable) -> None:
        self._listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        if event_name in self._listeners:
            self._listeners[event_name] = [
                cb for cb in self._listeners[event_name] if cb != callback
            ]
    
    def emit(self, event_name: str, **data: Any) -> None:
        for callback in self._listeners[event_name]:
            try:
                callback(**data)
            except Exception as e:
                print(f"Error in handler for '{event_name}': {e}")
    
    def clear(self) -> None:
        self._listeners.clear()


class Events:
    PLAYER_MOVED = "player_moved"
    NOISE_EMIT = "noise_emit"
    ENEMY_SPOTTED_PLAYER = "enemy_spotted_player"
    ENEMY_LOST_PLAYER = "enemy_lost_player"
    PLAYER_DIED = "player_died"
    LEVEL_COMPLETED = "level_completed"
    COIN_COLLECTED = "coin_collected"