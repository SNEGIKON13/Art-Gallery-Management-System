"""
Базовый сервис для работы с MinIO API.
Предоставляет методы для базовых операций с объектами в MinIO.
"""
import io
import os
from typing import Optional, BinaryIO, List, Dict, Any, Tuple, Union, cast
from urllib.parse import urljoin

from minio import Minio
from minio.error import S3Error

from art_gallery.infrastructure.config.minio_config import MinioConfig


class MinioService:
    """
    Сервис для работы с MinIO API.
    Предоставляет методы для выполнения базовых операций с объектами в MinIO.
    """

    def __init__(self, config: Optional[MinioConfig] = None):
        """
        Инициализирует сервис для работы с MinIO.
        
        Args:
            config: Конфигурация для подключения к MinIO. Если не указана,
                   используется конфигурация по умолчанию.
        """
        self.config = config or MinioConfig()
        self.client = Minio(
            endpoint=self.config.ENDPOINT,
            access_key=self.config.ACCESS_KEY,
            secret_key=self.config.SECRET_KEY,
            secure=self.config.SECURE
        )

    def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """
        Проверяет существование бакета и создает его, если он не существует.
        
        Args:
            bucket_name: Имя бакета для проверки/создания.
            
        Returns:
            bool: True, если бакет существует или был успешно создан, иначе False.
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' создан успешно")
            return True
        except S3Error as err:
            print(f"Ошибка при проверке/создании бакета '{bucket_name}': {err}")
            return False

    def upload_data(self, bucket_name: str, object_name: str, data: Union[bytes, BinaryIO],
                    content_type: str = "application/octet-stream") -> bool:
        """
        Загружает данные в MinIO.
        
        Args:
            bucket_name: Имя бакета для загрузки данных.
            object_name: Имя объекта (путь) в бакете.
            data: Данные для загрузки (байты или файлоподобный объект).
            content_type: MIME-тип содержимого.
            
        Returns:
            bool: True, если загрузка успешна, иначе False.
        """
        try:
            # Убедимся, что бакет существует
            if not self.ensure_bucket_exists(bucket_name):
                return False

            # Если data - это байты, преобразуем их в файлоподобный объект
            if isinstance(data, bytes):
                data = io.BytesIO(data)
                data_size = len(data.getvalue())
            else:
                # Определяем размер файлоподобного объекта
                data.seek(0, os.SEEK_END)
                data_size = data.tell()
                data.seek(0)

            # Загружаем данные
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=data,
                length=data_size,
                content_type=content_type
            )
            return True
        except S3Error as err:
            print(f"Ошибка при загрузке объекта '{object_name}' в бакет '{bucket_name}': {err}")
            return False

    def download_data(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """
        Скачивает данные из MinIO.
        
        Args:
            bucket_name: Имя бакета.
            object_name: Имя объекта (путь) в бакете.
            
        Returns:
            Optional[bytes]: Данные объекта или None, если объект не найден или произошла ошибка.
        """
        try:
            # Получаем объект
            response = self.client.get_object(bucket_name, object_name)
            # Читаем все данные
            data = response.read()
            # Закрываем соединение
            response.close()
            response.release_conn()
            return data
        except S3Error as err:
            if "code: NoSuchKey" in str(err):
                print(f"Объект '{object_name}' не найден в бакете '{bucket_name}'")
            else:
                print(f"Ошибка при скачивании объекта '{object_name}' из бакета '{bucket_name}': {err}")
            return None

    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """
        Удаляет объект из MinIO.
        
        Args:
            bucket_name: Имя бакета.
            object_name: Имя объекта (путь) в бакете.
            
        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            return True
        except S3Error as err:
            print(f"Ошибка при удалении объекта '{object_name}' из бакета '{bucket_name}': {err}")
            return False

    def list_objects(self, bucket_name: str, prefix: str = "", recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Получает список объектов в бакете.
        
        Args:
            bucket_name: Имя бакета.
            prefix: Префикс для фильтрации объектов.
            recursive: Искать объекты рекурсивно.
            
        Returns:
            List[Dict[str, Any]]: Список объектов с их метаданными.
        """
        try:
            objects = []
            for obj in self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive):
                objects.append({
                    'name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag
                })
            return objects
        except S3Error as err:
            print(f"Ошибка при получении списка объектов из бакета '{bucket_name}': {err}")
            return []

    def get_object_url(self, bucket_name: str, object_name: str, expires: int = 7 * 24 * 60 * 60) -> Optional[str]:
        """
        Получает URL для доступа к объекту.
        
        Args:
            bucket_name: Имя бакета.
            object_name: Имя объекта (путь) в бакете.
            expires: Время жизни URL в секундах (по умолчанию 7 дней).
            
        Returns:
            Optional[str]: URL для доступа к объекту или None, если произошла ошибка.
        """
        try:
            url = self.client.presigned_get_object(bucket_name, object_name, expires=expires)
            return url
        except S3Error as err:
            print(f"Ошибка при получении URL для объекта '{object_name}' из бакета '{bucket_name}': {err}")
            return None

    def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Проверяет существование объекта в бакете.
        
        Args:
            bucket_name: Имя бакета.
            object_name: Имя объекта (путь) в бакете.
            
        Returns:
            bool: True, если объект существует, иначе False.
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False

    def copy_object(self, source_bucket: str, source_object: str, 
                    target_bucket: str, target_object: str) -> bool:
        """
        Копирует объект внутри MinIO.
        
        Args:
            source_bucket: Исходный бакет.
            source_object: Исходный объект.
            target_bucket: Целевой бакет.
            target_object: Целевой объект.
            
        Returns:
            bool: True, если копирование успешно, иначе False.
        """
        try:
            # Убедимся, что целевой бакет существует
            if not self.ensure_bucket_exists(target_bucket):
                return False
                
            # Копируем объект
            self.client.copy_object(
                target_bucket, target_object,
                source_bucket=source_bucket, source_object=source_object
            )
            return True
        except S3Error as err:
            print(f"Ошибка при копировании объекта: {err}")
            return False
