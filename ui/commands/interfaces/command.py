from abc import ABC, abstractmethod
from ..models import CommandContext, CommandResult

class ICommand(ABC):
    """Базовый интерфейс для всех команд"""
    @property
    @abstractmethod
    def name(self) -> str:
        """Название команды для вызова"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Описание команды для help"""
        pass

    @property
    @abstractmethod
    def usage(self) -> str:
        """Пример использования команды"""
        pass

    @abstractmethod
    def can_execute(self, context: CommandContext) -> bool:
        """Проверка возможности выполнения команды"""
        pass

    @abstractmethod
    def execute(self, context: CommandContext) -> CommandResult:
        """Выполнить команду"""
        pass
