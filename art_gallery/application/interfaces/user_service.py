from abc import ABC, abstractmethod
from typing import Optional, List
from art_gallery.domain import User, UserRole # Добавили UserRole
from datetime import datetime # Добавили datetime

class IUserService(ABC):

    @abstractmethod
    def add_imported_user(self, username: str, password_hash: str, role: UserRole, created_at: datetime, last_login: Optional[datetime], is_active: bool) -> User:
        """
        Добавляет пользователя из импортированных данных с предварительно хешированным паролем.
        """
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Аутентифицирует пользователя"""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по id"""
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получает пользователя по имени"""
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Получает список всех пользователей"""
        pass

    @abstractmethod
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Изменяет пароль пользователя"""
        pass

    @abstractmethod
    def deactivate_user(self, user_id: int) -> bool:
        """Деактивирует пользователя"""
        pass

    @abstractmethod
    def register(self, username: str, password: str, is_admin: bool = False) -> User:
        """Регистрирует нового пользователя"""
        pass
