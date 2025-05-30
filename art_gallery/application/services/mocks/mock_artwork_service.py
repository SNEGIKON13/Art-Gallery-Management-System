from typing import List, Optional, Dict
from art_gallery.domain.models.artwork import Artwork, ArtworkType
from art_gallery.application.interfaces.artwork_service import IArtworkService

class MockArtworkService(IArtworkService):
    def __init__(self):
        self._artworks: Dict[int, Artwork] = {}
        self._next_id = 1

    def add_artwork(self, title: str, artist: str, year: int, 
                   description: str, type: ArtworkType, 
                   image_path: Optional[str] = None) -> Artwork:
        artwork = Artwork(
            title=title,
            artist=artist,
            year=year,
            description=description,
            type=type,
            image_path=image_path
        )
        # Устанавливаем ID до сохранения
        artwork.id = self._next_id
        self._artworks[self._next_id] = artwork
        self._next_id += 1
        return artwork

    def update_artwork(self, artwork_id: int, 
                      title: Optional[str] = None,
                      artist: Optional[str] = None, 
                      year: Optional[int] = None,
                      description: Optional[str] = None,
                      type: Optional[ArtworkType] = None,
                      image_path: Optional[str] = None) -> Artwork:
        if artwork_id not in self._artworks:
            raise ValueError("Artwork not found")
            
        artwork = self._artworks[artwork_id]
        if title: artwork.title = title
        if artist: artwork.artist = artist
        if year: artwork.year = year
        if description: artwork.description = description
        if type: artwork.type = type
        if image_path: artwork.image_path = image_path
        return artwork

    def delete_artwork(self, artwork_id: int) -> None:
        if artwork_id not in self._artworks:
            raise ValueError("Artwork not found")
        del self._artworks[artwork_id]

    def get_artwork(self, artwork_id: int) -> Optional[Artwork]:
        return self._artworks.get(artwork_id)

    def get_all_artworks(self) -> List[Artwork]:
        return list(self._artworks.values())

    def filter_by_type(self, artwork_type: ArtworkType) -> List[Artwork]:
        return [a for a in self._artworks.values() if a.type == artwork_type]

    def filter_by_year(self, start_year: int, end_year: Optional[int] = None) -> List[Artwork]:
        end_year = end_year or start_year
        return [a for a in self._artworks.values() 
                if start_year <= a.year <= end_year]
