from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class IBaseRepository(Generic[T], ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Получить сущность по id"""
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Получить все сущности"""
        pass

    @abstractmethod
    def add(self, entity: T) -> T:
        """Добавить новую сущность"""
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        """Обновить существующую сущность"""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """Удалить сущность по id"""
        pass
