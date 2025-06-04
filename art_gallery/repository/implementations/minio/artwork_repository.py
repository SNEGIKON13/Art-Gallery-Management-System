"""
MinIO-реализация репозитория для экспонатов.
Реализует интерфейс IArtworkRepository с использованием MinIO для хранения данных.
"""
from typing import List, Dict, Any, Optional

from art_gallery.domain import Artwork, ArtworkType
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.implementations.minio.base_minio_repository import BaseMinioRepository
from art_gallery.repository.specifications.base_specification import Specification
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.cloud.minio_service import MinioService

from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer


class ArtworkMinioRepository(BaseMinioRepository[Artwork], IArtworkRepository):
    """
    MinIO-реализация репозитория для экспонатов.
    Наследуется от базового MinIO репозитория и реализует интерфейс IArtworkRepository.
    """

    def __init__(self, 
                 serializer: ISerializer, 
                 deserializer: IDeserializer,
                 minio_service: Optional[MinioService] = None,
                 config: Optional[MinioConfig] = None):
        """
        Инициализирует репозиторий экспонатов с использованием MinIO.
        
        Args:
            serializer: Сериализатор для преобразования данных в строку.
            deserializer: Десериализатор для преобразования строки в данные.
            minio_service: Сервис для работы с MinIO. Если не указан, создается новый.
            config: Конфигурация для подключения к MinIO. Используется, если minio_service не указан.
        """
        self._config = config or MinioConfig.from_env()
        
        self.ENTITY_TYPE_STR = "artwork"
        file_extension = "xml" if serializer.__class__.__name__ == 'XMLSerializer' else "json"

        # Construct the object path using the prefix and file extension
        base_filename = f"{self.ENTITY_TYPE_STR}.{file_extension}"
        object_path = f"{self._config.get_prefix_for_entity_type(self.ENTITY_TYPE_STR)}{base_filename}"

        super().__init__(
            bucket_name=self._config.default_bucket,
            object_path=object_path,
            serializer=serializer,
            deserializer=deserializer,
            minio_service=minio_service,
            config=self._config
        )

    def _create_entity_from_dict(self, data: Dict[str, Any]) -> Artwork:
        """
        Создает экспонат из словаря.
        
        Args:
            data: Словарь с данными экспоната.
            
        Returns:
            Artwork: Созданный экспонат.
        """
        return Artwork.from_dict(data)

    def get_by_artist(self, artist: str) -> List[Artwork]:
        """
        Получает все работы художника.
        
        Args:
            artist: Имя художника (регистр не имеет значения).
            
        Returns:
            List[Artwork]: Список работ художника.
        """
        return [artwork for artwork in self._items.values() 
                if artwork.artist.lower() == artist.lower()]

    def get_by_type(self, type: ArtworkType) -> List[Artwork]:
        """
        Получает все работы определенного типа.
        
        Args:
            type: Тип работы.
            
        Returns:
            List[Artwork]: Список работ указанного типа.
        """
        return [artwork for artwork in self._items.values() 
                if artwork.type == type]
