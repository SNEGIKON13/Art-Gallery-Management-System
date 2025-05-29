from datetime import datetime
from typing import List, Optional, Union
from domain.models.artwork import Artwork, ArtworkType
from repository.interfaces.base_repository import IBaseRepository
from application.interfaces.artwork_service import IArtworkService

class ArtworkService(IArtworkService):
    def __init__(self, artwork_repository: IBaseRepository[Artwork]):
        self._repository = artwork_repository

    def add_artwork(self, title: str, artist: str, year: int,
                   description: str, type: ArtworkType,
                   image_path: Optional[str] = None) -> Artwork:
        artwork = Artwork(
            title=title,
            artist=artist,
            year=year,
            description=description,
            type=type,
            image_path=image_path,
            created_at=datetime.now()
        )
        return self._repository.add(artwork)

    def update_artwork(self, artwork_id: int, 
                      title: Optional[str] = None,
                      artist: Optional[str] = None, 
                      year: Optional[int] = None,
                      description: Optional[str] = None,
                      type: Optional[ArtworkType] = None,
                      image_path: Optional[str] = None) -> Artwork:
        artwork = self._repository.get_by_id(artwork_id)
        if not artwork:
            raise ValueError(f"Artwork with id {artwork_id} not found")

        if title is not None:
            artwork.title = title
        if artist is not None:
            artwork.artist = artist
        if year is not None:
            artwork.year = year
        if description is not None:
            artwork.description = description
        if type is not None:
            artwork.type = type
        if image_path is not None:
            artwork.image_path = image_path

        artwork._validate()
        return self._repository.update(artwork)

    def delete_artwork(self, artwork_id: int) -> None:
        if not self._repository.get_by_id(artwork_id):
            raise ValueError(f"Artwork with id {artwork_id} not found")
        self._repository.delete(artwork_id)

    def get_artwork(self, artwork_id: int) -> Optional[Artwork]:
        return self._repository.get_by_id(artwork_id)

    def get_all_artworks(self) -> List[Artwork]:
        return self._repository.get_all()

    def filter_by_type(self, artwork_type: ArtworkType) -> List[Artwork]:
        return [
            artwork for artwork in self._repository.get_all()
            if artwork.type == artwork_type
        ]

    def filter_by_year(self, start_year: int, end_year: Optional[int] = None) -> List[Artwork]:
        if end_year is None:
            end_year = start_year

        if start_year > end_year:
            raise ValueError("Start year cannot be greater than end year")

        return [
            artwork for artwork in self._repository.get_all()
            if start_year <= artwork.year <= end_year
        ]
