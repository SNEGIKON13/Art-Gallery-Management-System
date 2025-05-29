from typing import Sequence
from ..base_command import BaseCommand
from ...exceptions.command_exceptions import InvalidArgumentsException, AuthorizationException, CommandException

class DeactivateUserCommand(BaseCommand):
    def get_name(self) -> str:
        return "deactivate-user"

    def get_description(self) -> str:
        return "Deactivate user account (admin only)"

    def get_usage(self) -> str:
        return "deactivate-user <user_id>"

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user or not self._current_user.is_admin():
            raise AuthorizationException("Admin rights required")
            
        if len(args) != 1:
            raise InvalidArgumentsException("User ID required")
        
        try:
            user_id = int(args[0])
            if self._user_service.deactivate_user(user_id):
                print(f"User {user_id} deactivated successfully")
            else:
                raise CommandException(f"User {user_id} not found")
        except ValueError:
            raise InvalidArgumentsException("Invalid user ID")
