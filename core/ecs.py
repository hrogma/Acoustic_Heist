"""ECS (Entity-Component-System) - архитектурный паттерн."""
from typing import Any, TypeVar, Type
from abc import ABC, abstractmethod

T = TypeVar("T")


class Entity:
    """Сущность - контейнер для компонентов."""
    _id_counter = 0
    
    def __init__(self):
        Entity._id_counter += 1
        self.id = Entity._id_counter
        self._components = {}
        self.alive = True
    
    def add(self, component: Any) -> "Entity":
        self._components[type(component)] = component
        return self
    
    def get(self, component_type: Type[T]) -> T:
        return self._components[component_type]
    
    def has(self, component_type: type) -> bool:
        return component_type in self._components


class World:
    """Мир - хранилище всех сущностей."""
    
    def __init__(self):
        self.entities = {}
        self._component_index = {}
    
    def create_entity(self) -> Entity:
        entity = Entity()
        self.entities[entity.id] = entity
        return entity
    
    def register(self, entity: Entity, component_type: type) -> None:
        if component_type not in self._component_index:
            self._component_index[component_type] = set()
        self._component_index[component_type].add(entity.id)
    
    def destroy_entity(self, entity_id: int) -> None:
        if entity_id in self.entities:
            self.entities[entity_id].alive = False
            for comp_type in self._component_index:
                self._component_index[comp_type].discard(entity_id)
            del self.entities[entity_id]
    
    def query(self, *component_types: type) -> list:
        if not component_types:
            return list(self.entities.values())
        result_ids = None
        for comp_type in component_types:
            ids = self._component_index.get(comp_type, set())
            if result_ids is None:
                result_ids = ids.copy()
            else:
                result_ids &= ids
        if result_ids is None:
            return []
        return [self.entities[eid] for eid in result_ids if eid in self.entities]


class System(ABC):
    """Базовый класс для всех систем."""
    
    def __init__(self, world: World):
        self.world = world
        self.enabled = True
    
    @abstractmethod
    def update(self, dt: float) -> None:
        pass