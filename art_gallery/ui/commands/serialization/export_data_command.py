from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError
from art_gallery.ui.exceptions.auth_exceptions import UnauthorizedError
from art_gallery.ui.decorators import admin_only, authenticated, transaction, log_command
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
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

    @admin_only
    @authenticated
    @transaction
    @log_command
    def execute(self, args: Sequence[str]) -> None:
        if len(args) < 2:
            raise MissingRequiredArgumentError(
                "Required: format (json/xml) and filepath"
            )
            
        format_type, filepath = args[0].lower(), args[1]
        
        try:
            # Собираем все данные
            data = {
                'users': [user.to_dict() for user in self._user_service.get_all_users()],
                'artworks': [artwork.to_dict() for artwork in self._artwork_service.get_all_artworks()],
                'exhibitions': [exhibition.to_dict() for exhibition in self._exhibition_service.get_all_exhibitions()]
            }

            # Получаем сериализатор через фабрику
            serializer = self._serialization_factory.create_serializer(format_type)
            
            # Сериализуем и сохраняем
            serializer.serialize_to_file(data, filepath)
            print(f"Data successfully exported to {filepath}")
            
        except Exception as e:
            raise CommandExecutionError(f"Failed to export data: {str(e)}")

    def get_name(self) -> str:
        return "export_data"

    def get_description(self) -> str:
        return "Export all gallery data to a file"

    def get_usage(self) -> str:
        return "export_data <format> <filepath>"
        
    def get_help(self) -> str:
        return ("Exports all gallery data to a file in specified format.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - format: The format to export (json or xml)\n"
                "  - filepath: Path where to save the file\n"
                "Example: export_data json ./backup.json")
