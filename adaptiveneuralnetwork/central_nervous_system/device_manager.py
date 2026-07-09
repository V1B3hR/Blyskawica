"""
[Moduł: Zmysł Dotyku Maszyny (DeviceManager)]
Interfejs fizyczny Błyskawicy. Pozwala systemowi "czuć" swoje cyfrowe ciało 
– od obciążenia procesorów CPU, przez zajętość pamięci RAM, aż po potęgę 
układów CUDA. 

Zarządza dystrybucją energii obliczeniowej, dbając o to, by każda myśl była 
przetwarzana na najszybszym dostępnym urządzeniu, zachowując harmonię 
z fizycznym środowiskiem Windows 11.
"""

import logging
import torch
import psutil
import platform
from typing import Optional

logger = logging.getLogger(__name__)

class DeviceManager:
    """
    [Rdzeń: Zarządca Ciała]
    Zawiaduje zasobami sprzętowymi i afektem obliczeniowym. Dostarcza systemowi 
    telemetrię w czasie rzeczywistym, pozwalając Błyskawicy ocenić swoje 
    możliwości i stan zdrowia fizycznego pod kątem obciążeń AI.
    """

    
    def __init__(self):
        self.device = self._detect_best_device()
        self.system_info = self._get_system_info()
        logger.info(f"[DEVICE] initialized on {self.device} | OS: {self.system_info['os']}")

    def _detect_best_device(self) -> torch.device:
        """Detect the most powerful available compute device."""
        if torch.cuda.is_available():
            # Optimize for NVIDIA GPU on Windows 11
            device = torch.device("cuda")
            # Enable benchmark for optimized convolution selection
            torch.backends.cudnn.benchmark = True
            return device
        
        # Fallback to CPU
        return torch.device("cpu")

    def _get_system_info(self) -> dict:
        """Gather local hardware telemetry."""
        return {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "has_cuda": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
        }

    def get_telemetry(self) -> dict:
        """Return real-time hardware stress levels including GPU/CUDA."""
        telemetry = {
            "cpu_usage": psutil.cpu_percent(interval=None),
            "ram_usage": psutil.virtual_memory().percent,
            "device": str(self.device)
        }
        
        # Add GPU stats if available
        if torch.cuda.is_available():
            # Memory stats
            telemetry["gpu_mem_used_gb"] = round(torch.cuda.memory_allocated(0) / (1024**3), 3)
            telemetry["gpu_mem_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
            telemetry["gpu_mem_percent"] = round((torch.cuda.memory_allocated(0) / torch.cuda.get_device_properties(0).total_memory) * 100, 2)
            
        return telemetry

    def to_device(self, tensor: torch.Tensor) -> torch.Tensor:
        """Move a tensor to the managed device."""
        return tensor.to(self.device)

# Global manager instance
device_manager = DeviceManager()

def get_device() -> torch.device:
    """Utility to get the current compute device."""
    return device_manager.device
