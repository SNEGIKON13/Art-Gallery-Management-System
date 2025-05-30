from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from art_gallery.domain.models.base_entity import BaseEntity

class ArtworkType(Enum):
    PAINTING = "painting"
    SCULPTURE = "sculpture"
    PHOTOGRAPH = "photograph"

@dataclass
class Artwork(BaseEntity):
    title: str
    artist: str
    year: int
    description: str
    type: ArtworkType
    image_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.title or len(self.title) < 1:
            raise ValueError("Title cannot be empty")
        if not self.artist or len(self.artist) < 1:
            raise ValueError("Artist cannot be empty")
        if self.year < 1000 or self.year > datetime.now().year:
            raise ValueError("Invalid year")
        if not self.description:
            raise ValueError("Description cannot be empty")

    def update_info(self, title: Optional[str] = None, 
                   artist: Optional[str] = None,
                   year: Optional[int] = None, 
                   description: Optional[str] = None) -> None:
        """Обновляет основную информацию об экспонате"""
        if title is not None:
            self.title = title
        if artist is not None:
            self.artist = artist
        if year is not None:
            self.year = year
        if description is not None:
            self.description = description
        self._validate()

    def update_image(self, new_image_path: str) -> None:
        """Обновляет путь к изображению экспоната"""
        self.image_path = new_image_path

    def change_type(self, new_type: ArtworkType) -> None:
        """Изменяет тип экспоната"""
        self.type = new_type
        self._validate()

    def is_contemporary(self) -> bool:
        """Проверяет, является ли произведение современным (не старше 50 лет)"""
        current_year = datetime.now().year
        return (current_year - self.year) <= 50

    def __eq__(self, other: object) -> bool:
        """Сравнивает экспонаты по id"""
        if not isinstance(other, Artwork):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Хеширует экспонат по id"""
        return hash(self.id)
