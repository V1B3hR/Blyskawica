"""
Dashboard Themes
"""

import logging
from enum import Enum


class ThemeType(Enum):
    """Available theme types"""

    DARK = "dark"
    LIGHT = "light"
    BLUE = "blue"
    MATRIX = "matrix"


class ThemeManager:
    """Manages dashboard themes"""

    def __init__(self):
        self.logger = logging.getLogger("nethical.theme_manager")
        self._initialize_logger()
        self.current_theme = ThemeType.DARK
        self.themes = {
            ThemeType.DARK: {"primary": "#1a1a1a", "secondary": "#2d2d2d", "accent": "#00ff00", "text": "#ffffff"},
            ThemeType.LIGHT: {"primary": "#ffffff", "secondary": "#f0f0f0", "accent": "#0066cc", "text": "#000000"},
            ThemeType.BLUE: {"primary": "#001f3f", "secondary": "#003d7a", "accent": "#0074D9", "text": "#ffffff"},
            ThemeType.MATRIX: {"primary": "#000000", "secondary": "#001100", "accent": "#00ff00", "text": "#00ff00"},
        }

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [ThemeManager] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def set_theme(self, theme_type: ThemeType):
        """Set current theme"""
        self.current_theme = theme_type
        self.logger.info(f"Theme changed to: {theme_type.value}")

    def get_theme_colors(self) -> dict[str, str]:
        """Get current theme colors"""
        return self.themes[self.current_theme]
