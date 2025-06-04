import sys
import os
from dotenv import load_dotenv # Импортируем load_dotenv

# Загружаем переменные из .env файла
# Это нужно сделать до импорта модулей, которые могут использовать os.getenv()
load_dotenv()

# Получаем абсолютный путь до папки art_gallery
this_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем её же в sys.path, чтобы Python видел подмодули domain/, application/, ui/ и т.д.
if this_dir not in sys.path:
    sys.path.insert(0, this_dir)

# Теперь, когда .env загружен, можно импортировать остальные модули
from art_gallery.ui.main import main


if __name__ == "__main__":
    main()
