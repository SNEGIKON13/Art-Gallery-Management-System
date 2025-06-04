from typing import Sequence, Optional
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.exceptions.validation_exceptions import InvalidInputError

class GetArtworkCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    def execute(self, args: Sequence[str]) -> Optional[str]:
        if len(args) != 1:
            raise InvalidInputError("Required: artwork_id")
        
        try:
            artwork_id = int(args[0])
            artwork = self._artwork_service.get_artwork(artwork_id)
            if artwork:
                output_lines = []
                output_lines.append(f"ID: {artwork.id}")
                output_lines.append(f"Title: {artwork.title}")
                output_lines.append(f"Artist: {artwork.artist}")
                output_lines.append(f"Year: {artwork.year}")
                output_lines.append(f"Type: {artwork.type.value if hasattr(artwork.type, 'value') else artwork.type}") # Handle if type is already a string
                output_lines.append(f"Description: {artwork.description}")
                if artwork.image_path:
                    output_lines.append(f"Image: {artwork.image_path}")
                return "\n".join(output_lines)
            else:
                return f"Artwork {artwork_id} not found"
        except ValueError as e:
            raise InvalidInputError(str(e))

    def get_name(self) -> str:
        return "get_artwork"

    def get_description(self) -> str:
        return "Get artwork details"

    def get_usage(self) -> str:
        return "get_artwork <artwork_id>"
        
    def get_help(self) -> str:
        return ("Displays detailed information about a specific artwork.\n"
                "Parameters:\n"
                "  - artwork_id: The unique identifier of the artwork\n"
                "Shows title, artist, year, type, description and image path if available.\n"
                "Example: get_artwork 1")
