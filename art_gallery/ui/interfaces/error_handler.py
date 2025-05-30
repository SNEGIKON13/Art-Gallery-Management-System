from abc import ABC, abstractmethod
from typing import Any, Optional

class IErrorHandler(ABC):
    @abstractmethod
    def handle_error(self, error: Exception) -> None:
        """Обработать ошибку и вывести сообщение пользователю"""
        pass

    @abstractmethod
    def format_error(self, error: Exception) -> str:
        """Форматировать ошибку в читаемое сообщение"""
        pass

    @abstractmethod
    def log_error(self, error: Exception) -> None:
        """Записать ошибку в лог"""
        pass
