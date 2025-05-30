from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.auth_exceptions import PermissionDeniedError
from art_gallery.application.services.user_service import UserService
from art_gallery.ui.exceptions.auth_exceptions import UnauthorizedError, AuthenticationError
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError

class ChangePasswordCommand(BaseCommand):
    def get_name(self) -> str:
        return "change-password"

    def get_description(self) -> str:
        return "Change user password"

    def get_usage(self) -> str:
        return "change-password <old_password> <new_password>"

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
            raise AuthenticationError("Failed to change password")
