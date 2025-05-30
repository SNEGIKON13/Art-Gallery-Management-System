import sys
import os

# Получаем абсолютный путь до папки art_gallery
this_dir = os.path.dirname(os.path.abspath(__file__))

# Добавляем её же в sys.path, чтобы Python видел подмодули domain/, application/, ui/ и т.д.
if this_dir not in sys.path:
    sys.path.insert(0, this_dir)

from art_gallery.ui.main import main

if __name__ == "__main__":
    main()
