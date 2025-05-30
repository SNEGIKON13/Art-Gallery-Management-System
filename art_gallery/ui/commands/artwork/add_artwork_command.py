from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.application.services.artwork_service import IArtworkService
from art_gallery.domain.models.artwork import ArtworkType
from art_gallery.ui.exceptions.validation_exceptions import MissingRequiredArgumentError, InvalidArgumentTypeError

class AddArtworkCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    @admin_only
    def execute(self, args: Sequence[str]) -> None:
        if len(args) < 5:
            raise MissingRequiredArgumentError(
                "Required: title artist year type description [image_path]"
            )
        
        try:
            title = args[0]
            artist = args[1]
            year = int(args[2])
            artwork_type = ArtworkType(args[3].lower())
            description = args[4]
            image_path = args[5] if len(args) > 5 else None

            artwork = self._artwork_service.add_artwork(
                title, artist, year, description, artwork_type, image_path
            )
            print(f"Artwork added successfully with ID: {artwork.id}")
        except ValueError as e:
            raise InvalidArgumentTypeError(str(e))

    def get_name(self) -> str:
        return "add_artwork"

    def get_description(self) -> str:
        return "Add new artwork to gallery"

    def get_usage(self) -> str:
        return "add_artwork <title> <artist> <year> <type> <description> [image_path]"
