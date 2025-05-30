from typing import List, Dict, Any
from art_gallery.domain.models.artwork import ArtworkType
   
ARTWORK_FIXTURES = [
    # Paintings
    {
        "title": "Apotheosis of War",
        "artist": "Vasily Vereshchagin",
        "year": 1871,
        "description": "An anti-war painting depicting a pyramid of human skulls in a desert landscape. A stark reminder of war's consequences.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/apotheosis.jpg"
    },
    {
        "title": "Black Square",
        "artist": "Kazimir Malevich",
        "year": 1915,
        "description": "A groundbreaking avant-garde artwork featuring a black square on white background, representing the zero point of painting.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/black_square.jpg"
    },
    {
        "title": "Morning in a Pine Forest",
        "artist": "Ivan Shishkin",
        "year": 1889,
        "description": "A naturalistic scene showing four bear cubs playing in a misty pine forest, one of Russia's most famous landscape paintings.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/morning_in_a_pine_forest.jpg"
    },
    {
        "title": "Portrait of Lopukhina",
        "artist": "Vladimir Borovikovsky",
        "year": 1797,
        "description": "A romantic portrait of Maria Lopukhina, representing the beauty ideals of Russian nobility in the 18th century.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/portrait_of_lopukhina.jpg"
    },
    {
        "title": "Ship Grove",
        "artist": "Ivan Aivazovsky",
        "year": 1898,
        "description": "A maritime landscape showcasing Aivazovsky's mastery of seascapes and atmospheric effects.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/ship_grove.jpg"
    },
    {
        "title": "The Starry Night",
        "artist": "Vincent van Gogh",
        "year": 1889,
        "description": "An iconic post-impressionist painting depicting a night scene with swirling clouds, bright stars, and a crescent moon over a village.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/starry_night.jpg"
    },
    {
        "title": "The Appearance of Christ to the People",
        "artist": "Alexander Ivanov",
        "year": 1857,
        "description": "A monumental religious painting depicting John the Baptist's revelation of Christ to the people, took 20 years to complete.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/the_appearance_of_christ_to_the_people.jpg"
    },
    {
        "title": "The Unknown Woman",
        "artist": "Ivan Kramskoi",
        "year": 1883,
        "description": "A mysterious portrait of an elegant unknown woman in a carriage, symbolizing the allure and sophistication of urban life in 19th century Russia.",
        "type": ArtworkType.PAINTING,
        "image_path": "media/paintings/unknown.jpg"
    },

    # Photographs
    {
        "title": "A Moment of Peace",
        "artist": "Shane Gross",
        "year": 2024,
        "description": "Grand Prize winning photograph capturing Western Toad tadpoles in a Vancouver lake, Canada. The image titled 'Swarm of Life' demonstrates the incredible biodiversity of wetland ecosystems.",
        "type": ArtworkType.PHOTOGRAPH,
        "image_path": "media/photographs/a_moment_of_peace.jpg"
    },
    {
        "title": "Among the Trees",
        "artist": "Thomas Peschak",
        "year": 2024,
        "description": "Award-winning photo story category winner showing Amazon river dolphins swimming through flooded forests, capturing their mysterious behavior in their natural habitat.",
        "type": ArtworkType.PHOTOGRAPH,
        "image_path": "media/photographs/among_the_trees.jpg"
    },
    {
        "title": "Hope for Nina",
        "artist": "Yannico Kelk",
        "year": 2024,
        "description": "Impact Award winning photograph of the Greater Bilby (Nina), showcasing this rare Australian marsupial in its natural environment, highlighting wildlife conservation efforts.",
        "type": ArtworkType.PHOTOGRAPH,
        "image_path": "media/photographs/hope_for_nina.jpg"
    },
    {
        "title": "Lynx Border",
        "artist": "Igor Metelsky",
        "year": 2024,
        "description": "Award-winning camera trap photograph of a lynx in its natural habitat, captured in the Lazovsky District of Primorsky Krai, Russia. Winner in the 'Animals in their Environment' category.",
        "type": ArtworkType.PHOTOGRAPH,
        "image_path": "media/photographs/lynx_border.jpg"
    },
    {
        "title": "Under Water",
        "artist": "Matthew Smith",
        "year": 2024,
        "description": "Winning photograph in the 'Underwater' category featuring a curious leopard seal in Antarctica, capturing the unique marine life of the polar regions.",
        "type": ArtworkType.PHOTOGRAPH,
        "image_path": "media/photographs/under_water.jpg"
    },

    # Sculptures
    {
        "title": "Christ's Entry into Jerusalem",
        "artist": "Giovanni Della Robbia",
        "year": 1521,
        "description": "A masterful glazed terracotta relief sculpture depicting Christ's triumphant entry into Jerusalem. Part of the Renaissance tradition of religious architectural decoration.",
        "type": ArtworkType.SCULPTURE,
        "image_path": "media/sculptures/christs_entry_into_jerusalem.jpg"
    },
    {
        "title": "Leda and the Swan",
        "artist": "Bartolomeo Ammannati",
        "year": 1535,
        "description": "A marble sculpture depicting the mythological scene of Zeus transformed into a swan approaching Leda. This Renaissance masterpiece demonstrates the period's fascination with classical mythology.",
        "type": ArtworkType.SCULPTURE,
        "image_path": "media/sculptures/leda_and_the_swan.jpg"
    },
    {
        "title": "The Abduction of Ganymede",
        "artist": "Benvenuto Cellini",
        "year": 1547,
        "description": "A bronze sculpture depicting the mythological scene of Zeus, in the form of an eagle, carrying away the young Ganymede. This work exemplifies Mannerist sculpture.",
        "type": ArtworkType.SCULPTURE,
        "image_path": "media/sculptures/the_abduction_of_ganymede.jpg"
    },
    {
        "title": "The Dying Gladiator",
        "artist": "Unknown Roman Artist",
        "year": 230,
        "description": "Also known as the Dying Gaul, this ancient Roman marble copy of a lost Hellenistic bronze original depicts a wounded Celtic warrior in his final moments.",
        "type": ArtworkType.SCULPTURE,
        "image_path": "media/sculptures/the_dying_gladiator.jpg"
    }
]

# Constants for easy access to artwork counts
TOTAL_ARTWORKS = len(ARTWORK_FIXTURES)
