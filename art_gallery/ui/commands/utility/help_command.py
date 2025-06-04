from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.ui.exceptions.command_exceptions import CommandNotFoundError

class HelpCommand(BaseCommand):
    def __init__(self, command_registry, user_service: IUserService, cli_config: CLIConfig):
        super().__init__(user_service)
        self._registry = command_registry
        self._cli_config = cli_config

    def execute(self, args: Sequence[str]) -> None:
        # If a specific command is provided (e.g., help login or login --help)
        if args and (args[0] != '--help'):
            command_name = args[0]
            try:
                cmd = self._registry.get_command_instance(command_name)
                help_text = (
                    f"\nCommand: {cmd.get_name()}\n"
                    f"Description: {cmd.get_description()}\n"
                    f"Usage: {cmd.get_usage()}\n"
                    f"Details: {cmd.get_help()}\n"
                )
                print(self._cli_config.format_message(help_text, "success"))
            except CommandNotFoundError:
                print(self._cli_config.format_message(f"Command '{command_name}' not found", "error"))
            return

        # Command categories in English
        command_categories = {
            "General": ["help", "exit"],
            "Users": ["login", "logout", "register", "change_password", "deactivate-user", "whoami", "list_users", "get_user"],
            "Artworks": ["add_artwork", "get_artwork", "update_artwork", "delete_artwork", "open_image", "list_artworks", "search_artworks", "upload_image"],
            "Exhibitions": ["create_exhibition", "get_exhibition", "update_exhibition", "delete_exhibition", "list_exhibitions", "add_artwork_to_exhibition", "remove_artwork_from_exhibition"],
            "Utilities": ["format", "stats", "convert_data"]
        }
        
        # Команды, требующие прав администратора
        admin_commands = [
            # Artworks
            "add_artwork", "update_artwork", "delete_artwork", "upload_image", 
            # Users
            "deactivate-user", "list_users", "get_user", 
            # Exhibitions
            "create_exhibition", "update_exhibition", "delete_exhibition",
            "add_artwork_to_exhibition", "remove_artwork_from_exhibition",
            # Utilities
            "format", "stats", "convert_data"
        ]
        
        # Create a dictionary for all commands
        all_commands = {}
        for command in self._registry.get_commands():
            cmd_instance = self._registry.get_command_instance(command)
            all_commands[command] = {
                "name": cmd_instance.get_name(),
                "description": cmd_instance.get_description(),
                "usage": cmd_instance.get_usage()
            }
        
        # Build help text with categories
        help_text = "\nAvailable commands:\n"
        
        # Add commands by category
        for category, cmd_list in command_categories.items():
            # Check if there are registered commands in this category
            category_commands = [cmd for cmd in cmd_list if cmd in all_commands]
            if category_commands:
                help_text += f"\n== {category} ==\n"
                for cmd_name in category_commands:
                    cmd_info = all_commands[cmd_name]
                    # Добавляем пометку (admin only) для команд администратора
                    admin_suffix = " (admin only)" if cmd_name in admin_commands else ""
                    help_text += (f"{cmd_info['name']}{admin_suffix} - {cmd_info['description']}\n"
                                f"Usage: {cmd_info['usage']}\n\n")
        
        # Add uncategorized commands if any
        all_categorized = [cmd for sublist in command_categories.values() for cmd in sublist]
        uncategorized = [cmd for cmd in all_commands if cmd not in all_categorized]
        
        if uncategorized:
            help_text += "\n== Other commands ==\n"
            for cmd_name in uncategorized:
                cmd_info = all_commands[cmd_name]
                # Добавляем пометку (admin only) для команд администратора
                admin_suffix = " (admin only)" if cmd_name in admin_commands else ""
                help_text += (f"{cmd_info['name']}{admin_suffix} - {cmd_info['description']}\n"
                            f"Usage: {cmd_info['usage']}\n\n")
        
        help_text += "\nFor detailed help on a specific command, enter: <command> --help"
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
