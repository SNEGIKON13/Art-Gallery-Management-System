import os
import webbrowser
import subprocess
import logging
from typing import Optional, Union
from urllib.parse import urlparse
from art_gallery.infrastructure.config.cli_config import CLIConfig

class ImageViewer:
    def __init__(self, config: CLIConfig):
        self._config = config
        self._logger = logging.getLogger(__name__)

    def _create_html_viewer(self, image_src: str, title: str = "Artwork View") -> str:
        """Creates a temporary HTML file to view the image
        
        Args:
            image_src: Path or URL to the image
            title: Title for the HTML page
            
        Returns:
            str: Path to the generated HTML file
        """
        # Проверяем, является ли изображение URL или локальным файлом
        is_url = self._is_url(image_src)
        
        image_tag = f'<img src="{image_src}" alt="{title}">' if is_url else f'<img src="file:///{image_src}" alt="{title}">'  
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 20px;
                    background: #1a1a1a;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                img {{ 
                    max-width: 90%;
                    max-height: 90vh;
                    object-fit: contain;
                    border: 2px solid #333;
                    box-shadow: 0 0 20px rgba(0,0,0,0.5);
                }}
                h1 {{
                    color: #fff;
                    font-family: Arial, sans-serif;
                    margin-bottom: 20px;
                }}
                .image-container {{
                    position: relative;
                    min-width: 300px;
                    min-height: 200px;
                }}
                .error-message {{
                    color: #ff5555;
                    padding: 20px;
                    text-align: center;
                    border: 1px solid #ff5555;
                    display: none;
                }}
            </style>
            <script>
                function handleImageError() {{
                    document.getElementById('error-message').style.display = 'block';
                }}
            </script>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="image-container">
                {image_tag.replace('"', '"')} <!-- заменяем кавычки для корректного отображения в строке -->
                <div id="error-message" class="error-message">
                    Error loading image. The image might be unavailable or the URL might be incorrect.
                </div>
            </div>
            <script>
                document.querySelector('img').onerror = handleImageError;
            </script>
        </body>
        </html>
        """
        # Создаем имя временного файла на основе имени изображения или случайной строки
        if isinstance(image_src, str) and not self._is_url(image_src) and os.path.exists(image_src):
            # Если это локальный файл, создаем HTML рядом с ним
            html_path = os.path.splitext(image_src)[0] + '_viewer.html'
        else:
            # Для URL или нестандартных путей создаем в временной директории
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            html_path = os.path.join(temp_dir, f"viewer_{os.urandom(4).hex()}.html")
            
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_path

    def _is_url(self, path: str) -> bool:
        """Проверяет, является ли путь URL-адресом
        
        Args:
            path: Путь или URL для проверки
            
        Returns:
            bool: True если путь является URL
        """
        parsed = urlparse(path)
        return bool(parsed.scheme and parsed.netloc)
    
    def _get_local_path(self, image_path: str) -> str:
        """Преобразует относительный путь к файлу в полный путь
        
        Args:
            image_path: Относительный или абсолютный путь к файлу
            
        Returns:
            str: Полный путь к файлу
        """
        # Проверяем, что base_media_path не None
        base_path = self._config.base_media_path or os.getcwd()
        
        # Нормализуем путь и уберем дублирование media
        normalized_path = image_path.replace('media/', '')
        return os.path.normpath(os.path.join(base_path, normalized_path))
    
    def open_image(self, image_path: str, use_web: bool = False) -> Optional[str]:
        """Opens image in default viewer or web browser
        
        Args:
            image_path: Path or URL to the image
            use_web: Whether to open in web browser
            
        Returns:
            Optional[str]: Error message or None if successful
        """
        try:
            # Проверяем, является ли путь URL-адресом
            is_url = self._is_url(image_path)
            
            if is_url:
                # Если это URL, то не открываем браузер автоматически,
                # а только выводим ссылку с инструкцией
                self._logger.info(f"Image URL: {image_path}")
                print(f"Image URL: {image_path}")
                print("\nUse Ctrl+click on the link above to open the image in your browser.")
                return None  # Успешно обработали URL
            else:
                # Для локальных файлов проверяем существование
                full_path = self._get_local_path(image_path)
                
                if not os.path.exists(full_path):
                    return f"Image file not found: {full_path}"
                    
                image_src = os.path.abspath(full_path).replace('\\', '/')
                title = os.path.basename(full_path)
                
            # Открываем изображение
            if use_web:
                # Создаем HTML просмотрщик
                # Проверяем, что base_media_path не None
                base_path = self._config.base_media_path or os.getcwd()
                temp_dir = os.path.join(base_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Используем временное имя для HTML файла
                temp_name = f"viewer_{os.urandom(4).hex()}.html"
                html_path = os.path.join(temp_dir, temp_name)
                
                # Создаем HTML просмотрщик
                html_content = self._create_html_viewer(image_src, title)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                    
                # Преобразуем путь для URL
                html_path_url = html_path.replace('\\', '/')
                webbrowser.open(f'file:///{html_path_url}', new=2)
            else:
                # Используем системный просмотрщик для локальных файлов
                if os.name == 'nt':  # Windows
                    os.startfile(full_path)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open' if os.name == 'posix' else 'open', full_path])
                    
            return None
        except Exception as e:
            error_message = f"Failed to open image: {str(e)}"
            self._logger.error(error_message)
            return error_message
