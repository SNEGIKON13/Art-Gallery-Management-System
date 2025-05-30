from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.services.artwork_service import IArtworkService
from art_gallery.ui.exceptions.validation_exceptions import InvalidInputError

class GetArtworkCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 1:
            raise InvalidInputError("Required: artwork_id")
        
        try:
            artwork_id = int(args[0])
            artwork = self._artwork_service.get_artwork(artwork_id)
            if artwork:
                print(f"ID: {artwork.id}")
                print(f"Title: {artwork.title}")
                print(f"Artist: {artwork.artist}")
                print(f"Year: {artwork.year}")
                print(f"Type: {artwork.type.value}")
                print(f"Description: {artwork.description}")
                if artwork.image_path:
                    print(f"Image: {artwork.image_path}")
            else:
                print(f"Artwork {artwork_id} not found")
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
