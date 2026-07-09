"""
Sensors Status Panel - Shows sensor and camera status
"""

from rich.align import Align
from rich.panel import Panel
from rich.text import Text

from ..base import UIColors


class SensorsStatusPanel:
    """Panel showing sensors and cameras status"""

    def __init__(self, sensors_online: int = 0, sensors_total: int = 0, cameras_online: int = 0):
        self.sensors_online = sensors_online
        self.sensors_total = sensors_total
        self.cameras_online = cameras_online

    def update(self, sensors_online: int = None, sensors_total: int = None, cameras_online: int = None):
        """Update sensor status"""
        if sensors_online is not None:
            self.sensors_online = sensors_online
        if sensors_total is not None:
            self.sensors_total = sensors_total
        if cameras_online is not None:
            self.cameras_online = cameras_online

    def render(self, width: int = 22) -> Panel:
        """Render the panel"""
        text = Text()

        # Sensors status
        sensor_color = UIColors.SAFE if self.sensors_online == self.sensors_total else UIColors.WARNING
        text.append(f"📡 {self.sensors_online}/{self.sensors_total} ONLINE\n", style=sensor_color)

        # Cameras status
        camera_color = UIColors.CAMERA if self.cameras_online > 0 else UIColors.DIM
        text.append(f"🔴 {self.cameras_online} CAMERAS ON", style=camera_color)

        return Panel(
            Align.center(text), title="ACTIVE SENSORS", border_style=UIColors.SENSOR, padding=(0, 1), width=width
        )

    def render_compact(self) -> str:
        """Render compact text version"""
        return f"📡 {self.sensors_online}/{self.sensors_total} 🔴 {self.cameras_online}"
