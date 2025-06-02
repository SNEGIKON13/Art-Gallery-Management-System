import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain.models import Artwork, ArtworkType
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.specifications.base_specification import Specification
from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

class ArtworkJsonRepository(IArtworkRepository):
    def __init__(self, filepath: str, serializer: ISerializer, deserializer: IDeserializer):
        self._filepath = filepath
        self._serializer = serializer  # Сериализатор из плагина
        self._deserializer = deserializer  # Десериализатор из плагина
        
        # Создаем директорию, если нужно
        file_dir = os.path.dirname(self._filepath)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        self._artworks: List[Artwork] = []
        self._load_data()

    def _load_data(self) -> None:
        try:
            # Используем десериализатор из плагина
            list_of_dicts = self._deserializer.deserialize_from_file(self._filepath)
            loaded_artworks = []
            for artwork_data_dict in list_of_dicts:
                try:
                    loaded_artworks.append(Artwork.from_dict(artwork_data_dict))
                except Exception as e:
                    print(f"Error creating Artwork from dict: {artwork_data_dict}, error: {e}")
                    # TODO: Заменить на логирование
            self._artworks = loaded_artworks
        except Exception as e:
            # В случае ошибки считаем, что данных нет
            print(f"Error loading data from {self._filepath} using deserializer: {e}")
            # TODO: Заменить на логирование
            self._artworks = []

    def _save_data(self) -> None:
        try:
            # Используем сериализатор из плагина
            data_to_serialize = [artwork.to_dict() for artwork in self._artworks]
            self._serializer.serialize_to_file(data_to_serialize, self._filepath)
        except Exception as e:
            print(f"Error saving data to {self._filepath} using serializer: {e}")
            # TODO: Заменить на логирование

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
