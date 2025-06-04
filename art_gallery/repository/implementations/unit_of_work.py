from typing import Optional, Dict, TypeVar, Generic, List
from domain import User, Artwork, Exhibition, BaseEntity
from repository.interfaces.user_repository import IUserRepository
from repository.interfaces.artwork_repository import IArtworkRepository
from repository.interfaces.exhibition_repository import IExhibitionRepository
from .user_repository import UserMemoryRepository
from .artwork_repository import ArtworkMemoryRepository
from .exhibition_repository import ExhibitionMemoryRepository

T = TypeVar('T', bound=BaseEntity)

class UnitOfWork:
    def __init__(self):
        self._user_repository: Optional[IUserRepository] = None
        self._artwork_repository: Optional[IArtworkRepository] = None
        self._exhibition_repository: Optional[IExhibitionRepository] = None
        self._transaction_cache: Dict[str, Dict[int, BaseEntity]] = {}
        self._is_transaction_active: bool = False
        self._changes: Dict[str, List[BaseEntity]] = {}

    @property
    def users(self) -> IUserRepository:
        if not self._user_repository:
            self._user_repository = UserMemoryRepository()
        return self._user_repository

    @property
    def artworks(self) -> IArtworkRepository:
        if not self._artwork_repository:
            self._artwork_repository = ArtworkMemoryRepository()
        return self._artwork_repository

    @property
    def exhibitions(self) -> IExhibitionRepository:
        if not self._exhibition_repository:
            self._exhibition_repository = ExhibitionMemoryRepository()
        return self._exhibition_repository

    def begin_transaction(self) -> None:
        """Начать транзакцию"""
        if self._is_transaction_active:
            raise ValueError("Transaction already active")
        self._is_transaction_active = True
        self._transaction_cache = {
            'users': {},
            'artworks': {},
            'exhibitions': {}
        }

    def register_new(self, entity: BaseEntity, repository_name: str) -> None:
        if repository_name not in self._changes:
            self._changes[repository_name] = []
        self._changes[repository_name].append(entity)

    def commit(self) -> None:
        """Подтвердить транзакцию"""
        if not self._is_transaction_active:
            raise ValueError("No active transaction")
        
        try:
            for repo_name, entities in self._changes.items():
                repository = getattr(self, repo_name)
                for entity in entities:
                    repository.add(entity)
            self._is_transaction_active = False
            self._changes.clear()
        except Exception:
            self.rollback()
            raise

    def rollback(self) -> None:
        """Откатить транзакцию"""
        if not self._is_transaction_active:
            raise ValueError("No active transaction")
        
        # Восстанавливаем состояние из кэша
        for repo_name, entities in self._transaction_cache.items():
            repo = getattr(self, repo_name)
            for entity_id, entity in entities.items():
                repo._items[entity_id] = entity

        self._is_transaction_active = False
        self._transaction_cache.clear()

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
