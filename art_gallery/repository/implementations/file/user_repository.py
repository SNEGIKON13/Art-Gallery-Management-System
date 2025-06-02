import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from art_gallery.domain.models import User, UserRole
from art_gallery.repository.interfaces.user_repository import IUserRepository
from art_gallery.repository.specifications.base_specification import Specification
from serialization.interfaces.ISerializer import ISerializer
from serialization.interfaces.IDeserializer import IDeserializer

class UserFileRepository(IUserRepository):
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
            
        # Присвоение ID происходит через свойство user.id
        if not user.id:
            # Генерация ID для нового пользователя
            if not self._users:
                new_id = 0
            else:
                # Находим максимальный ID и увеличиваем на 1
                existing_ids = [u.id for u in self._users if hasattr(u, 'id') and u.id is not None]
                if not existing_ids:
                    new_id = 0
                else:
                    new_id = max(existing_ids) + 1
            user.id = new_id
            
        self._users.append(user)
        self._save_data()
        return user
        
    def get_by_id(self, user_id: int) -> Optional[User]:
        return next((user for user in self._users if user.id == user_id), None)
        
    def get_all(self) -> List[User]:
        return list(self._users)
        
    def update(self, user_to_update: User) -> User:
        # Проверяем, что пользователь существует
        existing_user = next((user for user in self._users if user.id == user_to_update.id), None)
        if not existing_user:
            raise ValueError(f"User with id {user_to_update.id} not found.")
            
        # Проверяем, что имя пользователя не занято, если оно изменилось
        if existing_user.username != user_to_update.username and self.username_exists(user_to_update.username):
            raise ValueError(f"User with username '{user_to_update.username}' already exists.")
            
        # Обновляем пользователя
        for i, user in enumerate(self._users):
            if user.id == user_to_update.id:
                self._users[i] = user_to_update
                self._save_data()
                return user_to_update
                
        return user_to_update # Строго говоря, мы сюда не дойдем из-за проверки выше
        
    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if user:
            self._users.remove(user)
            self._save_data()
            
    def find(self, specification: Specification[User]) -> List[User]:
        return [user for user in self._users if specification.is_satisfied_by(user)]
        
    def get_by_username(self, username: str) -> Optional[User]:
        return next((user for user in self._users if user.username.lower() == username.lower()), None)
        
    def username_exists(self, username: str) -> bool:
        return any(user.username.lower() == username.lower() for user in self._users)
        
    def get_by_role(self, role: UserRole) -> List[User]:
        return [user for user in self._users if user.role == role]
