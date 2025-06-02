from datetime import datetime
from typing import Sequence
import os
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError
from art_gallery.ui.decorators import admin_only, authenticated, transaction, log_command
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
from art_gallery.infrastructure.config.cli_config import CLIConfig
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.exhibition_service import IExhibitionService

class ExportDataCommand(BaseCommand):
    def __init__(
        self, 
        user_service: IUserService,
        artwork_service: IArtworkService,
        exhibition_service: IExhibitionService,
        serialization_factory: SerializationPluginFactory
    ):
        super().__init__(user_service)
        self._artwork_service = artwork_service
        self._exhibition_service = exhibition_service
        self._serialization_factory = serialization_factory

import os

@admin_only
@authenticated
@transaction
@log_command
def execute(self, args: Sequence[str]) -> None:
    config = CLIConfig()
    format_type = config.serialization_config['default_format']
    
    # Генерируем имя файла с timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Создаем абсолютный путь
    export_dir = os.path.abspath("exports")
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    filepath = os.path.join(export_dir, f"backup_{timestamp}.{format_type}")
    
    try:
        data = {
            'users': [user.to_dict() for user in self._user_service.get_all_users()],
            'artworks': [artwork.to_dict() for artwork in self._artwork_service.get_all_artworks()],
            'exhibitions': [exhibition.to_dict() for exhibition in self._exhibition_service.get_all_exhibitions()]
        }
        
        plugin = self._serialization_factory.get_plugin(format_type)
        plugin.serialize_to_file(data, filepath)
        print(f"Data successfully exported to {filepath}")
        
    except Exception as e:
        raise CommandExecutionError(f"Failed to export data: {str(e)}")

    def get_name(self) -> str:
        return "export_data"

    def get_description(self) -> str:
        return "Export all gallery data to a file"

    def get_usage(self) -> str:
        return "export_data"
        
    def get_help(self) -> str:
        return ("Exports all gallery data to a file.\n"
                "Only administrators can use this command.\n"
                "The format is defined in configuration.\n"
                "Example: export_data")
