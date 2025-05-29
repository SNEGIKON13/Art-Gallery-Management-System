from typing import Sequence
from base_command import BaseCommand
from application.services.user_service import IUserService

class HelpCommand(BaseCommand):
    def __init__(self, command_registry, user_service: IUserService):
        super().__init__(user_service)
        self._registry = command_registry

    def execute(self, args: Sequence[str]) -> None:
        available_commands = []
        for command in self._registry.get_commands():
            cmd_instance = self._registry.get_command_instance(command)
            available_commands.append(
                f"{cmd_instance.get_name()} - {cmd_instance.get_description()}\n"
                f"Usage: {cmd_instance.get_usage()}"
            )
        
        print("\nAvailable commands:\n" + "\n\n".join(available_commands))

    def get_name(self) -> str:
        return "help"

    def get_description(self) -> str:
        return "Show list of available commands"

    def get_usage(self) -> str:
        return "help"
