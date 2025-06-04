import os
from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.domain.artwork import ArtworkType
from art_gallery.exceptions.validation_exceptions import MissingRequiredArgumentError, InvalidArgumentTypeError

class AddArtworkCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service
        # Assuming logger is available from BaseCommand or initialized here
        # For simplicity, if BaseCommand doesn't have self._logger, it should be added.
        # Or get it directly: import logging; self._logger = logging.getLogger(__name__)
        if not hasattr(self, '_logger'):
            import logging
            self._logger = logging.getLogger(__name__)

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
            raw_image_path_arg = args[5] if len(args) > 5 else None
            artwork = None

            if raw_image_path_arg and os.path.isfile(raw_image_path_arg):
                self._logger.info(f"Attempting to add artwork with image: {raw_image_path_arg}")
                try:
                    with open(raw_image_path_arg, 'rb') as image_file:
                        image_data = image_file.read()
                    image_filename = os.path.basename(raw_image_path_arg)
                    
                    artwork = self._artwork_service.add_artwork_with_image(
                        title, artist, year, description, artwork_type, 
                        image_data, image_filename
                    )
                    print(f"Artwork with image added successfully with ID: {artwork.id}")
                    if artwork.image_path:
                        print(f"Image stored at: {artwork.image_path}")
                    else:
                        print("Artwork added, but image processing might have failed. Check logs.")

                except FileNotFoundError:
                    self._logger.warning(f"Image file not found at {raw_image_path_arg}. Adding artwork without image.")
                    # Fallback to adding artwork without image if file operation fails mid-way
                    artwork = self._artwork_service.add_artwork(
                        title, artist, year, description, artwork_type, image_path=None
                    )
                    print(f"Artwork added (image not found) successfully with ID: {artwork.id}")
                except Exception as e:
                    self._logger.error(f"Error processing image file {raw_image_path_arg}: {e}", exc_info=True)
                    # Fallback to adding artwork without image on other errors
                    artwork = self._artwork_service.add_artwork(
                        title, artist, year, description, artwork_type, image_path=None
                    )
                    print(f"Artwork added (image processing error) successfully with ID: {artwork.id}. Error: {e}")
            else:
                if raw_image_path_arg:
                    self._logger.warning(f"Provided image path '{raw_image_path_arg}' is not a file or not provided. Adding artwork without image.")
                artwork = self._artwork_service.add_artwork(
                    title, artist, year, description, artwork_type, image_path=None
                )
                print(f"Artwork added successfully (without image) with ID: {artwork.id}")
        except ValueError as e:
            raise InvalidArgumentTypeError(str(e))

    def get_name(self) -> str:
        return "add_artwork"

    def get_description(self) -> str:
        return "Add new artwork to gallery"

    def get_usage(self) -> str:
        return "add_artwork <title> <artist> <year> <type> <description> [image_path]"
        
    def get_help(self) -> str:
        return ("Adds a new artwork to the gallery.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - title: The name of the artwork\n"
                "  - artist: The creator of the artwork\n"
                "  - year: Year of creation (number)\n"
                "  - type: Type of artwork (painting/sculpture/photo/other)\n"
                "  - description: Detailed description of the artwork\n"
                "  - image_path: Optional path to artwork image\n"
                "Example: add_artwork 'Mona Lisa' 'Da Vinci' 1503 painting 'Famous portrait' '/images/mona.jpg'")
