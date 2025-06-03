from typing import Dict, List, Optional, TypeVar, Generic
from domain.base_entity import BaseEntity
from ..specifications.base_specification import Specification

T = TypeVar('T', bound=BaseEntity)

class BaseMemoryRepository(Generic[T]):
    def __init__(self):
        self._items: Dict[int, T] = {}
        self.__next_id: int = 1

    @property
    def _next_id(self) -> int:
        next_id = self.__next_id
        self.__next_id += 1
        return next_id

    def get_by_id(self, id: int) -> Optional[T]:
        return self._items.get(id)

    def get_all(self) -> List[T]:
        return list(self._items.values())

    def add(self, entity: T) -> T:
        if entity is None:
            raise ValueError("Entity cannot be None")
        
        entity.id = self._next_id
        self._items[entity.id] = entity
        return entity

    def update(self, entity: T) -> T:
        if not entity.id or entity.id not in self._items:
            raise ValueError("Entity not found")
        self._items[entity.id] = entity
        return entity

    def delete(self, id: int) -> None:
        if id not in self._items:
            raise ValueError("Entity not found")
        del self._items[id]

    def find(self, specification: Specification[T]) -> List[T]:
        return [item for item in self._items.values() 
                if specification.is_satisfied_by(item)]
