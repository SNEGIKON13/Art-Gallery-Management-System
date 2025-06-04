from typing import Sequence, Optional
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
        
    def execute(self, args: Sequence[str]) -> Optional[str]:
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
        
        report_lines = []

        main_title = "=== GALLERY STATISTICS ==="
        report_lines.append(main_title)
        report_lines.append("")  # Spacer

        report_lines.append("USERS:")
        report_lines.append(f"Total users: {total_users}")
        report_lines.append(f"Active users: {active_users}")
        report_lines.append(f"Administrators: {admin_users}")
        report_lines.append("")  # Spacer

        report_lines.append("ARTWORKS:")
        report_lines.append(f"Total artworks: {total_artworks}")
        report_lines.append(f"Paintings: {paintings}")
        report_lines.append(f"Sculptures: {sculptures}")
        report_lines.append(f"Photographs: {photographs}")
        report_lines.append("")  # Spacer

        report_lines.append("EXHIBITIONS:")
        report_lines.append(f"Total exhibitions: {total_exhibitions}")
        report_lines.append(f"Active exhibitions: {active_exhibitions}")
        report_lines.append(f"Artworks in exhibitions: {artworks_in_exhibitions}")
        
        if total_artworks > 0: # Avoid division by zero if no artworks
            # Calculate percentage even if artworks_in_exhibitions is 0
            percent_displayed = (artworks_in_exhibitions / total_artworks) * 100 if total_artworks > 0 else 0
            report_lines.append(f"Percentage of artworks displayed: {percent_displayed:.1f}%")
        else:
            report_lines.append("Percentage of artworks displayed: N/A")
        
        report_lines.append("") # Spacer before bottom separator

        # Calculate max line length from the content generated so far
        max_line_length = 0
        for line in report_lines:
            # Consider stripped length for lines that might just be whitespace intended as content
            # but for simple text lines, len(line) is fine.
            # We want the visual length, so len(line) is appropriate.
            max_line_length = max(max_line_length, len(line))
        
        bottom_separator = "=" * max_line_length
        report_lines.append(bottom_separator)
            
        return "\n".join(report_lines)
            
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
