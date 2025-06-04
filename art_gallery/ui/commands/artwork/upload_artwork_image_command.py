from typing import Sequence
import os
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.exceptions.validation_exceptions import InvalidInputError, MissingRequiredArgumentError
from art_gallery.exceptions.command_exceptions import CommandExecutionError


class UploadArtworkImageCommand(BaseCommand):
    """Command to upload an image for an existing artwork. (Admin only)"""
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    @admin_only
    def execute(self, args: Sequence[str]) -> None:
        if len(args) < 2:
            raise MissingRequiredArgumentError(
                "Required: artwork_id image_path"
            )
        
        try:
            artwork_id = int(args[0])
            image_path = args[1]
            
            # Check if the artwork exists
            artwork = self._artwork_service.get_artwork(artwork_id)
            if not artwork:
                raise CommandExecutionError(f"Artwork with ID {artwork_id} not found")
                
            # Check if the image file exists
            if not os.path.exists(image_path):
                raise CommandExecutionError(f"Image file not found: {image_path}")
                
            # Read the image file
            try:
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()
                    filename = os.path.basename(image_path)
                    
                    # Upload the image
                    artwork = self._artwork_service.update_artwork_image(
                        artwork_id, 
                        image_data, 
                        filename
                    )
                    
                    print(f"Image successfully uploaded for artwork {artwork_id}")
                    if hasattr(artwork, 'image_path') and artwork.image_path:
                        print(f"Image path: {artwork.image_path}")
                        
            except IOError as e:
                raise CommandExecutionError(f"Error reading image file: {e}")
            except Exception as e:
                raise CommandExecutionError(f"Error uploading image: {e}")
                
        except ValueError:
            raise InvalidInputError("Artwork ID must be a number")

    def get_name(self) -> str:
        return "upload_image"

    def get_description(self) -> str:
        return "Upload image for an artwork"

    def get_usage(self) -> str:
        return "upload_image <artwork_id> <image_path>"
        
    def get_help(self) -> str:
        return ("Uploads an image for an existing artwork.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - artwork_id: The unique identifier of the artwork\n"
                "  - image_path: Path to the image file on local system\n\n"
                "Examples:\n"
                "  upload_image 1 C:\\images\\artwork.jpg\n"
                "  upload_image 2 ./images/sculpture.png\n\n"
                "Note: The image file must exist on the local system.")
