from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.auth_exceptions import PermissionDeniedError
from art_gallery.application.services.user_service import UserService
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError
from art_gallery.ui.exceptions.validation_exceptions import InvalidInputError

class DeactivateUserCommand(BaseCommand):
    def get_name(self) -> str:
        return "deactivate-user"

    def get_description(self) -> str:
        return "Deactivate user account (admin only)"

    def get_usage(self) -> str:
        return "deactivate-user <user_id>"

    def get_help(self) -> str:
        return ("Deactivates a user account by ID.\n"
                "This command is only available to administrators.\n"
                "Deactivated users cannot log in.\n"
                "Usage: deactivate-user <user_id>")

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user or not self._current_user.is_admin():
            raise PermissionDeniedError("Admin rights required")
            
        if len(args) != 1:
            raise InvalidInputError("User ID required")
        
        try:
            user_id = int(args[0])
            if self._user_service.deactivate_user(user_id):
                print(f"User {user_id} deactivated successfully")
            else:
                raise CommandExecutionError(f"User {user_id} not found")
        except ValueError:
            raise InvalidInputError("Invalid user ID format")
