from datetime import datetime
import hashlib
from typing import Optional, List
from domain.models import User, UserRole
from repository.interfaces.user_repository import IUserRepository
from application.interfaces.user_service import IUserService
from application.validation.validators import BusinessRuleValidator

class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository):
        self._repository = user_repository
        self._next_id = 1  # Временное решение для генерации ID

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str, is_admin: bool = False, current_user: Optional[User] = None) -> User:
        """Регистрирует нового пользователя"""
        if is_admin and current_user:
            BusinessRuleValidator.validate_admin_access(current_user)

        if self._repository.username_exists(username):
            raise ValueError("Username already exists")

        user = User(
            username=username,
            password_hash=self._hash_password(password),
            role=UserRole.ADMIN if is_admin else UserRole.USER,
            created_at=datetime.now()
        )
        
        self._next_id += 1
        return self._repository.add(user)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Аутентифицирует пользователя"""
        user = self._repository.get_by_username(username)
        if user and user.password_hash == self._hash_password(password):
            if not user.can_login():
                raise ValueError("Account is deactivated")
            user.update_last_login()
            self._repository.update(user)
            return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по id"""
        return self._repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получает пользователя по имени"""
        return self._repository.get_by_username(username)

    def get_all_users(self) -> List[User]:
        """Получает список всех пользователей"""
        return self._repository.get_all()

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Изменяет пароль пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        if user.password_hash != self._hash_password(old_password):
            return False

        user.update_password(self._hash_password(new_password))
        self._repository.update(user)
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """Деактивирует пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.deactivate()
        self._repository.update(user)
        return True
