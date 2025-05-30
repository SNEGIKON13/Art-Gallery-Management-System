from typing import Optional, List, Dict
from art_gallery.domain.models import User, UserRole
from art_gallery.application.interfaces.user_service import IUserService
import hashlib
from datetime import datetime

class MockUserService(IUserService):
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1
        self._username_to_id: Dict[str, int] = {}
        
        # Создаем админа по умолчанию
        self.register("admin", "admin", True)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str, is_admin: bool = False) -> User:
        if username in self._username_to_id:
            raise ValueError("Username already exists")
            
        user = User(
            username=username,
            password_hash=self._hash_password(password),
            role=UserRole.ADMIN if is_admin else UserRole.USER,
            created_at=datetime.now()
        )
        
        self._users[self._next_id] = user
        self._username_to_id[username] = self._next_id
        self._next_id += 1
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user_id = self._username_to_id.get(username)
        if not user_id:
            return None
            
        user = self._users[user_id]
        if user.password_hash == self._hash_password(password):
            return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        user_id = self._username_to_id.get(username)
        return self._users.get(user_id) if user_id else None

    def get_all_users(self) -> List[User]:
        return list(self._users.values())

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user or user.password_hash != self._hash_password(old_password):
            return False
        user.password_hash = self._hash_password(new_password)
        return True

    def deactivate_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        user.is_active = False
        return True
