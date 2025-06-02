from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.validation_exceptions import InvalidInputError
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError
from art_gallery.ui.decorators import admin_only, authenticated
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory

class ConfigSerializationCommand(BaseCommand):
    def __init__(
        self, 
        user_service,
        cli_config: CLIConfig,
        serialization_factory: SerializationPluginFactory
    ):
        super().__init__(user_service)
        self._cli_config = cli_config
        self._serialization_factory = serialization_factory

    @admin_only
    @authenticated
    def execute(self, args: Sequence[str]) -> None:
        if not args:
            self._show_current_config()
            return
            
        if len(args) != 1:
            raise InvalidInputError("Required: format (json/xml)")
            
        format_type = args[0].lower()
        if format_type not in ['json', 'xml']:
            raise InvalidInputError("Format must be either 'json' or 'xml'")
            
        self._set_format(format_type)

    def _show_current_config(self) -> None:
        """Показывает текущие настройки сериализации"""
        config = self._cli_config.serialization_config
        print(self._cli_config.format_message(
            f"\nCurrent serialization settings:\n"
            f"Default format: {config['default_format']}\n"
            f"Available formats: json, xml",
            "info"
        ))

    def _set_format(self, format_type: str) -> None:
        """Устанавливает формат по умолчанию"""
        self._cli_config.serialization_config['default_format'] = format_type
        print(self._cli_config.format_message(
            f"Default format set to: {format_type}",
            "success"
        ))

    def get_name(self) -> str:
        return "config_serialization"

    def get_description(self) -> str:
        return "Configure serialization format"

    def get_usage(self) -> str:
        return "config_serialization [format]"
        
    def get_help(self) -> str:
        return ("Configure serialization format for data export/import.\n"
                "Only administrators can use this command.\n\n"
                "Usage:\n"
                "1. config_serialization         - Show current settings\n"
                "2. config_serialization json    - Set format to JSON\n"
                "3. config_serialization xml     - Set format to XML\n\n"
                "Available formats:\n"
                "- json: JSON format\n"
                "- xml: XML format")
