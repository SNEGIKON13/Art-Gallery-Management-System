from typing import Optional
from domain.models import User
from repository.interfaces.user_repository import IUserRepository
from .base_memory_repository import BaseMemoryRepository

class UserMemoryRepository(BaseMemoryRepository[User], IUserRepository):
    def get_by_username(self, username: str) -> Optional[User]:
        return next((user for user in self._items.values() 
                    if user.username == username), None)

    def username_exists(self, username: str) -> bool:
        return any(user.username == username for user in self._items.values())
