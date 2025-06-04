import logging
from typing import Sequence, Optional
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.ui.utils.image_viewer import ImageViewer
from art_gallery.exceptions.validation_exceptions import InvalidInputError
from art_gallery.exceptions.command_exceptions import CommandExecutionError
from art_gallery.infrastructure.config.cli_config import CLIConfig

class OpenArtworkImageCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service, cli_config: CLIConfig):
        super().__init__(user_service)
        self._artwork_service = artwork_service
        self._image_viewer = ImageViewer(cli_config)
        self._logger = logging.getLogger(__name__)

    def execute(self, args: Sequence[str]) -> Optional[str]:
        if len(args) < 1:
            raise InvalidInputError("Required: artwork_id [--web]")
        
        try:
            artwork_id = int(args[0])
            use_web = "--web" in args
            
            artwork = self._artwork_service.get_artwork(artwork_id)
            if not artwork:
                raise CommandExecutionError(f"Artwork {artwork_id} not found")
            
            # Пытаемся получить URL или путь к изображению через сервис
            image_url = self._artwork_service.get_artwork_image_url(artwork_id)
            
            # Если изображение отсутствует, пытаемся использовать классическое свойство image_path
            if not image_url and hasattr(artwork, 'image_path') and artwork.image_path:
                self._logger.info(f"Используем классический путь для изображения: {artwork.image_path}")
                image_url = artwork.image_path
                
            # Проверяем наличие изображения
            if not image_url:
                raise CommandExecutionError(f"Artwork {artwork_id} has no image")
            
            # Открываем изображение через просмотрщик
            viewer_message = self._image_viewer.open_image(image_url, use_web)

            # Check if viewer_message indicates an error
            if viewer_message and (
                "error" in viewer_message.lower() or 
                "failed" in viewer_message.lower() or 
                "not found" in viewer_message.lower() or 
                "unsupported" in viewer_message.lower() or
                "could not" in viewer_message.lower()
            ):
                raise CommandExecutionError(viewer_message)
            
            # If no error, viewer_message contains the success message to be printed by the main loop
            return viewer_message
            
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
