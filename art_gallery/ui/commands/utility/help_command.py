from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.services.user_service import IUserService
from art_gallery.infrastructure.config.cli_config import CLIConfig

class HelpCommand(BaseCommand):
    def __init__(self, command_registry, user_service: IUserService, cli_config: CLIConfig):
        super().__init__(user_service)
        self._registry = command_registry
        self._cli_config = cli_config

    def execute(self, args: Sequence[str]) -> None:
        available_commands = []
        for command in self._registry.get_commands():
            cmd_instance = self._registry.get_command_instance(command)
            available_commands.append(
                f"{cmd_instance.get_name()} - {cmd_instance.get_description()}\n"
                f"Usage: {cmd_instance.get_usage()}"
            )
        
        help_text = "\nAvailable commands:\n" + "\n\n".join(available_commands)
        print(self._cli_config.format_message(help_text, "success"))

    def get_name(self) -> str:
        return "help"

    def get_description(self) -> str:
        return "Show list of available commands"

    def get_usage(self) -> str:
        return "help"
