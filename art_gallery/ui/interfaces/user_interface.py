from abc import ABC, abstractmethod
from typing import Any, Optional

class IUserInterface(ABC):
    @abstractmethod
    def display(self, message: str) -> None:
        """Отобразить сообщение пользователю"""
        pass

    @abstractmethod
    def get_input(self, prompt: Optional[str] = None) -> str:
        """Получить ввод от пользователя"""
        pass

    @abstractmethod
    def display_error(self, error: str) -> None:
        """Отобразить сообщение об ошибке"""
        pass

    @abstractmethod
    def display_success(self, message: str) -> None:
        """Отобразить сообщение об успехе"""
        pass

    @abstractmethod
    def clear_screen(self) -> None:
        """Очистить экран"""
        pass
