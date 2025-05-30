from typing import Sequence
from base_command import BaseCommand
from ui.exceptions.command_exceptions import CommandExecutionError
from ui.exceptions.validation_exceptions import MissingRequiredArgumentError

class RegisterCommand(BaseCommand):
    def get_name(self) -> str:
        return "register"

    def get_description(self) -> str:
        return "Register a new user"

    def get_usage(self) -> str:
        return "register <username> <password> [--admin]"

    def execute(self, args: Sequence[str]) -> None:
        if len(args) < 2:
            raise MissingRequiredArgumentError("Username and password required")
        
        username, password = args[0], args[1]
        is_admin = "--admin" in args[2:] if len(args) > 2 else False
        
        try:
            self._user_service.register(username, password, is_admin)
            print(f"User {username} successfully registered")
        except ValueError as e:
            raise CommandExecutionError(str(e))
