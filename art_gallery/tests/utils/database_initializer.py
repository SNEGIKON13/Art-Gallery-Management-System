import os
from art_gallery.ui.services import ServiceCollection
from art_gallery.tests.fixtures.artwork_fixtures import ARTWORK_FIXTURES
from art_gallery.tests.fixtures.exhibition_fixtures import EXHIBITION_FIXTURES

def ensure_media_directories(base_path: str) -> None:
    """Create required media directories"""
    # Создаем путь art_gallery/media/ и поддиректории
    media_path = os.path.join(base_path, "art_gallery", "media")
    for subdir in ["paintings", "sculptures", "photographs"]:
        dir_path = os.path.join(media_path, subdir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")

def initialize_test_database(services: ServiceCollection) -> None:
    """Initialize test database with fixture data"""
    print("\nInitializing test database...")
    
    # Create media directories
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    ensure_media_directories(project_root)
    
    # Initialize artworks
    for artwork_data in ARTWORK_FIXTURES:
        try:
            artwork = services.artwork_service.add_artwork(
                title=artwork_data["title"],
                artist=artwork_data["artist"],
                year=artwork_data["year"],
                description=artwork_data["description"],
                type=artwork_data["type"],
                image_path=artwork_data.get("image_path")
            )
            print(f"[SUCCESS] Added artwork: {artwork.title}")
        except Exception as e:
            print(f"[ERROR] Failed to add artwork {artwork_data['title']}: {str(e)}")
            
    # Initialize exhibitions
    for exhibition_data in EXHIBITION_FIXTURES:
        try:
            exhibition = services.exhibition_service.create_exhibition(
                title=exhibition_data["title"],
                description=exhibition_data["description"],
                start_date=exhibition_data["start_date"],
                end_date=exhibition_data["end_date"],
                max_capacity=exhibition_data["max_capacity"]
            )
            
            # Add artworks to exhibition
            for artwork_id in exhibition_data["artwork_ids"]:
                services.exhibition_service.add_artwork(exhibition.id, artwork_id)
                
            print(f"[SUCCESS] Added exhibition: {exhibition.title}")
        except Exception as e:
            print(f"[ERROR] Failed to add exhibition {exhibition_data['title']}: {str(e)}")
    
    print(f"\nDatabase initialization complete.\n"
          f"Added {len(ARTWORK_FIXTURES)} artworks and {len(EXHIBITION_FIXTURES)} exhibitions.\n")
