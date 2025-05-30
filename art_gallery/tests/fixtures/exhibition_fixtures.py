from datetime import datetime, timedelta
from typing import List, Dict, Any
from art_gallery.domain.models.artwork import ArtworkType
from .artwork_fixtures import ARTWORK_FIXTURES

# Получаем списки ID артефактов по типам (с учетом того что ID начинаются с 1)
PAINTINGS = [i+1 for i, a in enumerate(ARTWORK_FIXTURES) if a["type"] == ArtworkType.PAINTING]
SCULPTURES = [i+1 for i, a in enumerate(ARTWORK_FIXTURES) if a["type"] == ArtworkType.SCULPTURE]
PHOTOGRAPHS = [i+1 for i, a in enumerate(ARTWORK_FIXTURES) if a["type"] == ArtworkType.PHOTOGRAPH]

BASE_DATE = datetime.now()

EXHIBITION_FIXTURES = [
    {
        "title": "Classical Russian Paintings",
        "description": "A journey through classical Russian paintings from different periods",
        "start_date": BASE_DATE,
        "end_date": BASE_DATE + timedelta(days=30),
        "artwork_ids": PAINTINGS,
        "max_capacity": 100
    },
    {
        "title": "Modern Photography Exhibition",
        "description": "Contemporary photography showcasing nature and wildlife",
        "start_date": BASE_DATE + timedelta(days=7),
        "end_date": BASE_DATE + timedelta(days=37),
        "artwork_ids": PHOTOGRAPHS,
        "max_capacity": 150
    },
    {
        "title": "Renaissance Sculptures",
        "description": "Collection of remarkable Renaissance sculptures",
        "start_date": BASE_DATE + timedelta(days=14),
        "end_date": BASE_DATE + timedelta(days=44),
        "artwork_ids": SCULPTURES,
        "max_capacity": 75
    }
]
