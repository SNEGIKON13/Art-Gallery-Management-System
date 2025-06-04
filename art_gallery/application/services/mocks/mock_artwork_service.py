from typing import List, Optional, Dict, Union, BinaryIO
from datetime import datetime
import logging

from art_gallery.domain.artwork import Artwork, ArtworkType
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy

class MockArtworkService(IArtworkService):
    def __init__(self, file_storage_strategy: Optional[IFileStorageStrategy] = None):
        self._artworks: Dict[int, Artwork] = {}
        self._next_id = 1
        self._file_storage_strategy = file_storage_strategy
        self._logger = logging.getLogger(__name__)

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
    
    def add_artwork_with_image(self, title: str, artist: str, year: int,
                             description: str, type: ArtworkType,
                             image_data: Union[bytes, BinaryIO], image_filename: str) -> Artwork:
        """
        Добавляет новый экспонат с изображением.
        """
        # Проверяем, доступна ли стратегия хранения файлов
        if not self._file_storage_strategy:
            self._logger.warning("No file storage strategy configured. Adding artwork without image.")
            return self.add_artwork(title, artist, year, description, type)
            
        try:
            # Создаем экспонат без изображения
            artwork = self.add_artwork(title, artist, year, description, type)
            
            # Загружаем изображение
            image_path = self._file_storage_strategy.upload_file(
                entity_id=artwork.id,
                file_data=image_data,
                filename=image_filename
            )
            
            if not image_path:
                self._logger.error(f"Failed to upload image for artwork ID {artwork.id}")
                return artwork
                
            # Обновляем экспонат с путем к изображению
            artwork = self.update_artwork(artwork.id, image_path=image_path)
            self._logger.info(f"Added artwork with image: {artwork.id}, image path: {image_path}")
            return artwork
            
        except Exception as e:
            self._logger.error(f"Error adding artwork with image: {str(e)}")
            # В случае ошибки возвращаем экспонат без изображения
            return artwork
    
    def update_artwork_image(self, artwork_id: int, image_data: Union[bytes, BinaryIO], 
                           image_filename: str) -> Artwork:
        """
        Обновляет изображение существующего экспоната.
        """
        # Получаем экспонат
        artwork = self.get_artwork(artwork_id)
        if not artwork:
            raise ValueError(f"Artwork with id {artwork_id} not found")
            
        # Проверяем, доступна ли стратегия хранения файлов
        if not self._file_storage_strategy:
            raise ValueError("No file storage strategy configured")
            
        try:
            # Удаляем предыдущее изображение, если оно есть
            if artwork.image_path:
                try:
                    self._file_storage_strategy.delete_file(artwork.image_path)
                    self._logger.info(f"Deleted previous image for artwork {artwork_id}: {artwork.image_path}")
                except Exception as e:
                    self._logger.warning(f"Failed to delete previous image: {str(e)}")
            
            # Загружаем новое изображение
            image_path = self._file_storage_strategy.upload_file(
                entity_id=artwork_id,
                file_data=image_data,
                filename=image_filename
            )
            
            if not image_path:
                raise ValueError("Failed to upload image")
                
            # Обновляем экспонат с новым путем к изображению
            artwork = self.update_artwork(artwork_id, image_path=image_path)
            self._logger.info(f"Updated image for artwork {artwork_id}, new path: {image_path}")
            return artwork
            
        except Exception as e:
            self._logger.error(f"Error updating artwork image: {str(e)}")
            raise ValueError(f"Failed to update artwork image: {str(e)}")
    
    def get_artwork_image_url(self, artwork_id: int) -> Optional[str]:
        """
        Получает URL изображения экспоната.
        """
        # Получаем экспонат
        artwork = self.get_artwork(artwork_id)
        if not artwork or not artwork.image_path:
            return None
            
        # Проверяем, доступна ли стратегия хранения файлов
        if not self._file_storage_strategy:
            self._logger.warning(f"No file storage strategy configured. Cannot get URL for artwork {artwork_id}")
            return None
            
        try:
            # Получаем URL изображения
            image_url = self._file_storage_strategy.get_file_url(artwork.image_path)
            return image_url
        except Exception as e:
            self._logger.error(f"Error getting image URL for artwork {artwork_id}: {str(e)}")
            return None

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
