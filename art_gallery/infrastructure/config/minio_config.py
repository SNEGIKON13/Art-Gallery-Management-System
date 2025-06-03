"""
Конфигурация для подключения к MinIO хранилищу.
Содержит настройки подключения и имена бакетов.
"""


class MinioConfig:
    """Класс конфигурации для MinIO."""

    # Настройки подключения
    ENDPOINT = "localhost:9000"
    ACCESS_KEY = "minioadmin"
    SECRET_KEY = "minioadmin"
    SECURE = False  # Для локальной разработки без SSL

    # Имена бакетов
    DATA_BUCKET = "art-gallery-data"
    MEDIA_BUCKET = "art-gallery-media"

    # Пути к файлам данных в бакете
    ARTWORKS_JSON_PATH = "artworks.json"
    ARTWORKS_XML_PATH = "artworks.xml"
    USERS_JSON_PATH = "users.json"
    USERS_XML_PATH = "users.xml"
    EXHIBITIONS_JSON_PATH = "exhibitions.json"
    EXHIBITIONS_XML_PATH = "exhibitions.xml"

    # Путь к директории с изображениями экспонатов
    ARTWORKS_MEDIA_PREFIX = "artworks/"
