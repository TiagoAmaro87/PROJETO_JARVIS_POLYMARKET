import os
import psutil
import logging
import time
import json
from typing import Dict

class DailyHealthCheck:
    def __init__(self, hardware_engine, temp_limit: float = 80.0, dd_limit: float = 0.12):
        self.hw_engine = hardware_engine
        self.temp_limit = temp_limit
        self.dd_limit = dd_limit
        self.logger = logging.getLogger("JarvisHealth")

    def check_system_viability(self, current_balance: float) -> bool:
        hw = self.hw_engine.get_gpu_status()
        if hw["temp"] >= self.temp_limit:
            self.logger.critical("[CRITICAL] GPU overheat detected!")
            return False
        return True

    def export_dashboard_data(self, caixas: Dict, latency_metrics: Dict, mode: str = "LEAN"):
        hw = self.hw_engine.get_gpu_status()
        report = {
            "hardware": {
                "gpu_temp": hw["temp"],
                "gpu_load": hw["load"],
                "cpu_load": psutil.cpu_percent(),
                "ram_used": psutil.virtual_memory().percent,
                "safe_mode": True
            },
            "finance": caixas,
            "latency": latency_metrics,
            "timestamp": time.time(),
            "status": mode # SIMULATION ou LEAN
        }
        try:
            with open("live_status.json", "w") as f:
                json.dump(report, f, indent=4)
        except Exception as e:
            self.logger.error(f"Erro ao exportar dashboard: {e}")

    def daily_report(self, caixas: Dict, latency: Dict):
        hw = self.hw_engine.get_gpu_status()
        # Limpo de emojis para estabilidade no console do Windows
        print(f"[PAPER_TRADING] GPU: {hw['temp']}C | RAM: {psutil.virtual_memory().percent}% | COMP: {latency['compute']:.1f}ms")
