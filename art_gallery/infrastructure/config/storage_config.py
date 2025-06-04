import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class StorageConfig:
    """Конфигурация для хранилища файлов"""
    
    # Тип хранилища: 'local' или 'cloud'
    storage_type: str = 'local'
    
    # Путь к локальному хранилищу
    local_storage_path: str = os.path.join('media', 'artworks')
    
    # Настройки функциональности
    enable_image_thumbnails: bool = True
    enable_direct_urls: bool = True
    enable_caching: bool = False
    
    # Срок действия временных URL (в секундах)
    presigned_url_expiry: int = 3600
    
    @classmethod
    def from_env(cls) -> 'StorageConfig':
        """Создает конфигурацию из переменных окружения"""
        return cls(
            storage_type=os.getenv('STORAGE_TYPE', 'local'),
            local_storage_path=os.getenv('LOCAL_STORAGE_PATH', os.path.join('media', 'artworks')),
            enable_image_thumbnails=os.getenv('ENABLE_IMAGE_THUMBNAILS', '1') == '1',
            enable_direct_urls=os.getenv('ENABLE_DIRECT_URLS', '1') == '1',
            enable_caching=os.getenv('ENABLE_CACHING', '0') == '1',
            presigned_url_expiry=int(os.getenv('PRESIGNED_URL_EXPIRY', '3600'))
        )
