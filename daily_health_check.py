import os
import psutil
import logging
import time
from typing import Dict

try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

class DailyHealthCheck:
    """
    Monitor de Saúde do Hardware e Status do Sistema JARVIS.
    Focado na preservação da GTX 1660.
    """
    def __init__(self, temp_limit: float = 80.0):
        self.temp_limit = temp_limit
        self.logger = logging.getLogger("JarvisHealth")
        self.cool_down_active = False

    def check_hardware(self) -> Dict:
        status = {
            "gpu_temp": 0.0,
            "gpu_load": 0.0,
            "vram_used": 0.0,
            "cpu_load": psutil.cpu_percent(),
            "ram_used": psutil.virtual_memory().percent,
            "safe_mode": False
        }

        if HAS_GPUTIL:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                status["gpu_temp"] = gpu.temperature
                status["gpu_load"] = gpu.load * 100
                status["vram_used"] = gpu.memoryUsed
                
                if gpu.temperature > self.temp_limit:
                    self.logger.warning(f"TEMPERATURA GPU EXCEDIDA: {gpu.temperature}°C. Ativando Cool Down.")
                    status["safe_mode"] = True
                    self.cool_down_active = True
                else:
                    self.cool_down_active = False
        
        return status

    def daily_report(self, finance_data: Dict):
        """
        Exibe o Dashboard de Saúde e ROI.
        """
        hw = self.check_hardware()
        print("\n" + "="*40)
        print("   🤖 JARVIS_POLYMARKET DAILY HEALTH   ")
        print("="*40)
        print(f"🌡️  GPU Temp: {hw['gpu_temp']}°C (Limit: {self.temp_limit}°C)")
        print(f"📊 GPU Load: {hw['gpu_load']:.1f}% | VRAM: {hw['vram_used']}MB")
        print(f"💻 CPU: {hw['cpu_load']}% | RAM: {hw['ram_used']}%")
        print("-"*40)
        print("💰 FINANCEIRO (AS 4 CAIXAS)")
        for caixa, info in finance_data.items():
            print(f"- {caixa}: ${info['balance']:.2f} | ROI: {info['roi']:.2%}")
        print("="*40 + "\n")

if __name__ == "__main__":
    # Teste isolado
    checker = DailyHealthCheck()
    dummy_finance = {
        "Caixa 01 (Arb)": {"balance": 500.0, "roi": 0.02},
        "Caixa 02 (MM)": {"balance": 500.0, "roi": 0.015},
        "Caixa 03 (Sentiment)": {"balance": 500.0, "roi": -0.005},
        "Caixa 04 (Sniper)": {"balance": 0.0, "roi": 0.0}
    }
    checker.daily_report(dummy_finance)
