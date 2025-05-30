from abc import abstractmethod
from typing import Optional
from domain.models import User
from .base_repository import IBaseRepository

class IUserRepository(IBaseRepository[User]):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени"""
        pass

    @abstractmethod
    def username_exists(self, username: str) -> bool:
        """Проверить существование пользователя с таким именем"""
        pass
