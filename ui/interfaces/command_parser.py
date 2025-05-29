from abc import ABC, abstractmethod
from typing import Tuple, List

class ICommandParser(ABC):
    @abstractmethod
    def parse(self, input_string: str) -> Tuple[str, List[str]]:
        """
        Парсит входную строку на команду и аргументы
        Returns:
            Tuple[str, List[str]]: (имя_команды, [аргументы])
        """
        pass

    @abstractmethod
    def validate(self, command: str, args: List[str]) -> bool:
        """Проверяет валидность команды и её аргументов"""
        pass
