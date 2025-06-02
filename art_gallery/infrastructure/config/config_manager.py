import os
import json
from typing import Any, Dict, Optional

class ConfigManager:
    """Менеджер для работы с конфигурацией приложения"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Инициализация менеджера конфигурации
        
        Args:
            config_file (str, optional): Путь к файлу конфигурации. 
                                        Если не указан, используется значение по умолчанию.
        """
        # Определяем директорию с данными
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        config_dir = os.path.join(base_dir, 'config')
        
        # Создаем директорию, если она не существует
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Устанавливаем путь к файлу конфигурации
        self._config_file = config_file or os.path.join(config_dir, 'app_config.json')
        self._config: Dict[str, Any] = {}
        
        # Загружаем существующую конфигурацию, если она есть
        self._load()
    
    def _load(self) -> None:
        """Загружает конфигурацию из файла"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке конфигурации: {e}")
                # Используем пустую конфигурацию при ошибке
                self._config = {}
        else:
            # Если файл не существует, используем пустую конфигурацию
            self._config = {}
    
    def save(self) -> None:
        """Сохраняет текущую конфигурацию в файл"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение по ключу
        
        Args:
            key (str): Ключ для получения значения
            default (Any, optional): Значение по умолчанию, если ключ не найден
        
        Returns:
            Any: Значение из конфигурации или значение по умолчанию
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Устанавливает значение по ключу
        
        Args:
            key (str): Ключ для установки значения
            value (Any): Значение для установки
        """
        self._config[key] = value
    
    def delete(self, key: str) -> None:
        """
        Удаляет ключ из конфигурации
        
        Args:
            key (str): Ключ для удаления
        """
        if key in self._config:
            del self._config[key]
    
    def get_all(self) -> Dict[str, Any]:
        """
        Получает копию всей конфигурации
        
        Returns:
            Dict[str, Any]: Копия конфигурации
        """
        return dict(self._config)
