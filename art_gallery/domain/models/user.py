from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional
from art_gallery.domain.models.base_entity import BaseEntity

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

@dataclass
class User(BaseEntity):
    username: str
    password_hash: str
    role: UserRole
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.username or len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not self.password_hash:
            raise ValueError("Password hash cannot be empty")

    def is_admin(self) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return self.role == UserRole.ADMIN

    def update_password(self, new_password_hash: str) -> None:
        """Обновляет хеш пароля пользователя"""
        if not new_password_hash:
            raise ValueError("New password hash cannot be empty")
        self.password_hash = new_password_hash

    def deactivate(self) -> None:
        """Деактивирует учетную запись пользователя"""
        self.is_active = False

    def activate(self) -> None:
        """Активирует учетную запись пользователя"""
        self.is_active = True

    def update_last_login(self) -> None:
        """Обновляет время последнего входа"""
        self.last_login = datetime.now()

    def can_login(self) -> bool:
        """Проверяет, может ли пользователь войти в систему"""
        return self.is_active

    def __eq__(self, other: object) -> bool:
        """Сравнивает пользователей по id"""
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Хеширует пользователя по id"""
        return hash(self.id)
