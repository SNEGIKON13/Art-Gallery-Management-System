from abc import ABC, abstractmethod
from typing import List, Optional, Sequence
from ..interfaces.command import ICommand
from application.services.user_service import IUserService

class BaseCommand(ICommand, ABC):
    def __init__(self, user_service: IUserService):
        self._user_service = user_service
        self._current_user = None

    def set_current_user(self, user) -> None:
        self._current_user = user

    @abstractmethod
    def execute(self, args: Sequence[str]) -> None:
        """Execute command with given arguments"""
        pass
