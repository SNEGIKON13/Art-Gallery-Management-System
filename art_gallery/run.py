import sys
import os
import logging
from dotenv import load_dotenv # Импортируем load_dotenv

# Настроим базовый логгер
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные из .env файла
# Это нужно сделать до импорта модулей, которые могут использовать os.getenv()
load_dotenv()

# Получаем абсолютный путь до папки art_gallery
this_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем её же в sys.path, чтобы Python видел подмодули domain/, application/, ui/ и т.д.
if this_dir not in sys.path:
    sys.path.insert(0, this_dir)

# Импортируем центральный реестр конфигураций
from art_gallery.infrastructure.config.config_registry import ConfigRegistry, ConfigError

def main_with_config_validation():
    """
    Запускает приложение с валидацией конфигурации
    """
    try:
        # Инициализируем центральный реестр конфигураций
        config_registry = ConfigRegistry()
        
        # Загружаем и валидируем все конфигурации
        if not config_registry.load_configurations():
            logger.error("Конфигурация содержит ошибки. Приложение не может быть запущено.")
            sys.exit(1)
            
        # Выводим статус конфигурации
        config_registry.print_configuration_status()
        
        # Импортируем main только после успешной валидации конфигурации
        from art_gallery.ui.main import main
        
        # Запускаем приложение
        main()
        
    except ConfigError as e:
        logger.error(f"Ошибка конфигурации: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запуске приложения: {str(e)}")
        logger.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main_with_config_validation()
