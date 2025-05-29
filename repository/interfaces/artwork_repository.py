from abc import abstractmethod
from typing import List
from domain.models import Artwork, ArtworkType
from .base_repository import IBaseRepository

class IArtworkRepository(IBaseRepository[Artwork]):
    @abstractmethod
    def get_by_artist(self, artist: str) -> List[Artwork]:
        """Получить все работы художника"""
        pass

    @abstractmethod
    def get_by_type(self, type: ArtworkType) -> List[Artwork]:
        """Получить все работы определенного типа"""
        pass
