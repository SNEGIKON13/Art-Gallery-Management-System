from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from art_gallery.domain.base_entity import BaseEntity

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
        if self.year < 1 or self.year > datetime.now().year:
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

    def _get_entity_data(self) -> Dict[str, Any]:
        """Получает данные экспоната для сериализации"""
        return {
            'title': self.title,
            'artist': self.artist,
            'year': self.year,
            'description': self.description,
            'type': self.type.value,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat()
        }
        
    def clone(self) -> 'Artwork':
        """Создает глубокую копию объекта"""
        artwork = Artwork(
            title=self.title,
            artist=self.artist,
            year=self.year,
            description=self.description,
            type=self.type,
            image_path=self.image_path
        )
        artwork.created_at = self.created_at
        artwork.id = self.id
        return artwork
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artwork':
        """Создает объект Artwork из словаря"""
        # Обработка обязательных полей
        title = data['title']
        artist = data['artist']
        year = int(data['year']) if isinstance(data['year'], str) else data['year']
        description = data['description']
        
        # Обработка типа произведения искусства
        type_data = data['type']
        if isinstance(type_data, str):
            try:
                artwork_type = ArtworkType(type_data)
            except ValueError:
                # Если строка не совпадает с точным значением, пробуем с учетом регистра
                artwork_type = ArtworkType[type_data.upper()]
        else:
            artwork_type = type_data
        
        # Обработка опционального пути к изображению
        image_path = data.get('image_path')
        
        # Обработка даты создания
        created_at_str = data.get('created_at')
        created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
        
        # Создание объекта
        artwork = cls(
            title=title,
            artist=artist,
            year=year,
            description=description,
            type=artwork_type,
            image_path=image_path,
            created_at=created_at
        )
        
        # Установка ID, если он есть в данных и валидный
        if 'id' in data:
            try:
                id_value = int(data['id'])
                if id_value > 0:
                    artwork.id = id_value
            except (ValueError, TypeError):
                # Если ID не может быть преобразован в int или невалидный, игнорируем его
                pass
            
        return artwork
