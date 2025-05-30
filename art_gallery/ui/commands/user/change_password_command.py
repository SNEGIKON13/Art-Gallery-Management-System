from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.auth_exceptions import UnauthorizedError, AuthenticationError
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError

class ChangePasswordCommand(BaseCommand):
    def get_name(self) -> str:
        return "change_password"  # Убрали дефис для соответствия документации

    def get_description(self) -> str:
        return "Change user password"

    def get_usage(self) -> str:
        return "change_password <old_password> <new_password>"

    def get_help(self) -> str:
        return ("Changes the password for the current user.\n"
                "Requires old password for verification.\n"
                "You must be logged in to use this command.\n"
                "Usage: change_password <old_password> <new_password>")

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user:
            raise UnauthorizedError("You are not logged in")
            
        if len(args) != 2:
            raise MissingRequiredArgumentError("Old and new passwords required")
        
        old_password, new_password = args[0], args[1]
        
        if self._user_service.change_password(
            self._current_user.id, 
            old_password, 
            new_password
        ):
            print("Password changed successfully")
        else:
            raise AuthenticationError("Invalid old password")  # Изменили сообщение об ошибке
