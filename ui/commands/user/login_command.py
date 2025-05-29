from typing import Sequence
from ..base_command import BaseCommand
from ...exceptions.validation_exceptions import MissingRequiredArgumentError
from ...exceptions.auth_exceptions import AuthenticationError

class LoginCommand(BaseCommand):
    def get_name(self) -> str:
        return "login"

    def get_description(self) -> str:
        return "Login to the system"

    def get_usage(self) -> str:
        return "login <username> <password>"

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 2:
            raise MissingRequiredArgumentError("Username and password required")
        
        username, password = args[0], args[1]
        user = self._user_service.authenticate(username, password)
        
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        self.set_current_user(user)
        print(f"Welcome, {username}!")
