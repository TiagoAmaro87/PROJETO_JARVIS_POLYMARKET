import os
import psutil
import logging
import gc
from typing import Dict

try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False

class HardwareEngine:
    def __init__(self):
        self.logger = logging.getLogger("JarvisHW")
        self.gpu_handle = None
        self._init_nvml()
        self.set_normal_priority()
        self.cleanup_resources()

    def _init_nvml(self):
        if HAS_NVML:
            try:
                pynvml.nvmlInit()
                self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self.logger.info("[INIT] NVML Monitor Ativo.")
            except Exception: pass
                
    def set_normal_priority(self):
        try:
            p = psutil.Process(os.getpid())
            p.nice(psutil.NORMAL_PRIORITY_CLASS)
            self.logger.info("[SAFE] Prioridade: NORMAL")
        except: pass

    def cleanup_resources(self):
        gc.collect()
        self.logger.info("[CLEANUP] RAM limpa.")

    def get_gpu_status(self) -> Dict:
        status = {"temp": 0, "load": 0, "vram_free": 0, "vram_total": 0}
        if self.gpu_handle:
            try:
                temp = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
                util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
                mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
                status = {
                    "temp": temp, "load": util.gpu,
                    "vram_free": mem.free / (1024**2),
                    "vram_total": mem.total / (1024**2)
                }
            except: pass
        return status
