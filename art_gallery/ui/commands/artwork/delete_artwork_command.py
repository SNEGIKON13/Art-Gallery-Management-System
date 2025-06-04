from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.ui.exceptions.validation_exceptions import InvalidInputError

class DeleteArtworkCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    @admin_only
    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 1:
            raise InvalidInputError("Required: artwork_id")
        
        try:
            artwork_id = int(args[0])
            self._artwork_service.delete_artwork(artwork_id)
            print(f"Artwork {artwork_id} deleted successfully")
        except ValueError as e:
            raise InvalidInputError(str(e))

    def get_name(self) -> str:
        return "delete_artwork"

    def get_description(self) -> str:
        return "Delete artwork from gallery"

    def get_usage(self) -> str:
        return "delete_artwork <artwork_id>"
        
    def get_help(self) -> str:
        return ("Removes an artwork from the gallery.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - artwork_id: The unique identifier of the artwork to delete\n"
                "Warning: This action cannot be undone.\n"
                "Example: delete_artwork 1")
