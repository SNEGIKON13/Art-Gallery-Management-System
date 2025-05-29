from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from domain.models import Exhibition

class IExhibitionService(ABC):
    @abstractmethod
    def create_exhibition(self, title: str, description: str, 
                         start_date: datetime, end_date: datetime,
                         max_capacity: Optional[int] = None) -> Exhibition:
        """Создает новую выставку"""
        pass

    @abstractmethod
    def update_exhibition(self, exhibition_id: int, title: Optional[str] = None,
                         description: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         max_capacity: Optional[int] = None) -> Exhibition:
        """Обновляет информацию о выставке"""
        pass

    @abstractmethod
    def delete_exhibition(self, exhibition_id: int) -> None:
        """Удаляет выставку"""
        pass

    @abstractmethod
    def add_artwork(self, exhibition_id: int, artwork_id: int) -> None:
        """Добавляет экспонат в выставку"""
        pass

    @abstractmethod
    def remove_artwork(self, exhibition_id: int, artwork_id: int) -> None:
        """Удаляет экспонат из выставки"""
        pass

    @abstractmethod
    def get_exhibition(self, exhibition_id: int) -> Optional[Exhibition]:
        """Получает выставку по id"""
        pass

    @abstractmethod
    def get_all_exhibitions(self) -> List[Exhibition]:
        """Получает все выставки"""
        pass

    @abstractmethod
    def get_active_exhibitions(self) -> List[Exhibition]:
        """Получает активные выставки"""
        pass

    @abstractmethod
    def check_availability(self, exhibition_id: int) -> bool:
        """Проверяет, есть ли свободные места на выставке"""
        pass
