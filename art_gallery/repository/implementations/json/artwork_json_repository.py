import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain.models import Artwork, ArtworkType
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.specifications.base_specification import Specification

class ArtworkJsonRepository(IArtworkRepository):
    def __init__(self, filepath: str):
        self._filepath = filepath
        # Создаем директорию, если нужно
        file_dir = os.path.dirname(self._filepath)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        self._artworks: List[Artwork] = []
        self._load_data()

    def _load_data(self) -> None:
        if not os.path.exists(self._filepath) or os.path.getsize(self._filepath) == 0:
            self._artworks = []
            # Создаем пустой файл, если не существует
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return
        
        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Загружаем артефакты из данных
                loaded_artworks = []
                for artwork_data in data:
                    try:
                        loaded_artworks.append(Artwork.from_dict(artwork_data))
                    except Exception as e:
                        print(f"Error deserializing artwork: {e}")
                self._artworks = loaded_artworks
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self._filepath}. Starting with empty artwork list.")
            self._artworks = []
        except Exception as e:
            print(f"Error loading artworks: {e}")
            self._artworks = []

    def _save_data(self) -> None:
        try:
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump([artwork.to_dict() for artwork in self._artworks], f, indent=4, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving artworks: {e}")

    def add(self, artwork: Artwork) -> Artwork:
        # Генерация нового ID
        if not self._artworks:
            new_id = 0  # Или 1, если предпочитаете начинать с 1
        else:
            # Находим максимальный ID среди существующих арт-объектов
            # Убедимся, что у всех арт-объектов есть ID (на случай поврежденных данных)
            existing_ids = [art.id for art in self._artworks if hasattr(art, 'id') and art.id is not None]
            if not existing_ids:
                new_id = 0 # Или 1
            else:
                new_id = max(existing_ids) + 1
        
        artwork.id = new_id # Присваиваем сгенерированный ID
        
        # Добавляем артефакт и сохраняем
        self._artworks.append(artwork)
        self._save_data()
        return artwork

    def get_by_id(self, artwork_id: int) -> Optional[Artwork]:
        return next((artwork for artwork in self._artworks if artwork.id == artwork_id), None)
        
    def get_all(self) -> List[Artwork]:
        return list(self._artworks)
        
    def update(self, artwork_to_update: Artwork) -> Artwork:
        for i, artwork in enumerate(self._artworks):
            if artwork.id == artwork_to_update.id:
                self._artworks[i] = artwork_to_update
                self._save_data()
                return artwork_to_update
        raise ValueError(f"Artwork with id {artwork_to_update.id} not found.")
        
    def delete(self, artwork_id: int) -> None:
        artwork = self.get_by_id(artwork_id)
        if artwork:
            self._artworks.remove(artwork)
            self._save_data()
            
    def find(self, specification: Specification[Artwork]) -> List[Artwork]:
        """
        Найти экспонаты, соответствующие спецификации
        """
        return [artwork for artwork in self._artworks if specification.is_satisfied_by(artwork)]
        
    def get_by_artist(self, artist: str) -> List[Artwork]:
        """
        Получить все работы художника
        Args:
            artist (str): имя художника (регистр не имеет значения)
        Returns:
            List[Artwork]: список работ художника
        """
        return [artwork for artwork in self._artworks if artwork.artist.lower() == artist.lower()]
    
    def get_by_type(self, type: ArtworkType) -> List[Artwork]:
        """
        Получить все работы определенного типа
        Args:
            type (ArtworkType): тип работы
        Returns:
            List[Artwork]: список работ указанного типа
        """
        return [artwork for artwork in self._artworks if artwork.type == type]
        # Метод просто не делает ничего, если экспонат не найден
        # и возвращает None в соответствии с интерфейсом
