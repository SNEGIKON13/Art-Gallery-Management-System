from typing import Sequence
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

    def execute(self, args: Sequence[str]) -> None:
        if len(args) != 1:
            raise MissingRequiredArgumentError("Required: exhibition_id")
        
        try:
            exhibition_id = int(args[0])
            exhibition = self._exhibition_service.get_exhibition(exhibition_id)
            if exhibition:
                print(f"\nExhibition Details:")
                print(f"ID: {exhibition.id}")
                print(f"Title: {exhibition.title}")
                print(f"Description: {exhibition.description}")
                print(f"Start Date: {exhibition.start_date}")
                print(f"End Date: {exhibition.end_date}")
                print(f"Max Capacity: {exhibition.max_capacity}")
                
                if exhibition.artwork_ids:
                    print("\nArtworks in this exhibition:")
                    artwork_ids = []
                    for artwork_id in exhibition.artwork_ids:
                        artwork = self._artwork_service.get_artwork(artwork_id)
                        if artwork:
                            print(f"  - [{artwork.id}] {artwork.title} by {artwork.artist}")
                            artwork_ids.append(str(artwork.id))
                    print(f"\nArtwork IDs for reference: {', '.join(artwork_ids)}")
                    print("\nUse 'get_artwork <id>' to view details or 'open_image <id>' to view image")
                else:
                    print("\nNo artworks in this exhibition")
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
