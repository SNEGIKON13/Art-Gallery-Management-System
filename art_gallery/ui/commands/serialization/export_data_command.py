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
from art_gallery.infrastructure.logging.interfaces.logger import ILogger, LogLevel

class ExportDataCommand(BaseCommand):
    def __init__(
        self, 
        user_service: IUserService,
        artwork_service: IArtworkService,
        exhibition_service: IExhibitionService,
        serialization_factory: SerializationPluginFactory,
        cli_config: CLIConfig,
        logger: ILogger  # Added logger
    ):
        super().__init__(user_service)
        self._artwork_service = artwork_service
        self._exhibition_service = exhibition_service
        self._serialization_factory = serialization_factory
        self._cli_config = cli_config
        self._logger = logger  # Store logger

    @admin_only
    @authenticated
    @transaction
    @log_command
    def execute(self, args: Sequence[str]) -> None:
        format_type = self._cli_config.serialization_config['default_format']
        
        custom_filename_base = args[0] if args else None

        # Определяем путь к папке exports относительно корня проекта
        export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "exports"))
        self._logger.log(LogLevel.INFO, f"Exporting to directory: {export_dir}")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            self._logger.log(LogLevel.INFO, f"Created exports directory: {export_dir}")

        if custom_filename_base:
            # Ensure the custom filename doesn't have an extension, we'll add it
            if '.' in custom_filename_base:
                custom_filename_base = os.path.splitext(custom_filename_base)[0]
            filename = f"{custom_filename_base}.{format_type}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}.{format_type}"
        
        filepath = os.path.join(export_dir, filename)
        
        try:
            actual_data = {
                'users': [user.to_dict() for user in self._user_service.get_all_users()],
                'artworks': [artwork.to_dict() for artwork in self._artwork_service.get_all_artworks()],
                'exhibitions': [exhibition.to_dict() for exhibition in self._exhibition_service.get_all_exhibitions()]
            }
            self._logger.log(LogLevel.ERROR, f"DEBUG EXPORT COUNT: {len(actual_data['users'])} users, {len(actual_data['artworks'])} artworks, {len(actual_data['exhibitions'])} exhibitions.")

            export_wrapper = {
                'version': '1.0',  # Define a version for your data format
                'exported_at': datetime.now().isoformat(),
                'data': actual_data
            }

            plugin = self._serialization_factory.get_serializer(format_type)
            plugin.serialize_to_file(data=export_wrapper, filepath=filepath)
            print(f"Data successfully exported to {filepath}")
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to export data: {str(e)}")

    def get_name(self) -> str:
        return "export_data"

    def get_description(self) -> str:
        return "Export all gallery data to a file"

    def get_usage(self) -> str:
        return "export_data [custom_filename_base]"
        
    def get_help(self) -> str:
        return ("Exports all gallery data to a file.\n"
                "Only administrators can use this command.\n"
                "The format is defined in configuration.\n"
                "Optionally, provide a custom base name for the backup file (extension will be added automatically).\n"
                "Example: export_data\n"
                "Example: export_data my_special_backup")