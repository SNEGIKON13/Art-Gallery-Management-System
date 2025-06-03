from typing import Optional
from art_gallery.domain import User
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.implementations.base_memory_repository import BaseMemoryRepository

class UserMemoryRepository(BaseMemoryRepository[User], IUserRepository):
    def get_by_username(self, username: str) -> Optional[User]:
        return next((user for user in self._items.values() 
                    if user.username == username), None)

    def username_exists(self, username: str) -> bool:
        return any(user.username == username for user in self._items.values())
