from abc import abstractmethod
from typing import Any, Optional
from .interfaces.command import ICommand
from .models import CommandContext, CommandResult

class BaseCommand(ICommand):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def usage(self) -> str:
        return f"{self.name}"

    def can_execute(self, context: CommandContext) -> bool:
        return True

    @abstractmethod
    def execute(self, context: CommandContext) -> CommandResult:
        pass

    def _create_result(self, success: bool, message: str, data: Optional[Any] = None) -> CommandResult:
        return CommandResult(success=success, message=message, data=data)
