"""
MinIO-реализация репозитория для пользователей.
Реализует интерфейс IUserRepository с использованием MinIO для хранения данных.
"""
from typing import List, Dict, Any, Optional, Union

from art_gallery.domain.models import User, UserRole
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.implementations.minio.base_minio_repository import BaseMinioRepository
from art_gallery.repository.specifications.base_specification import Specification
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.storage.minio_service import MinioService

from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer


class UserMinioRepository(BaseMinioRepository[User], IUserRepository):
    """
    MinIO-реализация репозитория для пользователей.
    Наследуется от базового MinIO репозитория и реализует интерфейс IUserRepository.
    """

    def __init__(self, 
                 serializer: ISerializer, 
                 deserializer: IDeserializer,
                 minio_service: Optional[MinioService] = None,
                 config: Optional[MinioConfig] = None):
        """
        Инициализирует репозиторий пользователей с использованием MinIO.
        
        Args:
            serializer: Сериализатор для преобразования данных в строку.
            deserializer: Десериализатор для преобразования строки в данные.
            minio_service: Сервис для работы с MinIO. Если не указан, создается новый.
            config: Конфигурация для подключения к MinIO. Используется, если minio_service не указан.
        """
        self._config = config or MinioConfig()
        
        # Определяем путь к объекту в зависимости от формата сериализации
        object_path = self._config.USERS_JSON_PATH
        if serializer.__class__.__name__ == 'XMLSerializer':
            object_path = self._config.USERS_XML_PATH
        
        super().__init__(
            bucket_name=self._config.DATA_BUCKET,
            object_path=object_path,
            serializer=serializer,
            deserializer=deserializer,
            minio_service=minio_service,
            config=self._config
        )

    def _create_entity_from_dict(self, data: Dict[str, Any]) -> User:
        """
        Создает пользователя из словаря.
        
        Args:
            data: Словарь с данными пользователя.
            
        Returns:
            User: Созданный пользователь.
        """
        return User.from_dict(data)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Получает пользователя по имени пользователя.
        
        Args:
            username: Имя пользователя.
            
        Returns:
            Optional[User]: Найденный пользователь или None, если пользователь не найден.
        """
        for user in self._items.values():
            if user.username.lower() == username.lower():
                return user
        return None

    def username_exists(self, username: str) -> bool:
        """
        Проверяет существование пользователя с таким именем.
        
        Args:
            username: Имя пользователя.
            
        Returns:
            bool: True, если пользователь существует, иначе False.
        """
        return self.get_by_username(username) is not None
