import os
import webbrowser
import subprocess
from typing import Optional
from art_gallery.infrastructure.config.cli_config import CLIConfig

class ImageViewer:
    def __init__(self, config: CLIConfig):
        self._config = config

    def _create_html_viewer(self, image_path: str, title: str = "Artwork View") -> str:
        """Creates a temporary HTML file to view the image"""
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
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <img src="file:///{image_path}" alt="{title}">
        </body>
        </html>
        """
        # Создаем временный HTML файл рядом с изображением
        html_path = os.path.splitext(image_path)[0] + '_viewer.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_path

    def open_image(self, image_path: str, use_web: bool = False) -> Optional[str]:
        """Opens image in default viewer or web browser"""
        # Нормализуем путь и уберем дублирование media
        normalized_path = image_path.replace('media/', '')
        full_path = os.path.normpath(os.path.join(self._config.base_media_path, normalized_path))
        
        if not os.path.exists(full_path):
            return f"Image file not found: {full_path}"
            
        try:
            if use_web:
                # Создаем HTML просмотрщик
                html_path = self._create_html_viewer(
                    os.path.abspath(full_path).replace('\\', '/'),
                    os.path.basename(full_path)
                )
                webbrowser.open(f'file:///{html_path}', new=2)
            else:
                if os.name == 'nt':  # Windows
                    os.startfile(full_path)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open' if os.name == 'posix' else 'open', full_path])
            return None
        except Exception as e:
            return f"Failed to open image: {str(e)}"
