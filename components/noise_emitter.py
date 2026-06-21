"""Noise Emitter Component - источник шума."""
from dataclasses import dataclass


@dataclass
class NoiseEmitterComponent:
    base_noise: float = 0.0
    movement_noise: float = 0.3
    running_noise: float = 0.7
    is_moving: bool = False
    is_running: bool = False
    
    @property
    def current_noise(self) -> float:
        if self.is_running:
            return self.running_noise
        elif self.is_moving:
            return self.movement_noise
        return self.base_noise