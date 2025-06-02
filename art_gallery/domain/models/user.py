from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
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

    def _get_entity_data(self) -> Dict[str, Any]:
        """Получает данные пользователя для сериализации"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Создает объект User из словаря"""
        # Обработка обязательных полей
        username = data['username']
        password_hash = data['password_hash']
        
        # Обработка роли: может быть как строкой ("admin", "user"), так и значением перечисления
        role_data = data['role']
        if isinstance(role_data, str):
            role = UserRole(role_data) # Используем конструктор Enum с raw value
        else:
            role = role_data
            
        # Обработка дат: преобразование из ISO формата
        created_at_str = data.get('created_at')
        created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
        
        last_login_str = data.get('last_login')
        last_login = datetime.fromisoformat(last_login_str) if last_login_str else None
        
        # Обработка активности
        is_active = data.get('is_active', True)
        
        # Создание объекта
        user = cls(
            username=username,
            password_hash=password_hash,
            role=role,
            created_at=created_at,
            last_login=last_login,
            is_active=is_active
        )
        
        # Установка ID, если он есть в данных и валидный
        if 'id' in data:
            try:
                id_value = int(data['id'])
                if id_value > 0:
                    user.id = id_value
            except (ValueError, TypeError):
                # Если ID не может быть преобразован в int или невалидный, игнорируем его
                pass
            
        return user
