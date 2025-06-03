"""
Модуль реализует Unit of Work для работы с MinIO репозиториями.
"""
from typing import Optional, Dict, List, Type
from art_gallery.domain import BaseEntity
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.interfaces.artwork_repository import IArtworkRepository
from art_gallery.repository.interfaces.exhibition_repository import IExhibitionRepository
from art_gallery.repository.implementations.minio.user_repository import UserMinioRepository
from art_gallery.repository.implementations.minio.artwork_repository import ArtworkMinioRepository
from art_gallery.repository.implementations.minio.exhibition_repository import ExhibitionMinioRepository
from art_gallery.infrastructure.config.minio_config import MinioConfig
from art_gallery.infrastructure.storage.minio_service import MinioService
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory

class MinioUnitOfWork:
    """
    Unit of Work для работы с MinIO репозиториями.
    Обеспечивает транзакционность операций с репозиториями.
    """

    def __init__(self, format_name: str = "json", minio_service: Optional[MinioService] = None, config: Optional[MinioConfig] = None):
        """
        Инициализирует Unit of Work для MinIO репозиториев.
        
        Args:
            format_name: Формат сериализации (json, xml и т.д.)
            minio_service: Сервис для работы с MinIO
            config: Конфигурация для MinIO
        """
        self._format_name = format_name
        self._config = config or MinioConfig()
        self._minio_service = minio_service or MinioService(self._config)
        
        # Получаем сериализатор и десериализатор для выбранного формата
        self._serializer = SerializationPluginFactory.get_serializer(self._format_name)
        self._deserializer = SerializationPluginFactory.get_deserializer(self._format_name)
        
        # Репозитории
        self._user_repository: Optional[IUserRepository] = None
        self._artwork_repository: Optional[IArtworkRepository] = None
        self._exhibition_repository: Optional[IExhibitionRepository] = None
        
        # Состояние транзакции
        self._transaction_cache: Dict[str, Dict[int, BaseEntity]] = {}
        self._is_transaction_active: bool = False
        self._changes: Dict[str, List[BaseEntity]] = {}

    @property
    def users(self) -> IUserRepository:
        """
        Получает репозиторий пользователей.
        
        Returns:
            IUserRepository: Репозиторий пользователей.
        """
        if not self._user_repository:
            self._user_repository = UserMinioRepository(
                serializer=self._serializer,
                deserializer=self._deserializer,
                minio_service=self._minio_service,
                config=self._config
            )
        return self._user_repository

    @property
    def artworks(self) -> IArtworkRepository:
        """
        Получает репозиторий экспонатов.
        
        Returns:
            IArtworkRepository: Репозиторий экспонатов.
        """
        if not self._artwork_repository:
            self._artwork_repository = ArtworkMinioRepository(
                serializer=self._serializer,
                deserializer=self._deserializer,
                minio_service=self._minio_service,
                config=self._config
            )
        return self._artwork_repository

    @property
    def exhibitions(self) -> IExhibitionRepository:
        """
        Получает репозиторий выставок.
        
        Returns:
            IExhibitionRepository: Репозиторий выставок.
        """
        if not self._exhibition_repository:
            self._exhibition_repository = ExhibitionMinioRepository(
                serializer=self._serializer,
                deserializer=self._deserializer,
                minio_service=self._minio_service,
                config=self._config
            )
        return self._exhibition_repository

    def begin_transaction(self) -> None:
        """
        Начинает новую транзакцию.
        
        Raises:
            ValueError: Если транзакция уже активна.
        """
        if self._is_transaction_active:
            raise ValueError("Transaction already active")
        
        self._is_transaction_active = True
        self._changes.clear()
        
        # Создаем кэш для хранения исходного состояния сущностей
        self._transaction_cache = {
            'users': {},
            'artworks': {},
            'exhibitions': {}
        }
        
        # Копируем текущее состояние репозиториев в кэш
        if self._user_repository:
            # Используем новый метод для получения копии элементов
            self._transaction_cache['users'] = self._user_repository.get_all_items_copy() if hasattr(self._user_repository, 'get_all_items_copy') else {}
                
        if self._artwork_repository:
            # Используем новый метод для получения копии элементов
            self._transaction_cache['artworks'] = self._artwork_repository.get_all_items_copy() if hasattr(self._artwork_repository, 'get_all_items_copy') else {}
                
        if self._exhibition_repository:
            # Используем новый метод для получения копии элементов
            self._transaction_cache['exhibitions'] = self._exhibition_repository.get_all_items_copy() if hasattr(self._exhibition_repository, 'get_all_items_copy') else {}

    def register_new(self, entity: BaseEntity, repository_name: str) -> None:
        """
        Регистрирует новую сущность для добавления в репозиторий при коммите.
        
        Args:
            entity: Сущность для добавления.
            repository_name: Имя репозитория ('users', 'artworks', 'exhibitions').
        """
        if repository_name not in self._changes:
            self._changes[repository_name] = []
        self._changes[repository_name].append(entity)

    def commit(self) -> None:
        """
        Подтверждает транзакцию и сохраняет изменения в репозиториях.
        
        Raises:
            ValueError: Если нет активной транзакции.
        """
        if not self._is_transaction_active:
            raise ValueError("No active transaction")
        
        try:
            # Применяем изменения к репозиториям
            for repo_name, entities in self._changes.items():
                repository = getattr(self, repo_name)
                for entity in entities:
                    repository.add(entity)
            
            # Завершаем транзакцию
            self._is_transaction_active = False
            self._changes.clear()
            self._transaction_cache.clear()
        except Exception:
            # В случае ошибки откатываем транзакцию
            self.rollback()
            raise

    def rollback(self) -> None:
        """
        Откатывает транзакцию и восстанавливает исходное состояние репозиториев.
        
        Raises:
            ValueError: Если нет активной транзакции.
        """
        if not self._is_transaction_active:
            raise ValueError("No active transaction")
        
        # Восстанавливаем состояние из кэша
        for repo_name, entities in self._transaction_cache.items():
            repo = getattr(self, repo_name)
            if hasattr(repo, 'restore_items_state'):
                # Используем новый метод для восстановления состояния
                repo.restore_items_state(entities)
        
        # Завершаем транзакцию
        self._is_transaction_active = False
        self._changes.clear()
        self._transaction_cache.clear()

    def __enter__(self):
        """
        Метод для использования с контекстным менеджером (with).
        Начинает транзакцию.
        
        Returns:
            MinioUnitOfWork: Сам объект UnitOfWork.
        """
        self.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Метод для использования с контекстным менеджером (with).
        Завершает транзакцию.
        
        Args:
            exc_type: Тип исключения, если оно возникло.
            exc_val: Значение исключения, если оно возникло.
            exc_tb: Трассировка исключения, если оно возникло.
        """
        if exc_type is not None:
            # Если возникло исключение, откатываем транзакцию
            self.rollback()
        else:
            # Если все в порядке, применяем изменения
            self.commit()
