from typing import Sequence
from ...commands.base_command import BaseCommand
from ...decorators.admin_only import admin_only
from application.services.artwork_service import IArtworkService
from domain.models.artwork import ArtworkType
from ...exceptions.validation_exceptions import InvalidInputError

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
            updates = {}

            for arg in args[1:]:
                field, value = arg.split('=')
                if field == 'type':
                    value = ArtworkType(value.lower())
                elif field == 'year':
                    value = int(value)
                updates[field] = value

            artwork = self._artwork_service.update_artwork(artwork_id, **updates)
            print(f"Artwork {artwork.id} updated successfully")
        except ValueError as e:
            raise InvalidInputError(str(e))

    def get_name(self) -> str:
        return "update_artwork"

    def get_description(self) -> str:
        return "Update artwork information"

    def get_usage(self) -> str:
        return "update_artwork <id> field=value [field=value ...]"
