import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain.models import User, UserRole
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.specifications.base_specification import Specification

class UserJsonRepository(IUserRepository):
    def __init__(self, filepath: str):
        self._filepath = filepath
        # Создаем директорию, если нужно
        file_dir = os.path.dirname(self._filepath)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        self._users: List[User] = []
        self._load_data()

    def _load_data(self) -> None:
        if not os.path.exists(self._filepath) or os.path.getsize(self._filepath) == 0:
            self._users = []
            # Создаем пустой файл, если не существует
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return
        
        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Загружаем пользователей из данных
                loaded_users = []
                for user_data in data:
                    try:
                        loaded_users.append(User.from_dict(user_data))
                    except Exception as e:
                        print(f"Error deserializing user: {e}")
                self._users = loaded_users
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self._filepath}. Starting with empty user list.")
            self._users = []
        except Exception as e:
            print(f"Error loading users: {e}")
            self._users = []

    def _save_data(self) -> None:
        try:
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump([user.to_dict() for user in self._users], f, indent=4, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving users: {e}")

    def add(self, user: User) -> User:
        if self.username_exists(user.username):
            raise ValueError(f"User with username '{user.username}' already exists.")
        
        # Добавляем пользователя и сохраняем
        self._users.append(user)
        self._save_data()
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return next((user for user in self._users if user.id == user_id), None)

    def get_by_username(self, username: str) -> Optional[User]:
        return next((user for user in self._users if user.username == username), None)

    def get_all(self) -> List[User]:
        return list(self._users)

    def update(self, user_to_update: User) -> User:
        for i, user in enumerate(self._users):
            if user.id == user_to_update.id:
                self._users[i] = user_to_update
                self._save_data()
                return user_to_update
        raise ValueError(f"User with id {user_to_update.id} not found.")

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            self._users.remove(user)
            self._save_data()
        # Метод просто не делает ничего, если пользователь не найден
        # и возвращает None в соответствии с интерфейсом

    def username_exists(self, username: str) -> bool:
        return any(user.username == username for user in self._users)
        
    def find(self, specification: 'Specification[User]') -> List[User]:
        """
        Найти пользователей, соответствующих спецификации
        """
        return [user for user in self._users if specification.is_satisfied_by(user)]
