"""Player Component."""
from dataclasses import dataclass


@dataclass
class PlayerComponent:
    coins: int = 0
    health: int = 100
    is_alive: bool = True
    is_hidden: bool = False