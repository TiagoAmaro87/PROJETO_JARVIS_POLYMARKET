import asyncio
import logging
import time
import os
import json
import gc
import sys
import io
from typing import Dict, List, Any, Optional

from hardware_engine import HardwareEngine
from jarvis_brain import JarvisBrain
from polymarket_async_core import PolymarketAsyncCore
from daily_health_check import DailyHealthCheck

# Console Encoding fix
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

class MarketScanner:
    def __init__(self, config_path: str = "targets.json"):
        self.config_path = config_path
        self.load_config()
        
        self.logger = logging.getLogger("JarvisScanner")
        self.setup_logging()
        
        self.hw = HardwareEngine()
        self.brain = JarvisBrain()
        self.core = PolymarketAsyncCore(paper_trading=self.config["global_settings"].get("paper_trading", True))
        self.telemetry = DailyHealthCheck(self.hw)
        
        self.running = False
        self.stats = {
            "total_scans": 0,
            "opportunities_found": 0,
            "orders_executed": 0,
            "start_time": time.time()
        }
        
        # State management for targets
        self.state_file = "jarvis_v2_state.json"
        self.target_states = {}
        self.load_state()

    def load_state(self):
        """Carrega estados anteriores ou inicializa do config."""
        saved_data = {}
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    saved_data = json.load(f)
            except:
                pass

        for target in self.config["targets"]:
            tid = target["id"]
            if tid in saved_data:
                self.target_states[tid] = saved_data[tid]
            else:
                self.target_states[tid] = {
                    "balance": target.get("max_investment", 50.0),
                    "cash": target.get("max_investment", 50.0),
                    "inventory": 0.0,
                    "roi": 0.0,
                    "start": target.get("max_investment", 50.0)
                }

    def save_state(self):
        """Salva o estado atual dos alvos."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.target_states, f, indent=4)
        except Exception as e:
            self.logger.error(f"Erro ao salvar estado: {e}")

    def load_config(self):
        with open(self.config_path, "r") as f:
            self.config = json.load(f)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - JARVIS_SCANNER - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("jarvis_v2.log", mode='w', encoding='utf-8')
            ]
        )

    async def scan_target(self, target: Dict[str, Any]):
        """Processes a single target market based on its strategy."""
        target_id = target["id"]
        state = self.target_states[target_id]
        strategy = target.get("strategy", "arbitrage")
        
        try:
            if strategy == "arbitrage":
                y_p = await self.core.get_real_price(target["token_ids"]["yes"])
                n_p = await self.core.get_real_price(target["token_ids"]["no"])
                soma = y_p + n_p
                
                self.stats["total_scans"] += 1
                
                if soma < target.get("threshold", 0.9995):
                    self.stats["opportunities_found"] += 1
                    qty = 40.0 # Standard size for now
                    
                    res_y = await self.core.execute_order(target_id, "buy", y_p, qty, target["token_ids"]["yes"])
                    res_n = await self.core.execute_order(target_id, "buy", n_p, qty, target["token_ids"]["no"])
                    
                    total_cost = res_y["cost"] + res_n["cost"]
                    if state["cash"] >= total_cost:
                        state["cash"] -= total_cost
                        state["inventory"] += qty
                        self.logger.info(f"🎯 [ARB] {target_id} | SOMA: {soma:.4f} | EXECUTADO")
                        self.stats["orders_executed"] += 1
                    else:
                        self.logger.warning(f"⚠️ [ARB] {target_id} | Saldo insuficiente!")

                # Update balance and state
                current_value = state["inventory"] * 1.0 # In arbitrage, tokens sum to 1.0 eventually
                state["balance"] = state["cash"] + current_value
                state["roi"] = (state["balance"] - state["start"]) / state["start"] if state["start"] > 0 else 0

        except Exception as e:
            self.logger.error(f"❌ Erro ao escanear {target_id}: {e}")

    async def main_loop(self):
        self.running = True
        self.logger.info(f"🚀 Iniciando Multi-Target Scanner v2.0")
        self.logger.info(f"📡 Monitorando {len(self.config['targets'])} alvos...")

        last_dash = 0
        
        while self.running:
            # Thermal Check
            if not self.telemetry.check_system_viability(0):
                self.logger.critical("🚨 CRITICAL: System overheating or hardware failure. Shutting down.")
                break
            
            # Run scans in parallel
            active_targets = [t for t in self.config["targets"] if t.get("enabled", True)]
            tasks = [self.scan_target(t) for t in active_targets]
            await asyncio.gather(*tasks)
            
            # Dashboard update
            t_now = int(time.time())
            if t_now - last_dash >= 1:
                # Map internal states to the format expected by telemetry
                telemetry_data = {tid: s for tid, s in self.target_states.items()}
                self.telemetry.export_dashboard_data(telemetry_data, self.core.latency_metrics, mode="SCANNER-V2")
                last_dash = t_now
                
                # Periodically reload config and save state
                if t_now % 30 == 0:
                    self.save_state()
                    try:
                        self.load_config()
                    except:
                        pass
            
            await asyncio.sleep(self.config["global_settings"].get("scan_interval", 0.2))

    async def stop(self):
        self.running = False
        await self.core.close()
        self.logger.info("🛑 Scanner encerrado.")

if __name__ == "__main__":
    scanner = MarketScanner()
    try:
        asyncio.run(scanner.main_loop())
    except KeyboardInterrupt:
        asyncio.run(scanner.stop())
