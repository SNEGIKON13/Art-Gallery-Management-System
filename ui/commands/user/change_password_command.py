from typing import Sequence
from ..base_command import BaseCommand
from ...exceptions.command_exceptions import InvalidArgumentsException, AuthenticationException, CommandException

class ChangePasswordCommand(BaseCommand):
    def get_name(self) -> str:
        return "change-password"

    def get_description(self) -> str:
        return "Change user password"

    def get_usage(self) -> str:
        return "change-password <old_password> <new_password>"

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user:
            raise AuthenticationException("You are not logged in")
            
        if len(args) != 2:
            raise InvalidArgumentsException("Old and new passwords required")
        
        old_password, new_password = args[0], args[1]
        
        if self._user_service.change_password(
            self._current_user.id, 
            old_password, 
            new_password
        ):
            print("Password changed successfully")
        else:
            raise CommandException("Failed to change password")
