from abc import ABC
from dataclasses import dataclass, field

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
