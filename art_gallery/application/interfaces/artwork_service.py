from abc import ABC, abstractmethod
from typing import List, Optional, Union
from datetime import datetime
from art_gallery.domain.artwork import Artwork, ArtworkType

class IArtworkService(ABC):
    @abstractmethod
    def add_artwork(self, title: str, artist: str, year: int, 
                   description: str, type: ArtworkType, 
                   image_path: Optional[str] = None) -> Artwork:
        """Добавляет новый экспонат"""
        pass

    @abstractmethod
    def update_artwork(self, artwork_id: int, 
                      title: Optional[str] = None,
                      artist: Optional[str] = None, 
                      year: Optional[int] = None,
                      description: Optional[str] = None,
                      type: Optional[ArtworkType] = None,
                      image_path: Optional[str] = None) -> Artwork:
        """Обновляет существующий экспонат"""
        pass

    @abstractmethod
    def delete_artwork(self, artwork_id: int) -> None:
        """Удаляет экспонат"""
        pass

    @abstractmethod
    def get_artwork(self, artwork_id: int) -> Optional[Artwork]:
        """Получает экспонат по id"""
        pass

    @abstractmethod
    def get_all_artworks(self) -> List[Artwork]:
        """Получает все экспонаты"""
        pass

    @abstractmethod
    def filter_by_type(self, artwork_type: ArtworkType) -> List[Artwork]:
        """Фильтрует экспонаты по типу"""
        pass

    @abstractmethod
    def filter_by_year(self, start_year: int, end_year: Optional[int] = None) -> List[Artwork]:
        """Фильтрует экспонаты по году создания"""
        pass
        
    @abstractmethod
    def add_imported_artwork(self, title: str, artist: str, year: int, 
                          description: str, type: ArtworkType, 
                          image_path: Optional[str] = None, 
                          created_at: Optional[datetime] = None, 
                          id: Optional[int] = None) -> Artwork:
        """
        Добавляет импортированный экспонат с заданными значениями полей.
        Отличие от add_artwork в том, что позволяет устанавливать дополнительные поля, 
        такие как created_at и id, что необходимо при импорте данных.
        """
        pass
