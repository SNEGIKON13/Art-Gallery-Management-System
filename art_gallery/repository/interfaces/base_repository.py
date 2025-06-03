from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from art_gallery.domain.base_entity import BaseEntity
from art_gallery.repository.specifications.base_specification import Specification 

T = TypeVar('T', bound=BaseEntity)

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
    def update(self, entity: T) -> T:
        """Обновить существующую сущность"""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """Удалить сущность по id"""
        pass

    @abstractmethod
    def find(self, specification: Specification[T]) -> List[T]:
        """Найти сущности по спецификации"""
        pass
