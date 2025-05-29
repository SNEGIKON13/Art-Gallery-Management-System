from typing import Optional
from repository.interfaces.user_repository import IUserRepository
from repository.interfaces.artwork_repository import IArtworkRepository
from repository.interfaces.exhibition_repository import IExhibitionRepository
from .user_repository import UserMemoryRepository
from .artwork_repository import ArtworkMemoryRepository
from .exhibition_repository import ExhibitionMemoryRepository

class UnitOfWork:
    def __init__(self):
        self._user_repository: Optional[IUserRepository] = None
        self._artwork_repository: Optional[IArtworkRepository] = None
        self._exhibition_repository: Optional[IExhibitionRepository] = None

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
