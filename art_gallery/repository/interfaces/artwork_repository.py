from abc import abstractmethod
from typing import List
from art_gallery.domain.models import Artwork, ArtworkType
from art_gallery.repository.interfaces.base_repository import IBaseRepository

class IArtworkRepository(IBaseRepository[Artwork]):
    @abstractmethod
    def get_by_artist(self, artist: str) -> List[Artwork]:
        """
        Получить все работы художника
        Args:
            artist (str): имя художника (регистр не имеет значения)
        Returns:
            List[Artwork]: список работ художника
        """
        pass

    @abstractmethod
    def get_by_type(self, type: ArtworkType) -> List[Artwork]:
        """
        Получить все работы определенного типа
        Args:
            type (ArtworkType): тип работы
        Returns:
            List[Artwork]: список работ указанного типа
        """
        pass
