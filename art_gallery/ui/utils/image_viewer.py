import os
import webbrowser
import subprocess
from typing import Optional
from art_gallery.infrastructure.config.cli_config import CLIConfig

class ImageViewer:
    def __init__(self, config: CLIConfig):
        self._config = config

    def open_image(self, image_path: str, use_web: bool = False) -> Optional[str]:
        """Opens image in default image viewer or web browser"""
        # Нормализуем путь и уберем дублирование media
        normalized_path = image_path.replace('media/', '')
        full_path = os.path.normpath(os.path.join(self._config.base_media_path, normalized_path))
        
        if not os.path.exists(full_path):
            return f"Image file not found: {full_path}"
            
        try:
            if use_web:
                # Convert to absolute file URL
                file_url = f"file:///{os.path.abspath(full_path)}"
                webbrowser.open(file_url)
            else:
                if os.name == 'nt':  # Windows
                    os.startfile(full_path)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open' if os.name == 'posix' else 'open', full_path])
            return None
        except Exception as e:
            return f"Failed to open image: {str(e)}"
