"""Collectible Component."""
from dataclasses import dataclass
from enum import Enum


class CollectibleType(Enum):
    COIN = "coin"
    KEY = "key"
    HEALTH = "health"


@dataclass
class CollectibleComponent:
    type: CollectibleType = CollectibleType.COIN
    value: int = 1