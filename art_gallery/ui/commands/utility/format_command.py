from typing import List, Optional, Sequence
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
from art_gallery.ui.command_registry import CommandRegistry
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.domain.models import User
import os
import json
import shutil
from art_gallery.infrastructure.config.config_manager import ConfigManager

class FormatCommand(ICommand):
    """Команда для переключения формата данных между JSON и XML"""
    
    def __init__(self, command_registry: CommandRegistry, user_service: IUserService, 
                 serialization_factory: SerializationPluginFactory):
        self._command_registry = command_registry
        self._user_service = user_service
        self._serialization_factory = serialization_factory
        self._config_manager = ConfigManager()
        self._current_format = self._config_manager.get("format", "json")
        self._current_user: Optional[User] = None
    
    def get_name(self) -> str:
        return "format"
        
    def get_description(self) -> str:
        return "Переключение формата данных между JSON и XML"
        
    def get_usage(self) -> str:
        return "format [json|xml]"
    
    def set_current_user(self, user: Optional[User]) -> None:
        self._current_user = user  # type: ignore[assignment]
        
    def get_help(self) -> str:
        return (
            "Команда для переключения формата данных между JSON и XML.\n"
            "Использование: format [json|xml]\n"
            "  format - показать текущий формат данных\n"
            "  format json - переключиться на формат JSON\n"
            "  format xml - переключиться на формат XML"
        )
        
    def execute(self, args: Sequence[str]) -> None:
        available_formats = self._serialization_factory.get_supported_formats()
        
        # Если аргументы не указаны, показываем текущий формат и список доступных
        if not args:
            print(f"Текущий формат данных: {self._current_format.upper()}")
            print(f"Доступные форматы: {', '.join(available_formats)}")
            print(f"Использование: format [json|xml]")
            return
        
        # Получаем запрошенный формат и проверяем его доступность
        requested_format = args[0].lower()
        if requested_format not in available_formats:
            print(f"Ошибка: Формат '{requested_format}' не поддерживается. Доступные форматы: {', '.join(available_formats)}")
            return
        
        # Если формат не изменился, просто сообщаем об этом
        if requested_format == self._current_format:
            print(f"Формат данных уже установлен на {requested_format.upper()}")
            return
        
        # Выполняем переключение формата
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, 'data')
        
        # Пути к папкам форматов
        old_format_dir = os.path.join(data_dir, self._current_format)
        new_format_dir = os.path.join(data_dir, requested_format)
        
        # Создаем папку нового формата, если она не существует
        os.makedirs(new_format_dir, exist_ok=True)
        
        # Пути к файлам в текущем формате
        old_users_file = os.path.join(old_format_dir, f'users.{self._current_format}')
        old_artworks_file = os.path.join(old_format_dir, f'artworks.{self._current_format}')
        old_exhibitions_file = os.path.join(old_format_dir, f'exhibitions.{self._current_format}')
        
        # Пути к файлам в новом формате
        new_users_file = os.path.join(new_format_dir, f'users.{requested_format}')
        new_artworks_file = os.path.join(new_format_dir, f'artworks.{requested_format}')
        new_exhibitions_file = os.path.join(new_format_dir, f'exhibitions.{requested_format}')
        
        # Проверяем, существуют ли файлы данных для текущего формата
        old_files_exist = [
            os.path.exists(old_users_file),
            os.path.exists(old_artworks_file),
            os.path.exists(old_exhibitions_file)
        ]
        
        # Проверяем, существуют ли уже файлы данных для нового формата
        new_files_exist = [
            os.path.exists(new_users_file),
            os.path.exists(new_artworks_file),
            os.path.exists(new_exhibitions_file)
        ]
        
        # Если файлы нового формата уже существуют, спрашиваем, хочет ли пользователь переключиться на них
        if any(new_files_exist):
            print(f"Найдены существующие файлы данных в формате {requested_format.upper()}.")
            print(f"Для переключения на этот формат перезапустите приложение с параметром --format {requested_format}")
            return
        
        # Если файлы текущего формата существуют, но файлы нового формата не существуют,
        # рекомендуем пользователю экспортировать данные
        if any(old_files_exist) and not any(new_files_exist):
            print(f"Данные в формате {self._current_format.upper()} будут недоступны после переключения на {requested_format.upper()}.")
            print(f"Для корректного переключения формата с сохранением данных перезапустите приложение")
            print(f"с параметром --format {requested_format}")
            return
        
        # Предлагаем экспортировать данные
        if any(old_files_exist):
            try:
                self._export_data(self._current_format, requested_format)
                print(f"Данные успешно экспортированы из {self._current_format.upper()} в {requested_format.upper()}")
            except Exception as e:
                print(f"Ошибка при экспорте данных: {e}")
                print(f"Формат не будет изменен.")
                return

        # Обновляем текущий формат и сохраняем его в конфигурацию
        self._current_format = requested_format
        self._config_manager.set("format", requested_format)
        self._config_manager.save()
        
        print(f"Формат данных изменен на: {requested_format.upper()}")
        print("Для применения изменений перезапустите приложение")
        return
        
    def _export_data(self, source_format: str, target_format: str) -> None:
        """Экспортирует данные из одного формата в другой"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, 'data')
        
        # Пути к папкам форматов
        source_dir = os.path.join(data_dir, source_format)
        target_dir = os.path.join(data_dir, target_format)
        
        # Создаем папку целевого формата, если она не существует
        os.makedirs(target_dir, exist_ok=True)
        
        # Список файлов для экспорта
        entities = ['users', 'artworks', 'exhibitions']
        
        # Для каждого типа сущности
        for entity in entities:
            source_file = os.path.join(source_dir, f'{entity}.{source_format}')
            target_file = os.path.join(target_dir, f'{entity}.{target_format}')
            
            # Пропускаем, если исходный файл не существует
            if not os.path.exists(source_file):
                continue
                
            # Загружаем данные из исходного файла
            source_deserializer = self._serialization_factory.get_deserializer(source_format)
            data = source_deserializer.deserialize_from_file(source_file)
            
            # Сохраняем в целевой файл
            target_serializer = self._serialization_factory.get_serializer(target_format)
            target_serializer.serialize_to_file(data, target_file)
