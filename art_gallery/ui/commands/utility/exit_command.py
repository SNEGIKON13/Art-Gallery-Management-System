from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
import sys

class ExitCommand(BaseCommand):
    def execute(self, args: Sequence[str]) -> None:
        print("Goodbye!")
        sys.exit(0)

    def get_name(self) -> str:
        return "exit"

    def get_description(self) -> str:
        return "Exit the application"

    def get_usage(self) -> str:
        return "exit"

    def get_help(self) -> str:
        return ("Exits the application.\n"
                "This command will save any pending changes and close the application.\n"
                "Usage: exit")
