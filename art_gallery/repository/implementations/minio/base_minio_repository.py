"""
Базовый класс для всех MinIO репозиториев.
Предоставляет общую функциональность для загрузки и сохранения данных через MinIO.
"""
import os
from typing import List, Optional, Dict, Any, TypeVar, Generic, Union, Protocol, cast
from abc import ABC, abstractmethod

from art_gallery.domain.base_entity import BaseEntity
from art_gallery.repository.interfaces.base_repository import IBaseRepository
from art_gallery.repository.specifications.base_specification import Specification
from art_gallery.infrastructure.cloud.minio_config import MinioConfig
from art_gallery.infrastructure.cloud.minio_service import MinioService

from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

# Определяем T как BaseEntity с методом clone
T = TypeVar('T', bound=BaseEntity)


class BaseMinioRepository(Generic[T], IBaseRepository[T], ABC):
    """
    Базовый класс для всех MinIO репозиториев.
    Реализует общую функциональность для работы с данными через MinIO.
    """

    def __init__(self, 
                 bucket_name: str, 
                 object_path: str, 
                 serializer: ISerializer, 
                 deserializer: IDeserializer,
                 minio_service: Optional[MinioService] = None,
                 config: Optional[MinioConfig] = None):
        """
        Инициализирует базовый MinIO репозиторий.
        
        Args:
            bucket_name: Имя бакета в MinIO.
            object_path: Путь к объекту (файлу) в бакете.
            serializer: Сериализатор для преобразования данных в строку.
            deserializer: Десериализатор для преобразования строки в данные.
            minio_service: Сервис для работы с MinIO. Если не указан, создается новый.
            config: Конфигурация для подключения к MinIO. Используется, если minio_service не указан.
        """
        self._bucket_name = bucket_name
        self._object_path = object_path
        self._serializer = serializer
        self._deserializer = deserializer
        self._config = config or MinioConfig.from_env()
        self._minio_service = minio_service or MinioService(self._config)
        
        # Убедимся, что бакет существует
        self._minio_service.ensure_bucket_exists(self._bucket_name)
        
        # Инициализируем коллекцию сущностей
        self._items: Dict[int, T] = {}
        self._load_data()

    def _load_data(self) -> None:
        """
        Загружает данные из MinIO и преобразует их в сущности.
        """
        try:
            # Проверяем существование объекта
            if not self._minio_service.object_exists(self._bucket_name, self._object_path):
                print(f"Object {self._object_path} does not exist in bucket {self._bucket_name}. Starting with empty collection.")
                self._items = {}
                return
            
            # Скачиваем данные из MinIO
            data_bytes = self._minio_service.download_data(self._bucket_name, self._object_path)
            if data_bytes is None:
                print(f"Failed to download data from {self._bucket_name}/{self._object_path}. Starting with empty collection.")
                self._items = {}
                return
            
            # Десериализуем данные
            list_of_dicts = self._deserializer.deserialize(data_bytes.decode('utf-8'))
            
            # Преобразуем словари в сущности
            loaded_items = {}
            for item_dict in list_of_dicts:
                try:
                    entity = self._create_entity_from_dict(item_dict)
                    loaded_items[entity.id] = entity
                except Exception as e:
                    print(f"Error creating entity from dict: {item_dict}, error: {e}")
            
            self._items = loaded_items
        except Exception as e:
            print(f"Error loading data from {self._bucket_name}/{self._object_path}: {e}")
            self._items = {}

    def _save_data(self) -> None:
        """
        Сохраняет данные в MinIO.
        """
        try:
            # Преобразуем сущности в словари
            data_to_serialize = [item.to_dict() for item in self._items.values()]
            
            # Сериализуем данные
            serialized_data = self._serializer.serialize(data_to_serialize)
            
            # Загружаем данные в MinIO
            success = self._minio_service.upload_data(
                bucket_name=self._bucket_name,
                object_name=self._object_path,
                data=serialized_data.encode('utf-8'),
                content_type=self._get_content_type()
            )
            
            if not success:
                print(f"Failed to save data to {self._bucket_name}/{self._object_path}")
        except Exception as e:
            print(f"Error saving data to {self._bucket_name}/{self._object_path}: {e}")

    def _get_content_type(self) -> str:
        """
        Определяет MIME-тип на основе расширения файла.
        
        Returns:
            str: MIME-тип.
        """
        extension = os.path.splitext(self._object_path)[1].lower()
        content_types = {
            '.json': 'application/json',
            '.xml': 'application/xml',
        }
        return content_types.get(extension, 'application/octet-stream')

    @abstractmethod
    def _create_entity_from_dict(self, data: Dict[str, Any]) -> T:
        """
        Создает сущность из словаря.
        
        Args:
            data: Словарь с данными сущности.
            
        Returns:
            T: Созданная сущность.
        """
        pass

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Получает сущность по ID.
        
        Args:
            id: ID сущности.
            
        Returns:
            Optional[T]: Найденная сущность или None, если сущность не найдена.
        """
        return self._items.get(id)

    def get_all(self) -> List[T]:
        """
        Получает все сущности.
        
        Returns:
            List[T]: Список всех сущностей.
        """
        return list(self._items.values())

    def add(self, entity: T) -> T:
        """
        Добавляет новую сущность.
        
        Args:
            entity: Сущность для добавления.
            
        Returns:
            T: Добавленная сущность.
        """
        self._items[entity.id] = entity
        self._save_data()
        return entity

    def update(self, entity: T) -> T:
        """
        Обновляет существующую сущность.
        
        Args:
            entity: Сущность для обновления.
            
        Returns:
            T: Обновленная сущность.
        """
        if entity.id not in self._items:
            raise ValueError(f"Entity with id {entity.id} not found")
        
        self._items[entity.id] = entity
        self._save_data()
        return entity

    def delete(self, id: int) -> None:
        """
        Удаляет сущность по ID.
        
        Args:
            id: ID сущности для удаления.
        """
        if id not in self._items:
            raise ValueError(f"Entity with id {id} not found")
        
        del self._items[id]
        self._save_data()

    def find(self, specification: Specification[T]) -> List[T]:
        """
        Находит сущности по спецификации.
        
        Args:
            specification: Спецификация для поиска.
            
        Returns:
            List[T]: Список найденных сущностей.
        """
        return [entity for entity in self._items.values() if specification.is_satisfied_by(entity)]
        
    def get_all_items_copy(self) -> Dict[int, T]:
        """
        Возвращает копию словаря всех элементов для создания снимка состояния.
        Используется для транзакционности в UnitOfWork.
        
        Returns:
            Dict[int, T]: Копия словаря всех элементов.
        """
        # Используем явное приведение типа, чтобы указать, что clone() возвращает T
        return {entity_id: cast(T, entity.clone()) for entity_id, entity in self._items.items()}
    
    def restore_items_state(self, items_state: Dict[int, T]) -> None:
        """
        Восстанавливает состояние элементов из сохраненного снимка.
        Используется для отката транзакций в UnitOfWork.
        
        Args:
            items_state: Снимок состояния для восстановления.
        """
        self._items = items_state
