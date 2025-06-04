from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.artwork_service import IArtworkService

class ListArtworksCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    def execute(self, args: Sequence[str]) -> str:  # Изменяем возвращаемый тип на str
        artworks = self._artwork_service.get_all_artworks()
        
        if not artworks:
            return "The gallery is empty. No artworks found."
            
        output_lines = []
        separator = "-" * 60  # Стандартный разделитель
        
        output_lines.append(f"Total artworks: {len(artworks)}")
        output_lines.append(separator)
        
        # Sort by ID for easier viewing
        sorted_artworks = sorted(artworks, key=lambda a: a.id)
        
        for artwork in sorted_artworks:
            output_lines.append(f"ID: {artwork.id}")
            output_lines.append(f"Title: {artwork.title}")
            output_lines.append(f"Artist: {artwork.artist}")
            output_lines.append(f"Year: {artwork.year}")
            output_lines.append(f"Type: {artwork.type.value}")
            output_lines.append(separator)
            
        return "\n".join(output_lines)
            
    def get_name(self) -> str:
        return "list_artworks"
        
    def get_description(self) -> str:
        return "Show a list of all artworks in the gallery"
        
    def get_usage(self) -> str:
        return "list_artworks"
        
    def get_help(self) -> str:
        return ("Displays a list of all artworks in the gallery.\n"
                "For each artwork, shows ID, title, artist, year, and type.\n"
                "For detailed information on a specific artwork, use the command 'get_artwork <id>'.")
