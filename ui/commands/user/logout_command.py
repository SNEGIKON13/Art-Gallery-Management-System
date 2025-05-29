from typing import Sequence
from ..base_command import BaseCommand
from ...exceptions.auth_exceptions import UnauthorizedError

class LogoutCommand(BaseCommand):
    def get_name(self) -> str:
        return "logout"

    def get_description(self) -> str:
        return "Logout from the system"

    def get_usage(self) -> str:
        return "logout"

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user:
            raise UnauthorizedError("You are not logged in")
        
        self.set_current_user(None)
        print("Logged out successfully")
