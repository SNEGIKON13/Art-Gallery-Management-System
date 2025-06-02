import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain.models import User, UserRole
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.specifications.base_specification import Specification
from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

class UserJsonRepository(IUserRepository):
    def __init__(self, filepath: str, serializer: ISerializer, deserializer: IDeserializer):
        self._filepath = filepath
        self._serializer = serializer  # Сериализатор из плагина
        self._deserializer = deserializer  # Десериализатор из плагина
        
        # Создаем директорию, если нужно
        file_dir = os.path.dirname(self._filepath)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        self._users: List[User] = []
        self._load_data()

    def _load_data(self) -> None:
        try:
            # Используем десериализатор из плагина
            list_of_dicts = self._deserializer.deserialize_from_file(self._filepath)
            loaded_users = []
            for user_data_dict in list_of_dicts:
                try:
                    loaded_users.append(User.from_dict(user_data_dict))
                except Exception as e:
                    print(f"Error creating User from dict: {user_data_dict}, error: {e}")
                    # TODO: Заменить на логирование
            self._users = loaded_users
        except Exception as e:
            # В случае ошибки считаем, что данных нет
            print(f"Error loading data from {self._filepath} using deserializer: {e}")
            # TODO: Заменить на логирование
            self._users = []

    def _save_data(self) -> None:
        try:
            # Используем сериализатор из плагина
            data_to_serialize = [user.to_dict() for user in self._users]
            self._serializer.serialize_to_file(data_to_serialize, self._filepath)
        except Exception as e:
            print(f"Error saving data to {self._filepath} using serializer: {e}")
            # TODO: Заменить на логирование

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
