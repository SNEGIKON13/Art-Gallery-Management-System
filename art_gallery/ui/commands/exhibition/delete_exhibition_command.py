from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError, InvalidArgumentTypeError
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError

class DeleteExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 1:
            raise MissingRequiredArgumentError("Required: exhibition_id")
        
        try:
            exhibition_id = int(args[0])
            self._exhibition_service.delete_exhibition(exhibition_id)
            print(f"Exhibition {exhibition_id} deleted successfully")
        except ValueError:
            raise InvalidArgumentTypeError("Exhibition ID must be a number")
        except Exception as e:
            raise CommandExecutionError(f"Failed to delete exhibition: {str(e)}")

    def get_name(self) -> str:
        return "delete_exhibition"

    def get_description(self) -> str:
        return "Delete an exhibition"

    def get_usage(self) -> str:
        return "delete_exhibition <exhibition_id>"
        
    def get_help(self) -> str:
        return ("Removes an exhibition from the gallery.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - exhibition_id: The unique identifier of the exhibition to delete\n"
                "Warning: This action cannot be undone.\n"
                "Example: delete_exhibition 1")
