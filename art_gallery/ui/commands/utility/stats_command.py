from typing import Sequence
from art_gallery.ui.commands.base_command import BaseCommand
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.application.interfaces.artwork_service import IArtworkService
from art_gallery.application.interfaces.exhibition_service import IExhibitionService
from art_gallery.domain.artwork import ArtworkType

class StatsCommand(BaseCommand):
    def __init__(self, user_service: IUserService, artwork_service: IArtworkService, exhibition_service: IExhibitionService):
        super().__init__(user_service)
        self._artwork_service = artwork_service
        self._exhibition_service = exhibition_service
        
    def execute(self, args: Sequence[str]) -> None:
        # Get statistics
        users = self._user_service.get_all_users()
        artworks = self._artwork_service.get_all_artworks()
        exhibitions = self._exhibition_service.get_all_exhibitions()
        
        # User statistics
        total_users = len(users)
        active_users = sum(1 for user in users if user.is_active)
        admin_users = sum(1 for user in users if user.role.name == "ADMIN")
        
        # Artwork statistics
        total_artworks = len(artworks)
        paintings = sum(1 for artwork in artworks if artwork.type == ArtworkType.PAINTING)
        sculptures = sum(1 for artwork in artworks if artwork.type == ArtworkType.SCULPTURE)
        photographs = sum(1 for artwork in artworks if artwork.type == ArtworkType.PHOTOGRAPH)
        
        # Exhibition statistics
        total_exhibitions = len(exhibitions)
        artworks_in_exhibitions = sum(len(exhibition.artwork_ids) for exhibition in exhibitions)
        active_exhibitions = sum(1 for exhibition in exhibitions if exhibition.is_active())
        
        # Print statistics
        print("\n=== GALLERY STATISTICS ===")
        print("\nUSERS:")
        print(f"Total users: {total_users}")
        print(f"Active users: {active_users}")
        print(f"Administrators: {admin_users}")
        
        print("\nARTWORKS:")
        print(f"Total artworks: {total_artworks}")
        print(f"Paintings: {paintings}")
        print(f"Sculptures: {sculptures}")
        print(f"Photographs: {photographs}")
        
        print("\nEXHIBITIONS:")
        print(f"Total exhibitions: {total_exhibitions}")
        print(f"Active exhibitions: {active_exhibitions}")
        print(f"Artworks in exhibitions: {artworks_in_exhibitions}")
        
        if artworks_in_exhibitions > 0 and total_artworks > 0:
            percent_displayed = (artworks_in_exhibitions / total_artworks) * 100
            print(f"Percentage of artworks displayed: {percent_displayed:.1f}%")
            
        print("\n=========================")
            
    def get_name(self) -> str:
        return "stats"
        
    def get_description(self) -> str:
        return "Show gallery statistics"
        
    def get_usage(self) -> str:
        return "stats"
        
    def get_help(self) -> str:
        return ("Displays overall statistics for the gallery management system.\n"
                "Includes information on:\n"
                "- Number of users and their statuses\n"
                "- Number of artworks by type\n"
                "- Number of exhibitions and artworks on display")
