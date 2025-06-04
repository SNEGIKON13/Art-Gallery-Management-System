from typing import List, Optional, Sequence
import os
import logging
from art_gallery.ui.interfaces.command import ICommand
from art_gallery.ui.command_registry import CommandRegistry
from art_gallery.application.interfaces.user_service import IUserService
from art_gallery.domain import User
from art_gallery.infrastructure.factory.serialization_plugin_factory import SerializationPluginFactory
from art_gallery.infrastructure.config import ConfigRegistry

class ConvertDataCommand(ICommand):
    """Команда для конвертации данных между различными форматами (json, xml)"""
    
    def __init__(self, command_registry: CommandRegistry, user_service: IUserService, 
                 serialization_factory: SerializationPluginFactory):
        self._command_registry = command_registry
        self._user_service = user_service
        self._serialization_factory = serialization_factory
        self._config_registry = ConfigRegistry()
        self._current_user: Optional[User] = None
    
    def get_name(self) -> str:
        return "convert_data"
        
    def get_description(self) -> str:
        return "Convert data files between different formats (json, xml)"
        
    def get_usage(self) -> str:
        return "convert_data <source_format> <target_format>"
    
    def set_current_user(self, user: Optional[User]) -> None:
        self._current_user = user  # type: ignore[assignment]
        
    def get_help(self) -> str:
        return (
            "Command for converting data files between different formats.\n"
            "Usage: convert_data <source_format> <target_format>\n"
            "Example: convert_data json xml - converts data from JSON to XML\n"
            "\n"
            "Note: This command does not change the active format setting.\n"
            "It only converts the data files.\n"
            "To change the active format, use the 'format' command."
        )
        
    def execute(self, args: Sequence[str]) -> None:
        available_formats = self._serialization_factory.get_supported_formats()
        
        # Check if correct arguments are provided
        if len(args) != 2:
            print(f"Error: This command requires exactly two arguments.")
            print(f"Usage: convert_data <source_format> <target_format>")
            print(f"Available formats: {', '.join(available_formats)}")
            return
        
        source_format = args[0].lower()
        target_format = args[1].lower()
        
        # Check if the formats are valid
        if source_format not in available_formats:
            print(f"Error: Source format '{source_format}' is not supported.")
            print(f"Available formats: {', '.join(available_formats)}")
            return
            
        if target_format not in available_formats:
            print(f"Error: Target format '{target_format}' is not supported.")
            print(f"Available formats: {', '.join(available_formats)}")
            return
            
        # Check if source and target formats are different
        if source_format == target_format:
            print(f"Source and target formats are the same ({source_format}).")
            print(f"No conversion needed.")
            return
            
        # Convert the data
        try:
            success = self._convert_data(source_format, target_format)
            if success:
                print(f"Successfully converted data from {source_format.upper()} to {target_format.upper()}.")
            else:
                print(f"No data files were found for conversion from {source_format.upper()} to {target_format.upper()}.")
        except Exception as e:
            logging.error(f"Error during data conversion: {str(e)}", exc_info=True)
            print(f"Error during conversion: {str(e)}")
            return
            
    def _convert_data(self, source_format: str, target_format: str) -> bool:
        """
        Конвертирует данные из одного формата в другой.
        
        Args:
            source_format: исходный формат (json, xml)
            target_format: целевой формат (json, xml)
            
        Returns:
            bool: True если конвертация выполнена успешно
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.join(base_dir, 'data')
        
        # Проверяем существование директорий
        source_dir = os.path.join(data_dir, source_format)
        target_dir = os.path.join(data_dir, target_format)
        
        if not os.path.exists(source_dir):
            print(f"Source directory for {source_format} does not exist.")
            return False
            
        os.makedirs(target_dir, exist_ok=True)
        
        # Список сущностей для конвертации
        entities = ['users', 'artworks', 'exhibitions']
        
        # Счетчик успешных конвертаций
        converted_count = 0
        
        # Создаем сериализаторы/десериализаторы
        source_deserializer = self._serialization_factory.create_deserializer(source_format)
        target_serializer = self._serialization_factory.create_serializer(target_format)
        
        for entity in entities:
            source_file = os.path.join(source_dir, f'{entity}.{source_format}')
            target_file = os.path.join(target_dir, f'{entity}.{target_format}')
            
            # Проверяем существование исходного файла и не пуст ли он
            if os.path.exists(source_file) and os.path.getsize(source_file) > 0:
                try:
                    # Чтение данных
                    with open(source_file, 'r', encoding='utf-8') as f:
                        data = source_deserializer.deserialize(f.read())
                    
                    # Запись в новом формате
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(target_serializer.serialize(data))
                        
                    print(f"Converted {entity} from {source_format} to {target_format}")
                    converted_count += 1
                except Exception as e:
                    logging.error(f"Error converting {entity}: {str(e)}", exc_info=True)
                    print(f"Error converting {entity}: {str(e)}")
            else:
                print(f"File for {entity} in {source_format} format does not exist or is empty.")
        
        return converted_count > 0
