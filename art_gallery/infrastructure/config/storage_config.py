import os
import pathlib
from dataclasses import dataclass
from typing import Optional

from .constants import (
    DEFAULT_STORAGE_TYPE,
    DEFAULT_LOCAL_STORAGE_PATH,
    DEFAULT_ENABLE_IMAGE_THUMBNAILS,
    DEFAULT_ENABLE_DIRECT_URLS,
    DEFAULT_ENABLE_CACHING,
    DEFAULT_PRESIGNED_URL_EXPIRY
)

@dataclass
class StorageConfig:
    """Конфигурация для хранилища файлов"""
    
    # Тип хранилища: 'local' или 'cloud'
    storage_type: str = DEFAULT_STORAGE_TYPE
    
    # Путь к локальному хранилищу
    local_storage_path: str = DEFAULT_LOCAL_STORAGE_PATH
    
    # Настройки функциональности
    enable_image_thumbnails: bool = DEFAULT_ENABLE_IMAGE_THUMBNAILS
    enable_direct_urls: bool = DEFAULT_ENABLE_DIRECT_URLS
    enable_caching: bool = DEFAULT_ENABLE_CACHING
    
    # Срок действия временных URL (в секундах)
    presigned_url_expiry: int = DEFAULT_PRESIGNED_URL_EXPIRY
    
    @classmethod
    def from_env(cls) -> 'StorageConfig':
        """Создает конфигурацию из переменных окружения"""
        # Получаем значения из переменных окружения с учетом значений по умолчанию
        storage_type = os.getenv('STORAGE_TYPE', DEFAULT_STORAGE_TYPE)
        local_storage_path = os.getenv('LOCAL_STORAGE_PATH', DEFAULT_LOCAL_STORAGE_PATH)
        
        # Приведение строковых значений к булевым
        enable_thumbnails_str = os.getenv('ENABLE_IMAGE_THUMBNAILS', str(int(DEFAULT_ENABLE_IMAGE_THUMBNAILS)))
        enable_direct_urls_str = os.getenv('ENABLE_DIRECT_URLS', str(int(DEFAULT_ENABLE_DIRECT_URLS)))
        enable_caching_str = os.getenv('ENABLE_CACHING', str(int(DEFAULT_ENABLE_CACHING)))
        
        enable_image_thumbnails = enable_thumbnails_str == '1' or enable_thumbnails_str.lower() == 'true'
        enable_direct_urls = enable_direct_urls_str == '1' or enable_direct_urls_str.lower() == 'true'
        enable_caching = enable_caching_str == '1' or enable_caching_str.lower() == 'true'
        
        # Приведение строкового значения к int с обработкой ошибок
        try:
            presigned_url_expiry = int(os.getenv('PRESIGNED_URL_EXPIRY', str(DEFAULT_PRESIGNED_URL_EXPIRY)))
        except ValueError:
            presigned_url_expiry = DEFAULT_PRESIGNED_URL_EXPIRY
            
        # Нормализация пути к локальному хранилищу
        if local_storage_path:
            local_storage_path = str(pathlib.Path(local_storage_path))
        
        return cls(
            storage_type=storage_type,
            local_storage_path=local_storage_path,
            enable_image_thumbnails=enable_image_thumbnails,
            enable_direct_urls=enable_direct_urls,
            enable_caching=enable_caching,
            presigned_url_expiry=presigned_url_expiry
        )
        
    def __post_init__(self):
        """Валидация конфигурации после инициализации"""
        # Проверка типа хранилища
        if self.storage_type not in ['local', 'cloud']:
            raise ValueError(f"Недопустимый тип хранилища: {self.storage_type}. Допустимые значения: 'local', 'cloud'")
        
        # Проверка срока действия временных URL
        if self.presigned_url_expiry <= 0:
            raise ValueError(f"Срок действия временных URL должен быть положительным числом, получено: {self.presigned_url_expiry}")
        
        # Проверка пути к локальному хранилищу для типа 'local'
        if self.storage_type == 'local' and not self.local_storage_path:
            raise ValueError("Путь к локальному хранилищу не указан, но тип хранилища установлен как 'local'")
            
    def get_absolute_local_path(self) -> str:
        """Возвращает абсолютный путь к локальному хранилищу"""
        if self.storage_type != 'local':
            raise ValueError("Невозможно получить локальный путь для типа хранилища отличного от 'local'")
            
        # Если путь относительный, преобразуем его в абсолютный
        path = pathlib.Path(self.local_storage_path)
        if not path.is_absolute():
            # Получаем путь относительно корня приложения
            root_dir = pathlib.Path(__file__).parent.parent.parent.parent
            path = root_dir / path
        
        return str(path)
