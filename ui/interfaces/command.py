from abc import ABC, abstractmethod
from typing import List, Any, Optional

class ICommand(ABC):
    @abstractmethod
    def execute(self, *args: List[str]) -> None:
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
