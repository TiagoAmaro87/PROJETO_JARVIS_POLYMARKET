import asyncio
import logging
import time
import os
import gc
import random
import sys
import io
from dotenv import load_dotenv

from hardware_engine import HardwareEngine
from jarvis_brain import JarvisBrain
from polymarket_async_core import PolymarketAsyncCore
from pillars import TradingPillars
from daily_health_check import DailyHealthCheck

import json

load_dotenv()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- CONFIGURAÇÃO GLOBAL ---
PAPER_TRADING = True 
TICK_RATE = 0.2 # Modo Turbo: 5Hz
STATE_FILE = "jarvis_state.json"

class JarvisPolymarketStable:
    def __init__(self):
        self.os_version = "v2.1-ULTIMATE"
        self.setup_logging()
        self.logger = logging.getLogger("JarvisMaster")
        
        self.hw = HardwareEngine()
        self.brain = JarvisBrain()
        self.core = PolymarketAsyncCore(paper_trading=PAPER_TRADING)
        self.pillars = TradingPillars(self.brain)
        self.telemetry = DailyHealthCheck(self.hw)
        
        # Gestão de Capital - 4 Caixas
        self.caixas = {
            "CAIXA_01_ARB": {
                "cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, 
                "active_index": 0,
                "targets": [
                    {"yes": "110251828161543119357013227499774714771527179764174739487025581227481937033858", "no": "65176388692130651396848427090788038285140833850265294793449655516920659740141"}, # MicroStrategy
                    {"yes": "21742457389871910906232367150745558299797034870034458925206969572242502127271", "no": "21742457389871910906232367150745558299797034870034458925206969572242502127271"}, # Bitcoin
                    {"yes": "eth_yes_mock", "no": "eth_no_mock"} # Placeholder ativos secundários
                ]
            },
            "CAIXA_02_MM":  {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "110251828161543119357013227499774714771527179764174739487025581227481937033858"},
            "CAIXA_03_SENT": {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "110251828161543119357013227499774714771527179764174739487025581227481937033858"},
            "CAIXA_04_SNI":  {"cash": 40.0,  "inventory": 0.0, "start": 40.0,  "balance": 40.0,  "roi": 0.0, "token_id": "sniper_active"}
        }
        self.load_state() 
        self.is_running = False

    def load_state(self):
        """Carrega o lucro e o estoque salvos anteriormente."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    saved_data = json.load(f)
                    # Mescla os dados salvos com a estrutura básica (mantendo IDs e alvos)
                    for k, v in saved_data.items():
                        if k in self.caixas:
                            self.caixas[k].update(v)
                self.logger.info("[RESTORE] Memória carregada: Retomando lucros anteriores.")
            except Exception as e:
                self.logger.error(f"[RESTORE] Erro ao carregar memória: {e}")

    def save_state(self):
        """Salva o progresso financeiro no disco."""
        try:
            # Salva apenas o essencial para não corromper IDs
            persist = {k: {
                "cash": v["cash"], 
                "inventory": v["inventory"], 
                "balance": v["balance"], 
                "roi": v["roi"], 
                "start": v["start"]
            } for k, v in self.caixas.items()}
            with open(STATE_FILE, "w") as f:
                json.dump(persist, f, indent=4)
        except Exception as e:
            self.logger.error(f"[SAVE] Erro ao salvar estado: {e}")

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - JARVIS_ULTIMATE - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(), logging.FileHandler("jarvis_stable.log", mode='w')]
        )

    async def run_market_tick(self, name, data):
        start_compute = time.time()
        current_price = 0.5

        # --- CAIXA 01: ARBITRAGEM (MODO HUNTER) ---
        if name == "CAIXA_01_ARB":
            target = data["targets"][data["active_index"]]
            y_p = await self.core.get_real_price(target["yes"])
            n_p = await self.core.get_real_price(target["no"])
            soma = y_p + n_p
            current_price = y_p
            
            if random.random() > 0.95:
                self.logger.info(f"[{name}] ESCANEANDO MERCADO #{data['active_index']} | SOMA: {soma:.4f}")

            if soma < 0.9995:
                qty = 40.0
                cost = soma * qty * 1.001
                if data["cash"] >= cost:
                    await self.core.execute_order(name, "buy", y_p, qty, target["yes"])
                    await self.core.execute_order(name, "buy", n_p, qty, target["no"])
                    data["cash"] = float(data["cash"] - cost)
                    data["inventory"] = float(data["inventory"] + qty)
                    self.logger.info(f"[{name}] 🎯 ARBITRAGEM GLOBAL DETECTADA!")

            data["active_index"] = (data["active_index"] + 1) % len(data["targets"])

        # --- CAIXA 02: MARKET MAKING ---
        elif name == "CAIXA_02_MM":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            if inv < 50:
                buy_p = current_price * 0.998
                res = await self.core.execute_order(name, "buy", buy_p, 10.0, data["token_id"])
                if cash >= res["cost"]:
                    data["cash"] -= res["cost"]
                    data["inventory"] += res["amount"]
                    self.logger.info(f"[{name}] MM COMPRA")
            elif inv >= 10:
                sell_p = current_price * 1.012
                res = await self.core.execute_order(name, "sell", sell_p, 10.0, data["token_id"])
                data["cash"] += res["cost"]
                data["inventory"] -= res["amount"]
                self.logger.info(f"[{name}] MM VENDA (LUCRO)")

        # --- CAIXA 03: SENTIMENTO ---
        elif name == "CAIXA_03_SENT":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            if random.random() > 0.6: # Agressivo
                if inv < 80:
                    res = await self.core.execute_order(name, "buy", current_price * 1.001, 15.0, data["token_id"])
                    if cash >= res["cost"]:
                        data["cash"] -= res["cost"]
                        data["inventory"] += res["amount"]
                        self.logger.info(f"[{name}] SENTIMENTO: ENTRADA")
                elif inv >= 15:
                    res = await self.core.execute_order(name, "sell", current_price * 1.007, 15.0, data["token_id"])
                    data["cash"] += res["cost"]
                    data["inventory"] -= res["amount"]
                    self.logger.info(f"[{name}] SENTIMENTO: LUCRO")

        # --- CAIXA 04: SNIPER ---
        elif name == "CAIXA_04_SNI":
            current_price = await self.core.get_real_price(data["token_id"])
            if current_price < 0.10: # Contratos baratos
                qty = 50.0
                cost = current_price * qty * 1.001
                if data["cash"] >= cost:
                    res = await self.core.execute_order(name, "buy", current_price, qty, data["token_id"])
                    data["cash"] -= res["cost"]
                    data["inventory"] += res["amount"]
                    self.logger.info(f"[{name}] 🔫 SNIPER DISPAROU!")

        # --- ATUALIZAÇÃO PATRIMONIAL ---
        inv_v = float(data["inventory"]) * current_price
        patrimonio = float(data["cash"] + inv_v)
        
        # Lucro para o Sniper (10%)
        lucro = patrimonio - data["balance"]
        if lucro > 0.001 and name != "CAIXA_04_SNI":
            taxa = lucro * 0.10
            data["cash"] -= taxa
            self.caixas["CAIXA_04_SNI"]["cash"] += taxa
            patrimonio -= taxa

        data["balance"] = float(patrimonio)
        start_cap = float(data["start"])
        data["roi"] = float((patrimonio - start_cap) / start_cap if start_cap > 0 else 0)
        
        self.core.latency_metrics["compute"] = (time.time() - start_compute) * 1000

    async def main_loop(self):
        self.is_running = True
        self.logger.info(f"[BOOT] Jarvis {self.os_version} Inicializado com Sucesso.")
        
        while self.is_running:
            if not self.telemetry.check_system_viability(0, self.core.latency_metrics):
                self.logger.critical("ALERTA TÉRMICO: Encerrando por segurança.")
                break
            
            tasks = [self.run_market_tick(n, d) for n, d in self.caixas.items()]
            await asyncio.gather(*tasks)
            
            # Persistência de lucro a cada 30 segundos
            if int(time.time()) % 30 == 0:
                self.save_state()
                gc.collect()
            
            self.telemetry.export_dashboard_data(self.caixas, self.core.latency_metrics, mode="POLYMARKET-TURBO")
            await asyncio.sleep(TICK_RATE)

    def stop(self):
        self.is_running = False
        self.logger.info("Sistema encerrado.")

if __name__ == "__main__":
    jarvis = JarvisPolymarketStable()
    try:
        asyncio.run(jarvis.main_loop())
    except KeyboardInterrupt:
        jarvis.stop()
