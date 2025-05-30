import os
import webbrowser
import subprocess
from typing import Optional

class ImageViewer:
    @staticmethod
    def open_image(image_path: str, use_web: bool = False) -> Optional[str]:
        """Opens image in default image viewer or web browser"""
        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"
            
        try:
            if use_web:
                # Convert to absolute file URL
                file_url = f"file:///{os.path.abspath(image_path)}"
                webbrowser.open(file_url)
            else:
                if os.name == 'nt':  # Windows
                    os.startfile(image_path)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open' if os.name == 'posix' else 'open', image_path])
            return None
        except Exception as e:
            return f"Failed to open image: {str(e)}"
