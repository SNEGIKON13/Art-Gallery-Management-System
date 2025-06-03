"""
MinIO-реализация репозитория для выставок.
Реализует интерфейс IExhibitionRepository с использованием MinIO для хранения данных.
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from art_gallery.domain.models import Exhibition
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.implementations.minio.base_minio_repository import BaseMinioRepository
from art_gallery.repository.specifications.base_specification import Specification
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.storage.minio_service import MinioService

from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer


class ExhibitionMinioRepository(BaseMinioRepository[Exhibition], IExhibitionRepository):
    """
    MinIO-реализация репозитория для выставок.
    Наследуется от базового MinIO репозитория и реализует интерфейс IExhibitionRepository.
    """

    def __init__(self, 
                 serializer: ISerializer, 
                 deserializer: IDeserializer,
                 minio_service: Optional[MinioService] = None,
                 config: Optional[MinioConfig] = None):
        """
        Инициализирует репозиторий выставок с использованием MinIO.
        
        Args:
            serializer: Сериализатор для преобразования данных в строку.
            deserializer: Десериализатор для преобразования строки в данные.
            minio_service: Сервис для работы с MinIO. Если не указан, создается новый.
            config: Конфигурация для подключения к MinIO. Используется, если minio_service не указан.
        """
        self._config = config or MinioConfig()
        
        # Определяем путь к объекту в зависимости от формата сериализации
        object_path = self._config.EXHIBITIONS_JSON_PATH
        if serializer.__class__.__name__ == 'XMLSerializer':
            object_path = self._config.EXHIBITIONS_XML_PATH
        
        super().__init__(
            bucket_name=self._config.DATA_BUCKET,
            object_path=object_path,
            serializer=serializer,
            deserializer=deserializer,
            minio_service=minio_service,
            config=self._config
        )

    def _create_entity_from_dict(self, data: Dict[str, Any]) -> Exhibition:
        """
        Создает выставку из словаря.
        
        Args:
            data: Словарь с данными выставки.
            
        Returns:
            Exhibition: Созданная выставка.
        """
        return Exhibition.from_dict(data)

    def get_active(self) -> List[Exhibition]:
        """
        Получает все активные выставки (текущая дата входит в период проведения).
        
        Returns:
            List[Exhibition]: Список активных выставок.
        """
        now = datetime.now()
        return [exhibition for exhibition in self._items.values() 
                if exhibition.start_date <= now <= exhibition.end_date]

    def get_by_date_range(self, start: datetime, end: datetime) -> List[Exhibition]:
        """
        Получает выставки в заданном временном промежутке.
        
        Args:
            start: Начало временного промежутка.
            end: Конец временного промежутка.
            
        Returns:
            List[Exhibition]: Список выставок в заданном временном промежутке.
        """
        return [exhibition for exhibition in self._items.values() 
                if (exhibition.start_date <= end and exhibition.end_date >= start)]
