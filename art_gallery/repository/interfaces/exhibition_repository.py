from abc import abstractmethod
from typing import List
from datetime import datetime
from domain import Exhibition
from .base_repository import IBaseRepository

class IExhibitionRepository(IBaseRepository[Exhibition]):
    @abstractmethod
    def get_active(self) -> List[Exhibition]:
        """Получить все активные выставки"""
        pass

    @abstractmethod
    def get_by_date_range(self, start: datetime, end: datetime) -> List[Exhibition]:
        """Получить выставки в заданном временном промежутке"""
        pass
