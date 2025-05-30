from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError
from art_gallery.ui.exceptions.auth_exceptions import AuthenticationError

class LoginCommand(BaseCommand):
    def __init__(self, user_service, command_registry):
        super().__init__(user_service)
        self._registry = command_registry

    def get_name(self) -> str:
        return "login"

    def get_description(self) -> str:
        return "Login to the system"

    def get_usage(self) -> str:
        return "login <username> <password>"

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 2:
            raise MissingRequiredArgumentError("Username and password required")
        
        username: str = args[0]
        password: str = args[1]
        user = self._user_service.authenticate(username, password)
        
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        self.set_current_user(user)
        print(f"Welcome, {username}!")
