from typing import List
from art_gallery.domain import Artwork, ArtworkType
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.implementations.base_memory_repository import BaseMemoryRepository

class ArtworkMemoryRepository(BaseMemoryRepository[Artwork], IArtworkRepository):
    def get_by_artist(self, artist: str) -> List[Artwork]:
        if not artist:
            raise ValueError("Artist name cannot be empty")
        return [artwork for artwork in self._items.values() 
                if artwork.artist.lower() == artist.lower()]

    def get_by_type(self, type: ArtworkType) -> List[Artwork]:
        if not isinstance(type, ArtworkType):
            raise ValueError("Invalid artwork type")
        return [artwork for artwork in self._items.values() 
                if artwork.type == type]
