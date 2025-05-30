from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.auth_exceptions import UnauthorizedError

class GetUserInfoCommand(BaseCommand):
    def get_name(self) -> str:
        return "whoami"

    def get_description(self) -> str:
        return "Display information about current user"

    def get_usage(self) -> str:
        return "whoami"

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user:
            raise UnauthorizedError("You are not logged in")
        
        role = "administrator" if self._current_user.is_admin() else "user"
        print(f"Username: {self._current_user.username}")
        print(f"Role: {role}")
