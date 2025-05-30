from abc import ABC, abstractmethod
from typing import List, Any, Optional, Sequence
from art_gallery.domain.models import User  # добавим импорт

class ICommand(ABC):
    @abstractmethod
    def execute(self, args: Sequence[str]) -> None:
        """Выполнить команду с заданными аргументами"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Получить имя команды"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Получить описание команды"""
        pass

    @abstractmethod
    def get_usage(self) -> str:
        """Получить инструкцию по использованию"""
        pass
    
    @abstractmethod
    def set_current_user(self, user: Optional[User]) -> None:
        """Set current user for the command"""
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Get detailed help information about the command"""
        pass
