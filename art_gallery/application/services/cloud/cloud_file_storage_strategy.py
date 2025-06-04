"""
Cloud file storage strategy implementation.
"""
import logging
from typing import Optional, Union, BinaryIO

from art_gallery.application.interfaces.cloud.i_file_storage_strategy import IFileStorageStrategy
from art_gallery.infrastructure.interfaces.cloud.i_storage_service import IStorageService
from art_gallery.infrastructure.exceptions.cloud_exceptions import CloudStorageError


class CloudFileStorageStrategy(IFileStorageStrategy):
    """Implementation of file storage strategy that uses cloud storage service."""
    
    def __init__(self, storage_service: IStorageService, default_bucket_name: str):
        """
        Initialize cloud file storage strategy.
        
        Args:
            storage_service: Storage service implementation for cloud storage
            default_bucket_name: The default bucket name to use for operations
        """
        self.storage_service = storage_service
        self.default_bucket_name = default_bucket_name
        self.logger = logging.getLogger(__name__)
    
    def upload_file(self, entity_id: int, file_data: Union[bytes, BinaryIO], filename: str) -> Optional[str]:
        """
        Upload a file to cloud storage.
        
        Args:
            entity_id: ID of the entity (artwork, exhibition, etc.)
            file_data: File contents as bytes or file-like object
            filename: Original filename
            
        Returns:
            Optional[str]: Path to the stored file or None if failed
        """
        try:
            # Convert entity_id to string for the cloud storage
            entity_id_str = str(entity_id)
            
            # Формируем путь для хранения файла
            object_path = f"artworks/{entity_id_str}/{filename}"
            
            # Определяем тип контента на основе расширения файла
            content_type = "application/octet-stream"  # По умолчанию
            if filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif filename.lower().endswith('.png'):
                content_type = "image/png"
            elif filename.lower().endswith('.gif'):
                content_type = "image/gif"
            
            # Используем storage_service для загрузки файла
            success = self.storage_service.upload_data(
                bucket_name=self.default_bucket_name,
                object_name=object_path,
                data=file_data,
                content_type=content_type
            )
            
            if success:
                self.logger.info(f"Successfully uploaded file for entity {entity_id} to cloud storage")
                # Возвращаем путь к файлу в облачном хранилище
                return object_path
            else:
                self.logger.error(f"Failed to upload file for entity {entity_id} to cloud storage")
                return None
            
        except CloudStorageError as e:
            self.logger.error(f"Cloud storage error while uploading file for entity {entity_id}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error uploading file for entity {entity_id}: {str(e)}")
            return None
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """
        Get a URL to access the file from cloud storage.
        
        Args:
            file_path: Path to the file in cloud storage
            
        Returns:
            Optional[str]: URL to the file or None if not found
        """
        try:
            # Весь URL, включая имя бакета и объекта
            url = self.storage_service.get_object_url(
                bucket_name=self.default_bucket_name,
                object_name=file_path,
                expires=3600
            )
            
            if url:
                self.logger.debug(f"Generated URL for file: {file_path}")
            else:
                self.logger.warning(f"Could not generate URL for file: {file_path}")
                
            return url
            
        except CloudStorageError as e:
            self.logger.error(f"Cloud storage error getting URL for file {file_path}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting URL for file {file_path}: {str(e)}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from cloud storage.
        
        Args:
            file_path: Path to the file in cloud storage
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            success = self.storage_service.delete_object(
                bucket_name=self.default_bucket_name,
                object_name=file_path
            )
            
            if success:
                self.logger.info(f"Successfully deleted file: {file_path}")
            else:
                self.logger.error(f"Failed to delete file: {file_path}")
                
            return success
            
        except CloudStorageError as e:
            self.logger.error(f"Cloud storage error deleting file {file_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting file {file_path}: {str(e)}")
            return False
