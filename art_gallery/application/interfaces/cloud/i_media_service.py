from abc import ABC, abstractmethod
from typing import Optional, BinaryIO

class IMediaService(ABC):
    @abstractmethod
    def upload_file(self, file_path: str, object_name: str) -> bool:
        """Загружает файл в хранилище"""
        pass

    @abstractmethod
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """Получает временную URL для доступа к объекту"""
        pass
        
    @abstractmethod
    def download_file(self, object_name: str, file_path: str) -> bool:
        """Скачивает файл из хранилища"""
        pass
        
    @abstractmethod
    def upload_bytes(self, data: bytes, object_name: str) -> bool:
        """Загружает данные из байтов"""
        pass
