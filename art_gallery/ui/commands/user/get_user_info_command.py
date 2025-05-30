from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.auth_exceptions import UnauthorizedError

class GetUserInfoCommand(BaseCommand):
    def __init__(self, user_service, command_registry=None, cli_config=None):
        super().__init__(user_service, command_registry)
        self._cli_config = cli_config

    def get_name(self) -> str:
        return "whoami"

    def get_description(self) -> str:
        return "Display information about current user"

    def get_usage(self) -> str:
        return "whoami"

    def get_help(self) -> str:
        return ("Shows information about the currently logged in user.\n"
                "Displays username and role (user/administrator).\n"
                "You must be logged in to use this command.\n"
                "Usage: whoami")

    def execute(self, args: Sequence[str]) -> None:
        if not self._current_user:
            raise UnauthorizedError("You are not logged in")
        
        role = "administrator" if self._current_user.is_admin() else "user"
        info = f"Username: {self._current_user.username}\nRole: {role}"
        
        if self._cli_config:
            print(self._cli_config.format_message(info, "success"))
        else:
            print(info)
