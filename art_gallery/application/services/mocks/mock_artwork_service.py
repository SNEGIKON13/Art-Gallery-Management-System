from typing import List, Optional, Dict
from datetime import datetime
from art_gallery.domain.artwork import Artwork, ArtworkType
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
                
    def add_imported_artwork(self, title: str, artist: str, year: int, 
                          description: str, type: ArtworkType, 
                          image_path: Optional[str] = None, 
                          created_at: Optional[datetime] = None, 
                          id: Optional[int] = None) -> Artwork:
        """
        Добавляет импортированный экспонат с заданными значениями полей.
        """
        # Убедимся, что created_at имеет правильный тип
        if created_at is None:
            artwork_created_at = datetime.now()
        else:
            artwork_created_at = created_at
            
        artwork = Artwork(
            title=title,
            artist=artist,
            year=year,
            description=description,
            type=type,
            image_path=image_path,
            created_at=artwork_created_at
        )
        
        # Если задан ID, используем его, иначе генерируем новый
        if id is not None:
            artwork.id = id
            # Если существует экспонат с таким ID, обновляем
            if id in self._artworks:
                self._artworks[id] = artwork
                return artwork
            # В противном случае добавляем с указанным ID
            self._artworks[id] = artwork
            # Обновляем next_id если необходимо
            if id >= self._next_id:
                self._next_id = id + 1
        else:
            # Если ID не задан, генерируем новый
            artwork.id = self._next_id
            self._artworks[self._next_id] = artwork
            self._next_id += 1
            
        return artwork
