import time
import os
import sys
import json
from datetime import datetime
from loguru import logger

# Add Parent Dir to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BOT_EXECUTION.polymarket_executor import PolymarketExecutor

class PolymarketBrainV1:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.executor = PolymarketExecutor(dry_run=dry_run)
        self.history_path = os.path.join(os.getcwd(), "logs", "trade_history.json")
        self.last_trades = self._load_history()
        self.network_log_path = os.path.join(os.getcwd(), "logs", "agent_network.json")
        os.makedirs(os.path.dirname(self.network_log_path), exist_ok=True)

    def _load_history(self):
        if os.path.exists(self.history_path):
            with open(self.history_path, "r") as f:
                return json.load(f)
        return []

    def _save_history(self):
        with open(self.history_path, "w") as f:
            json.dump(self.last_trades, f)

    def _autonomous_scribe(self, summary: str):
        """Scribe Agent: Writes to Obsidian daily log automatically."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = f"C:\\Users\\tiago\\Documents\\Obsidian_Brain\\04_Diário\\{today}.md"
        war_room_path = "C:\\Users\\tiago\\Documents\\Obsidian_Brain\\00_Sistemas\\Sala_de_Guerra_Agentes.md"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Append to Daily Log
        if os.path.exists(log_path):
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n- **[AUTO-SCRIBE-POLY]** {timestamp}: {summary}\n")
        
        # Mirror to War Room
        if os.path.exists(war_room_path):
            with open(war_room_path, "a", encoding="utf-8") as f:
                f.write(f"| **PolyBrain** | **Scribe** | \"Status: {summary}\" | \"Registrado no Diário de Bordo.\" |\n")

    def _autonomous_guardian(self):
        """Guardian Agent: Auto-commits and pushes to GitHub."""
        if not hasattr(self, '_scan_count'): self._scan_count = 0
        self._scan_count += 1
        
        if self._scan_count % 60 == 0:
            logger.info("[GUARDIAN] Hourly Cloud Backup for Polymarket...")
            os.system(f"cd /d E:\\PROJETO_JARVIS_POLYMARKET && git add . && git commit -m \"AUTO-GUARDIAN: Polymarket Sync\" && git push origin main")

    def _nexus_pulse(self, hype):
        """Nexus Protocol: Shares hype with the Correlator."""
        status_path = os.path.join(os.getcwd(), "logs", "poly_status.json")
        os.makedirs(os.path.dirname(status_path), exist_ok=True)
        with open(status_path, "w") as f:
            json.dump({"hype": hype, "time": datetime.now().strftime("%H:%M:%S")}, f)

    def scan_clob(self):
        """Scan Polymarket Order Book for Arbitrage and Whale Following."""
        self._autonomous_scribe("Varredura Polymarket Realizada. Caçando rastros de Baleias...")
        self._autonomous_guardian()
        self._nexus_pulse("BULLISH") # Simulated Hype
        
        logger.info(f"[POLY-BRAIN] Hunting for Whale shadows... (History: {len(self.last_trades)} trades)")
        whales = self.executor.get_whale_movements()
        
        for move in whales:
            market = move["market"]
            if market not in self.last_trades:
                logger.warning(f"[EDGE-WHALE] Detected {move['whale']} in {market}!")
                self.executor.execute_trade(market, move["side"], 100, whale_name=move["whale"])
                self.last_trades.append(market)
                self._save_history()
                self._autonomous_scribe(f"ALINHAMENTO COM BALEIA: {move['whale']} em {market}.")

        logger.info(f"[POLY-BRAIN] Hunting for Weekly Alpha... (Expiring < 48h)")
        alphas = self.executor.get_weekly_alpha()
        for alpha in alphas:
            market = alpha["market"]
            if market not in self.last_trades:
                logger.success(f"[ALPHA-STRIKE] Leading Trader '{alpha['leader']}' found in {market} (Expires: {alpha['expires']})!")
                self.executor.execute_trade(market, alpha["side"], 75, whale_name=f"ALPHA:{alpha['leader']}")
                self.last_trades.append(market)
                self._save_history()
                self._autonomous_scribe(f"ATAQUE ALPHA REINVESTIDO: Seguindo {alpha['leader']} com stake aumentado ($75).")

        logger.info(f"[POLY-BRAIN] Hunting for Hot Hands (Snipers)... (High Velocity)")
        snipers = self.executor.get_hot_hands()
        for sniper in snipers:
            market = sniper["market"]
            if market not in self.last_trades:
                logger.warning(f"[SNIPER-STRIKE] High Accuracy '{sniper['sniper']}' found in {market} (Expires: {sniper['expires']})!")
                self.executor.execute_trade(market, sniper["side"], 30, whale_name=f"SNIPER:{sniper['sniper']}") # Giro de Capital: $30
                self.last_trades.append(market)
                self._save_history()
                self._autonomous_scribe(f"ALVO SNIPER: Giro de capital seguindo {sniper['sniper']} em {market}.")
        
        time.sleep(2)

    def run(self):
        logger.info("============================================================")
        logger.info("  JARVIS_POLYMARKET - Brain Engine V1")
        logger.info("============================================================")
        
        while True:
            try:
                self.scan_clob()
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    brain = PolymarketBrainV1(dry_run=True)
    brain.run()
