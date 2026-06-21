"""Sprite Component - визуальное представление."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SpriteComponent:
    image_path: Optional[str] = None
    width: int = 64
    height: int = 64
    visible: bool = True
    color: tuple = (255, 255, 255)
    _image_cache: object = None