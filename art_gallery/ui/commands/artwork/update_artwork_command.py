from typing import Sequence, Optional
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.ui.decorators.admin_only import admin_only
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.domain.artwork import ArtworkType
from art_gallery.ui.exceptions.validation_exceptions import InvalidInputError

class UpdateArtworkCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    @admin_only
    def execute(self, args: Sequence[str]) -> None:
        if len(args) < 2:
            raise InvalidInputError(
                "Required: artwork_id field=value [field=value ...]"
            )
        
        try:
            artwork_id = int(args[0])
            title_arg: Optional[str] = None
            artist_arg: Optional[str] = None
            year_arg: Optional[int] = None
            description_arg: Optional[str] = None
            type_arg: Optional[ArtworkType] = None
            image_path_arg: Optional[str] = None

            for arg_pair in args[1:]:
                field, value_str = arg_pair.split('=')
                if field == 'title':
                    title_arg = value_str
                elif field == 'artist':
                    artist_arg = value_str
                elif field == 'year':
                    year_arg = int(value_str)
                elif field == 'description':
                    description_arg = value_str
                elif field == 'type':
                    type_arg = ArtworkType(value_str.lower())
                elif field == 'image_path':
                    image_path_arg = value_str
                # else: # Optionally handle unknown fields, e.g., raise error or log warning
                #     pass

            artwork = self._artwork_service.update_artwork(
                artwork_id,
                title=title_arg,
                artist=artist_arg,
                year=year_arg,
                description=description_arg,
                type=type_arg,
                image_path=image_path_arg
            )
            print(f"Artwork {artwork.id} updated successfully")
        except ValueError as e:
            raise InvalidInputError(str(e))

    def get_name(self) -> str:
        return "update_artwork"

    def get_description(self) -> str:
        return "Update artwork information"

    def get_usage(self) -> str:
        return "update_artwork <id> field=value [field=value ...]"
        
    def get_help(self) -> str:
        return ("Updates information about an existing artwork.\n"
                "Only administrators can use this command.\n"
                "Parameters:\n"
                "  - id: The artwork's unique identifier\n"
                "  - field=value: One or more field updates\n"
                "Available fields:\n"
                "  - title: The artwork's name\n"
                "  - artist: The creator's name\n"
                "  - year: Year of creation\n"
                "  - type: Artwork type (painting/sculpture/photo/other)\n"
                "  - description: Artwork description\n"
                "  - image_path: Path to artwork image\n"
                "Example: update_artwork 1 title='New Title' year=1504")
