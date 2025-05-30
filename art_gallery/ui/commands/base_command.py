from abc import ABC, abstractmethod
from typing import List, Optional, Sequence
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.application.services.user_service import IUserService

class BaseCommand(ICommand, ABC):
    def __init__(self, user_service: IUserService, command_registry=None):
        self._user_service = user_service
        self._current_user = None
        self._registry = command_registry

    def set_current_user(self, user) -> None:
        self._current_user = user
        # Обновляем пользователя во всех командах
        if self._registry:
            for command in self._registry._commands.values():
                command._current_user = user

    @abstractmethod
    def execute(self, args: Sequence[str]) -> None:
        """Execute command with given arguments"""
        pass
