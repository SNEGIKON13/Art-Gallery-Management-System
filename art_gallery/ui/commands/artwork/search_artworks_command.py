from typing import Sequence, List
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.domain.artwork import Artwork, ArtworkType
from art_gallery.exceptions.validation_exceptions import ValidationError

class SearchArtworksCommand(BaseCommand):
    def __init__(self, artwork_service: IArtworkService, user_service):
        super().__init__(user_service)
        self._artwork_service = artwork_service

    def execute(self, args: Sequence[str]) -> None:
        if not args:
            raise ValidationError("No search query provided")
        
        # Get all artworks
        all_artworks = self._artwork_service.get_all_artworks()
        
        # Parse arguments for search
        if args[0].startswith('--'):
            # Search by specific field
            if len(args) < 2:
                raise ValidationError("No value provided for search")
                
            field = args[0][2:]  # Remove '--' from start
            value = ' '.join(args[1:])
            
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            if field == 'type':
                try:
                    # Check type match
                    artwork_type = self._parse_artwork_type(value)
                    results = [a for a in all_artworks if a.type == artwork_type]
                except ValueError:
                    raise ValidationError(f"Unknown artwork type: {value}")
            elif field == 'artist':
                results = [a for a in all_artworks if value.lower() in a.artist.lower()]
            elif field == 'year':
                try:
                    year = int(value)
                    results = [a for a in all_artworks if a.year == year]
                except ValueError:
                    raise ValidationError("Year must be an integer")
            elif field == 'title':
                results = [a for a in all_artworks if value.lower() in a.title.lower()]
            else:
                raise ValidationError(f"Unknown search field: {field}")
        else:
            # General search by all fields
            query = ' '.join(args).lower()
            results = []
            
            for artwork in all_artworks:
                # Search by all text fields
                if (query in artwork.title.lower() or 
                    query in artwork.artist.lower() or
                    query in artwork.description.lower() or
                    query in str(artwork.year)):
                    results.append(artwork)
        
        self._display_results(results)
    
    def _parse_artwork_type(self, type_str: str) -> ArtworkType:
        """Converts string to artwork type"""
        type_str = type_str.lower()
        
        if type_str in ('painting', 'painting'):
            return ArtworkType.PAINTING
        elif type_str in ('sculpture', 'sculpture'):
            return ArtworkType.SCULPTURE
        elif type_str in ('photograph', 'photograph'):
            return ArtworkType.PHOTOGRAPH
        else:
            raise ValueError(f"Unknown artwork type: {type_str}")
    
    def _display_results(self, artworks: List[Artwork]) -> None:
        """Displays search results"""
        if not artworks:
            print("No results found for your query.")
            return
            
        print(f"Artworks found: {len(artworks)}")
        print("-" * 80)
        
        # Sort by ID for easier viewing
        sorted_artworks = sorted(artworks, key=lambda a: a.id)
        
        for artwork in sorted_artworks:
            print(f"ID: {artwork.id}")
            print(f"Title: {artwork.title}")
            print(f"Artist: {artwork.artist}")
            print(f"Year: {artwork.year}")
            print(f"Type: {artwork.type.value}")
            print("-" * 50)
            
    def get_name(self) -> str:
        return "search_artworks"
        
    def get_description(self) -> str:
        return "Search artworks by specified criteria"
        
    def get_usage(self) -> str:
        return "search_artworks <query> | search_artworks --<field> <value>"
        
    def get_help(self) -> str:
        return ("Search artworks by specified criteria.\n"
                "Usage options:\n"
                "1. search_artworks <query> - General search by title, artist, or description\n"
                "2. search_artworks --type <type> - Search by type (painting, sculpture, photograph)\n"
                "3. search_artworks --artist \"<artist name>\" - Search by artist\n"
                "4. search_artworks --year <year> - Search by year\n"
                "5. search_artworks --title \"<title>\" - Search by title")
