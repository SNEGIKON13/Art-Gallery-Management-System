from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.ui.utils.image_viewer import ImageViewer
from art_gallery.ui.exceptions.validation_exceptions import InvalidInputError
from art_gallery.ui.exceptions.command_exceptions import CommandExecutionError
from art_gallery.infrastructure.config.cli_config import CLIConfig

class OpenArtworkImageCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service, cli_config: CLIConfig):
        super().__init__(user_service)
        self._artwork_service = artwork_service
        self._image_viewer = ImageViewer(cli_config)

    def execute(self, args: Sequence[str]) -> None:
        if len(args) < 1:
            raise InvalidInputError("Required: artwork_id [--web]")
        
        try:
            artwork_id = int(args[0])
            use_web = "--web" in args
            
            artwork = self._artwork_service.get_artwork(artwork_id)
            if not artwork:
                raise CommandExecutionError(f"Artwork {artwork_id} not found")
                
            if not artwork.image_path:
                raise CommandExecutionError(f"Artwork {artwork_id} has no image")
                
            error = self._image_viewer.open_image(artwork.image_path, use_web)
            if error:
                raise CommandExecutionError(error)
                
            print(f"Opening image for artwork {artwork_id}" + (" in web browser" if use_web else ""))
            
        except ValueError:
            raise InvalidInputError("Artwork ID must be a number")

    def get_name(self) -> str:
        return "open_image"

    def get_description(self) -> str:
        return "Open artwork image in default viewer or web browser"

    def get_usage(self) -> str:
        return "open_image <artwork_id> [--web]"
        
    def get_help(self) -> str:
        return ("Opens the artwork's image either in system's default image viewer or web browser.\n"
                "Parameters:\n"
                "  - artwork_id: The unique identifier of the artwork\n"
                "  - --web: Optional flag to open image in web browser instead of default viewer\n\n"
                "Examples:\n"
                "  1. open_image 1      # Opens in default system image viewer\n"
                "  2. open_image 1 --web # Opens in web browser\n\n"
                "Note: Image must exist and be accessible in the specified path")
