from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.validation_exceptions import ValidationError
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.application.interfaces.artwork_service import IArtworkService

class RemoveArtworkFromExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service
        self._artwork_service = artwork_service
        
    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 2:
            raise ValidationError("You must specify exhibition ID and artwork ID")
            
        try:
            exhibition_id = int(args[0])
        except ValueError:
            raise ValidationError("Exhibition ID must be an integer")
            
        try:
            artwork_id = int(args[1])
        except ValueError:
            raise ValidationError("Artwork ID must be an integer")
            
        # Check if exhibition exists
        exhibition = self._exhibition_service.get_exhibition(exhibition_id)
        if not exhibition:
            print(f"Exhibition with ID {exhibition_id} not found")
            return
            
        # Remove artwork from exhibition
        try:
            artwork = self._artwork_service.get_artwork(artwork_id)
            title = artwork.title if artwork else f"ID {artwork_id}"
            
            self._exhibition_service.remove_artwork(exhibition_id, artwork_id)
            print(f"Artwork '{title}' successfully removed from exhibition '{exhibition.title}'")
        except ValueError as e:
            print(f"Error: {str(e)}")
            
    def get_name(self) -> str:
        return "remove_artwork_from_exhibition"
        
    def get_description(self) -> str:
        return "Remove artwork from exhibition"
        
    def get_usage(self) -> str:
        return "remove_artwork_from_exhibition <exhibition_id> <artwork_id>"
        
    def get_help(self) -> str:
        return ("Removes an artwork from an exhibition.\n"
                "Both IDs must refer to existing objects in the system.\n"
                "Note that the artwork itself is not deleted from the system, only the link between it and the exhibition is removed.")
