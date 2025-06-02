from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.exceptions.validation_exceptions import ValidationError
from art_gallery.application.services.exhibition_service import IExhibitionService
from art_gallery.application.services.artwork_service import IArtworkService

class AddArtworkToExhibitionCommand(BaseCommand):
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
            
        # Check if exhibition and artwork exist
        exhibition = self._exhibition_service.get_exhibition(exhibition_id)
        if not exhibition:
            print(f"Exhibition with ID {exhibition_id} not found")
            return
            
        artwork = self._artwork_service.get_artwork(artwork_id)
        if not artwork:
            print(f"Artwork with ID {artwork_id} not found")
            return
            
        # Add artwork to exhibition
        try:
            self._exhibition_service.add_artwork(exhibition_id, artwork_id)
            print(f"Artwork '{artwork.title}' successfully added to exhibition '{exhibition.title}'")
        except ValueError as e:
            print(f"Error: {str(e)}")
            
    def get_name(self) -> str:
        return "add_artwork_to_exhibition"
        
    def get_description(self) -> str:
        return "Add artwork to exhibition"
        
    def get_usage(self) -> str:
        return "add_artwork_to_exhibition <exhibition_id> <artwork_id>"
        
    def get_help(self) -> str:
        return ("Adds an existing artwork to an exhibition.\n"
                "Both IDs must refer to existing objects in the system.\n"
                "The artwork will not be added if it is already present in this exhibition.")
