from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any

@dataclass
class BaseEntity(ABC):
    """Базовый класс для всех сущностей"""
    _id: int = field(default=0, init=False)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        if value <= 0:
            raise ValueError("ID must be positive")
        self._id = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует сущность в словарь"""
        return {
            'id': self.id,
            **self._get_entity_data()
        }
    
    @abstractmethod
    def _get_entity_data(self) -> Dict[str, Any]:
        """
        Получает специфичные для сущности данные
        Должен быть реализован в каждом наследнике
        """
        pass
