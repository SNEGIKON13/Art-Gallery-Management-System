from typing import Sequence, Optional
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.exceptions.validation_exceptions import MissingRequiredArgumentError, InvalidArgumentTypeError
from art_gallery.exceptions.command_exceptions import CommandExecutionError

class GetExhibitionCommand(BaseCommand):
    def __init__(self, exhibition_service: IExhibitionService, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._exhibition_service = exhibition_service
        self._artwork_service = artwork_service

    def execute(self, args: Sequence[str]) -> Optional[str]:
        if len(args) != 1:
            raise MissingRequiredArgumentError("Required: exhibition_id")
        
        try:
            exhibition_id = int(args[0])
            exhibition = self._exhibition_service.get_exhibition(exhibition_id)
            if exhibition:
                output_lines = []
                output_lines.append(f"Exhibition Details:") # Removed leading \n, main.py handles spacing
                output_lines.append(f"ID: {exhibition.id}")
                output_lines.append(f"Title: {exhibition.title}")
                output_lines.append(f"Description: {exhibition.description}")
                output_lines.append(f"Start Date: {exhibition.start_date}")
                output_lines.append(f"End Date: {exhibition.end_date}")
                output_lines.append(f"Max Capacity: {exhibition.max_capacity if exhibition.max_capacity is not None else 'N/A'}")
                
                if exhibition.artwork_ids:
                    output_lines.append("\nArtworks in this exhibition:")
                    artwork_display_ids = []
                    for artwork_id_in_exh in exhibition.artwork_ids:
                        artwork = self._artwork_service.get_artwork(artwork_id_in_exh)
                        if artwork:
                            output_lines.append(f"  - [{artwork.id}] {artwork.title} by {artwork.artist}")
                            artwork_display_ids.append(str(artwork.id))
                    if artwork_display_ids:
                        output_lines.append(f"\nArtwork IDs for reference: {', '.join(artwork_display_ids)}")
                        output_lines.append("\nUse 'get_artwork <id>' to view details or 'open_image <id>' to view image")
                    else:
                        output_lines.append("\nArtworks listed for this exhibition could not be found.")
                else:
                    output_lines.append("\nNo artworks in this exhibition")
                return "\n".join(output_lines)
            else:
                raise CommandExecutionError(f"Exhibition with ID {exhibition_id} not found")
        except ValueError:
            raise InvalidArgumentTypeError("Exhibition ID must be a number")

    def get_name(self) -> str:
        return "get_exhibition"

    def get_description(self) -> str:
        return "Get exhibition details and list of artworks"

    def get_usage(self) -> str:
        return "get_exhibition <exhibition_id>"
        
    def get_help(self) -> str:
        return ("Shows detailed information about a specific exhibition and its artworks.\n"
                "Parameters:\n"
                "  - exhibition_id: The unique identifier of the exhibition\n\n"
                "Output includes:\n"
                "  - Basic exhibition information (title, dates, capacity)\n"
                "  - List of artworks with their IDs\n"
                "  - You can use 'get_artwork <id>' to view detailed information about specific artwork\n\n"
                "Example: \n"
                "  1. get_exhibition 1\n"
                "  2. get_artwork 5  (to view details of artwork with ID 5 from the exhibition)\n\n"
                "Note: This command is available to all users")
