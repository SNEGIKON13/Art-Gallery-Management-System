from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.exceptions.auth_exceptions import UnauthorizedError

class LogoutCommand(BaseCommand):
    def __init__(self, user_service, command_registry):
        super().__init__(user_service)
        self._registry = command_registry

    def get_name(self) -> str:
        return "logout"

    def get_description(self) -> str:
        return "Logout from the system"

    def get_usage(self) -> str:
        return "logout"

    def get_help(self) -> str:
        return ("Logs out the current user from the system.\n"
                "This will end your current session.\n"
                "You need to be logged in to use this command.\n"
                "Usage: logout")

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user:
            raise UnauthorizedError("You are not logged in")
        
        self._registry.set_current_user(None)
        print("Logged out successfully")
