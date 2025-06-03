"""
Сервис для управления медиафайлами через MinIO.
Предоставляет методы для загрузки, получения и удаления изображений экспонатов.
"""
import io
import os
import uuid
from typing import Optional, BinaryIO, Tuple
from pathlib import Path

from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.storage.minio_service import MinioService


class MediaService:
    """
    Сервис для управления медиафайлами через MinIO.
    Предоставляет методы для работы с изображениями экспонатов.
    """

    def __init__(self, minio_service: MinioService = None, config: MinioConfig = None):
        """
        Инициализирует сервис для работы с медиафайлами.
        
        Args:
            minio_service: Сервис для работы с MinIO. Если не указан, создается новый.
            config: Конфигурация для подключения к MinIO. Используется, если minio_service не указан.
        """
        self.config = config or MinioConfig()
        self.minio_service = minio_service or MinioService(self.config)
        
        # Убедимся, что бакет для медиафайлов существует
        self.minio_service.ensure_bucket_exists(self.config.MEDIA_BUCKET)

    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Генерирует уникальное имя файла на основе UUID и оригинального расширения.
        
        Args:
            original_filename: Оригинальное имя файла.
            
        Returns:
            str: Уникальное имя файла.
        """
        # Получаем расширение файла
        _, extension = os.path.splitext(original_filename)
        # Генерируем уникальное имя
        unique_name = f"{uuid.uuid4()}{extension}"
        return unique_name

    def upload_artwork_image(self, artwork_id: str, image_data: bytes or BinaryIO, 
                            original_filename: str) -> Optional[str]:
        """
        Загружает изображение для экспоната.
        
        Args:
            artwork_id: ID экспоната.
            image_data: Данные изображения (байты или файлоподобный объект).
            original_filename: Оригинальное имя файла.
            
        Returns:
            Optional[str]: Путь к изображению в MinIO или None, если загрузка не удалась.
        """
        try:
            # Генерируем уникальное имя файла
            unique_filename = self.generate_unique_filename(original_filename)
            
            # Формируем путь к изображению в MinIO
            object_path = f"{self.config.ARTWORKS_MEDIA_PREFIX}{artwork_id}/{unique_filename}"
            
            # Определяем MIME-тип на основе расширения
            content_type = self._get_content_type_by_extension(original_filename)
            
            # Загружаем изображение
            success = self.minio_service.upload_data(
                bucket_name=self.config.MEDIA_BUCKET,
                object_name=object_path,
                data=image_data,
                content_type=content_type
            )
            
            if success:
                return object_path
            return None
        except Exception as e:
            print(f"Ошибка при загрузке изображения для экспоната {artwork_id}: {e}")
            return None

    def get_artwork_image(self, image_path: str) -> Optional[bytes]:
        """
        Получает изображение экспоната по пути.
        
        Args:
            image_path: Путь к изображению в MinIO.
            
        Returns:
            Optional[bytes]: Данные изображения или None, если изображение не найдено.
        """
        try:
            return self.minio_service.download_data(
                bucket_name=self.config.MEDIA_BUCKET,
                object_name=image_path
            )
        except Exception as e:
            print(f"Ошибка при получении изображения по пути {image_path}: {e}")
            return None

    def delete_artwork_image(self, image_path: str) -> bool:
        """
        Удаляет изображение экспоната.
        
        Args:
            image_path: Путь к изображению в MinIO.
            
        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        try:
            return self.minio_service.delete_object(
                bucket_name=self.config.MEDIA_BUCKET,
                object_name=image_path
            )
        except Exception as e:
            print(f"Ошибка при удалении изображения по пути {image_path}: {e}")
            return False

    def get_artwork_image_url(self, image_path: str, expires: int = 7 * 24 * 60 * 60) -> Optional[str]:
        """
        Получает URL для доступа к изображению экспоната.
        
        Args:
            image_path: Путь к изображению в MinIO.
            expires: Время жизни URL в секундах (по умолчанию 7 дней).
            
        Returns:
            Optional[str]: URL для доступа к изображению или None, если произошла ошибка.
        """
        try:
            return self.minio_service.get_object_url(
                bucket_name=self.config.MEDIA_BUCKET,
                object_name=image_path,
                expires=expires
            )
        except Exception as e:
            print(f"Ошибка при получении URL для изображения по пути {image_path}: {e}")
            return None

    def list_artwork_images(self, artwork_id: str) -> list:
        """
        Получает список изображений экспоната.
        
        Args:
            artwork_id: ID экспоната.
            
        Returns:
            list: Список путей к изображениям экспоната.
        """
        try:
            prefix = f"{self.config.ARTWORKS_MEDIA_PREFIX}{artwork_id}/"
            objects = self.minio_service.list_objects(
                bucket_name=self.config.MEDIA_BUCKET,
                prefix=prefix
            )
            return [obj['name'] for obj in objects]
        except Exception as e:
            print(f"Ошибка при получении списка изображений для экспоната {artwork_id}: {e}")
            return []

    def _get_content_type_by_extension(self, filename: str) -> str:
        """
        Определяет MIME-тип на основе расширения файла.
        
        Args:
            filename: Имя файла.
            
        Returns:
            str: MIME-тип.
        """
        extension = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        return content_types.get(extension, 'application/octet-stream')
