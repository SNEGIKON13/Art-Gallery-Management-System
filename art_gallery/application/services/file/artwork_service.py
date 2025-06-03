from datetime import datetime
from typing import List, Optional, Union, BinaryIO
import logging

from art_gallery.domain.artwork import Artwork, ArtworkType
from art_gallery.repository.interfaces.base_repository import IBaseRepository
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy

class ArtworkService(IArtworkService):
    def __init__(self, artwork_repository: IBaseRepository[Artwork], 
                 file_storage_strategy: Optional[IFileStorageStrategy] = None):
        self._repository = artwork_repository
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
        artwork = self._repository.get_by_id(artwork_id)
        if not artwork:
            raise ValueError(f"Artwork with id {artwork_id} not found")
            
        # Delete associated image file if it exists and we have storage strategy
        if self._file_storage_strategy and artwork.image_path:
            try:
                self._file_storage_strategy.delete_file(artwork.image_path)
                self._logger.info(f"Deleted image file for artwork {artwork_id}: {artwork.image_path}")
            except Exception as e:
                self._logger.error(f"Failed to delete image file for artwork {artwork_id}: {str(e)}")
                
        # Delete the artwork from repository
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
        
    def add_imported_artwork(self, title: str, artist: str, year: int, 
                          description: str, type: ArtworkType, 
                          image_path: Optional[str] = None, 
                          created_at: Optional[datetime] = None, 
                          id: Optional[int] = None) -> Artwork:
        """
        Добавляет импортированный экспонат с заданными значениями полей.
        Отличие от add_artwork в том, что позволяет устанавливать дополнительные поля, 
        такие как created_at и id, что необходимо при импорте данных.
        """
        # Создаем объект с указанными параметрами
        artwork = Artwork(
            title=title,
            artist=artist,
            year=year,
            description=description,
            type=type,
            image_path=image_path,
            created_at=created_at or datetime.now()
        )
        
        # Устанавливаем ID, если он предоставлен
        if id is not None:
            artwork.id = id
            
        # Проверяем, существует ли уже экспонат с таким ID
        if id is not None and self._repository.get_by_id(id):
            # Если существует, выполняем обновление
            return self._repository.update(artwork)
        else:
            # Если не существует, добавляем новый
            return self._repository.add(artwork)
            
    def add_artwork_with_image(self, title: str, artist: str, year: int,
                             description: str, type: ArtworkType,
                             image_data: Union[bytes, BinaryIO], image_filename: str) -> Artwork:
        """
        Добавляет новый экспонат с изображением.
        
        Args:
            title: Название экспоната
            artist: Автор экспоната
            year: Год создания
            description: Описание экспоната
            type: Тип экспоната
            image_data: Данные изображения (байты или файловый объект)
            image_filename: Имя файла изображения
            
        Returns:
            Artwork: Добавленный экспонат
            
        Raises:
            ValueError: Если не удалось загрузить изображение или не указана стратегия хранения
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
            return self.add_artwork(title, artist, year, description, type)
    
    def update_artwork_image(self, artwork_id: int, image_data: Union[bytes, BinaryIO], 
                           image_filename: str) -> Artwork:
        """
        Обновляет изображение существующего экспоната.
        
        Args:
            artwork_id: ID экспоната
            image_data: Данные изображения
            image_filename: Имя файла изображения
            
        Returns:
            Artwork: Обновленный экспонат
            
        Raises:
            ValueError: Если экспонат не найден или не указана стратегия хранения
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
        
        Args:
            artwork_id: ID экспоната
            
        Returns:
            Optional[str]: URL изображения или None, если изображения нет
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
