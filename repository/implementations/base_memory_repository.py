from typing import Dict, List, Optional, TypeVar, Generic
from repository.interfaces.base_repository import IBaseRepository

T = TypeVar('T')

class BaseMemoryRepository(IBaseRepository[T], Generic[T]):
    def __init__(self):
        self._items: Dict[int, T] = {}
        self._next_id: int = 1

    def get_by_id(self, id: int) -> Optional[T]:
        return self._items.get(id)

    def get_all(self) -> List[T]:
        return list(self._items.values())

    def add(self, entity: T) -> T:
        setattr(entity, 'id', self._next_id)
        self._items[self._next_id] = entity
        self._next_id += 1
        return entity

    def update(self, entity: T) -> T:
        if not hasattr(entity, 'id') or entity.id not in self._items:
            raise ValueError("Entity not found")
        self._items[entity.id] = entity
        return entity

    def delete(self, id: int) -> None:
        if id in self._items:
            del self._items[id]
