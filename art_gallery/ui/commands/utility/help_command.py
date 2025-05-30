from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.services.user_service import IUserService
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.ui.exceptions.command_exceptions import CommandNotFoundError

class HelpCommand(BaseCommand):
    def __init__(self, command_registry, user_service: IUserService, cli_config: CLIConfig):
        super().__init__(user_service)
        self._registry = command_registry
        self._cli_config = cli_config

    def execute(self, args: Sequence[str]) -> None:
        # Если указана конкретная команда (например: help login или login --help)
        if args and (args[0] != '--help'):
            command_name = args[0]
            try:
                cmd = self._registry.get_command_instance(command_name)
                help_text = (
                    f"\nCommand: {cmd.get_name()}\n"
                    f"Description: {cmd.get_description()}\n"
                    f"Usage: {cmd.get_usage()}\n"
                    f"Details: {cmd.get_help()}\n"  # Новый метод для детального описания
                )
                print(self._cli_config.format_message(help_text, "success"))
            except CommandNotFoundError:
                print(self._cli_config.format_message(f"Command '{command_name}' not found", "error"))
            return

        # Общий список команд
        available_commands = []
        for command in self._registry.get_commands():
            cmd_instance = self._registry.get_command_instance(command)
            available_commands.append(
                f"{cmd_instance.get_name()} - {cmd_instance.get_description()}\n"
                f"Usage: {cmd_instance.get_usage()}"
            )
        
        help_text = "\nAvailable commands:\n" + "\n\n".join(available_commands)
        help_text += "\n\nFor detailed help on a specific command, type: <command> --help"
        print(self._cli_config.format_message(help_text, "success"))

    def get_name(self) -> str:
        return "help"

    def get_description(self) -> str:
        return "Show list of available commands or detailed help for a specific command"

    def get_usage(self) -> str:
        return "help [command_name]"

    def get_help(self) -> str:
        return ("Displays help information for commands.\n"
                "Usage options:\n"
                "  1. help          - Shows list of all available commands\n"
                "  2. help <cmd>    - Shows detailed help for specific command\n"
                "  3. <cmd> --help  - Alternative way to get detailed help for a command")
