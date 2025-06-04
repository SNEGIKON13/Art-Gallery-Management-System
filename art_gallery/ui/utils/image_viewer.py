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

    def _is_file_uri(self, path: str) -> bool:
        """Checks if the path is a file URI."""
        parsed = urlparse(path)
        return parsed.scheme == "file"

    def _get_path_from_file_uri(self, file_uri: str) -> str:
        """Converts a file URI to an OS-specific local path."""
        parsed = urlparse(file_uri)
        # On Windows, urlparse result for 'file:///C:/path/...' is parsed.path='/C:/path/...'
        # We need to strip the leading '/' if it's followed by a drive letter like 'C:'
        # to avoid os.path.normpath turning '/C:/path' into '\C:\path'.
        path = parsed.path
        if os.name == 'nt' and path.startswith('/') and len(path) > 2 and path[1].isalpha() and path[2] == ':':
            # Path is like '/C:/Windows', convert to 'C:/Windows'
            path = path[1:]
        # For other paths like '/usr/local' (on POSIX, or if such a URI was made on Win)
        # or 'C:/Windows' (after stripping), normpath will correctly format them.
        # os.path.normpath('C:/Windows') -> 'C:\Windows'
        # os.path.normpath('/usr/local') -> '/usr/local' (POSIX) or '\usr\local' (Win)
        return os.path.normpath(path)

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
            Optional[str]: A message string (URL, success, or error).
        """
        try:
            final_os_path: str
            path_for_html_src: str

            if self._is_url(image_path):  # Checks for http/https schemes with netloc
                self._logger.info(f"Image is a web URL: {image_path}")
                return f"Image URL: {image_path}\nUse Ctrl+click on the link above to open the image in your browser."

            if self._is_file_uri(image_path):
                final_os_path = self._get_path_from_file_uri(image_path)
                path_for_html_src = final_os_path.replace('\\', '/') # For HTML src
                self._logger.info(f"Processing file URI: '{image_path}' -> OS path: '{final_os_path}'")
            else: # Is a relative or absolute local path
                final_os_path = self._get_local_path(image_path)
                path_for_html_src = os.path.abspath(final_os_path).replace('\\', '/') # For HTML src
                self._logger.info(f"Processing local path: '{image_path}' -> OS path: '{final_os_path}'")

            if not os.path.exists(final_os_path):
                self._logger.error(f"Image file not found at resolved path: {final_os_path}")
                return f"Image file not found: {final_os_path}"

            title = os.path.basename(final_os_path)

            if use_web:
                # path_for_html_src is 'C:/path/img.jpg' or a web URL.
                # _create_html_viewer handles both, creates an HTML file, and returns its path.
                created_html_file_path = self._create_html_viewer(path_for_html_src, title)
                
                # Ensure the path is absolute for webbrowser.open
                abs_html_path = os.path.abspath(created_html_file_path).replace("\\", "/")
                
                webbrowser.open(f'file:///{abs_html_path}')
                self._logger.info(f"Opened HTML viewer for {path_for_html_src} at {created_html_file_path}")
                return f"Opening image '{title}' in web browser via temporary HTML: file:///{abs_html_path}"

            else:
                opened_successfully = False
                if os.name == 'nt':  # Windows
                    try:
                        os.startfile(final_os_path)
                        opened_successfully = True
                    except Exception as e:
                        self._logger.error(f"os.startfile failed for {final_os_path}: {e}")
                        return f"Failed to open image with os.startfile: {e}"
                elif os.name == 'posix':  # macOS, Linux
                    try:
                        # Try 'xdg-open' (Linux) or 'open' (macOS)
                        cmd = 'open' if subprocess.check_output(['uname']).strip().decode() == 'Darwin' else 'xdg-open'
                        subprocess.run([cmd, final_os_path], check=True)
                        opened_successfully = True
                    except (FileNotFoundError, subprocess.CalledProcessError) as e:
                        self._logger.error(f"Command failed for {final_os_path}: {e}")
                        return f"Failed to open image with system viewer: {e}"
                else:
                    return f"Unsupported OS for opening image directly: {os.name}"

                if opened_successfully:
                    return f"Attempted to open image '{title}' with the default system viewer."
                # This part should ideally not be reached if error handling above is complete
                return f"Could not open image '{title}' with system viewer."

        except Exception as e:
            self._logger.error(f"Error opening image {image_path}: {e}", exc_info=True)
            return f"An unexpected error occurred while opening image: {str(e)}"
