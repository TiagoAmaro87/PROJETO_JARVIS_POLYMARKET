import asyncio
import logging
import time
import os
import gc
import random
from dotenv import load_dotenv

from hardware_engine import HardwareEngine
from jarvis_brain import JarvisBrain
from polymarket_async_core import PolymarketAsyncCore
from pillars import TradingPillars
from daily_health_check import DailyHealthCheck

load_dotenv()

# --- CONFIGURAÇÃO GLOBAL ---
PAPER_TRADING = True 
TICK_RATE = 0.2 # Modo Turbo: 5 varreduras por segundo (5Hz)

class JarvisPolymarketStable:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger("JarvisMaster")
        self.os_version = "v2.0-POLY-STABLE"
        
        self.hw = HardwareEngine()
        self.brain = JarvisBrain()
        self.core = PolymarketAsyncCore(paper_trading=PAPER_TRADING)
        self.pillars = TradingPillars(self.brain)
        self.telemetry = DailyHealthCheck(self.hw)
        
        # Gestão de Capital Segregada - 4 Caixas ($500 em cada das 3 primeiras)
        self.caixas = {
            "CAIXA_01_ARB": {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "110251828161543119357013227499774714771527179764174739487025581227481937033858", "pair_id": "65176388692130651396848427090788038285140833850265294793449655516920659740141"},
            "CAIXA_02_MM":  {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "110251828161543119357013227499774714771527179764174739487025581227481937033858"},
            "CAIXA_03_SENT": {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "110251828161543119357013227499774714771527179764174739487025581227481937033858"},
            "CAIXA_04_SNI":  {"cash": 40.0,  "inventory": 0.0, "start": 40.0,  "balance": 40.0,  "roi": 0.0, "token_id": "sniper_active"}
        }
        self.total_profit_tax = 0.0
        self.is_running = False

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - JARVIS_ULTIMATE - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(), logging.FileHandler("jarvis_stable.log", mode='w')]
        )

    async def run_market_tick(self, name, data):
        """Monitora e opera em cada módulo separadamente."""
        start_compute = time.time()
        
        # O Sniper só opera se tiver dinheiro (lucro das outras)
        if name == "CAIXA_04_SNI" and data["cash"] < 2.0:
            return

        # Preço Real do Polymarket
        current_price = await self.core.get_real_price(data["token_id"])
        if current_price <= 0: current_price = 0.01

        # --- LÓGICA DE OPERAÇÃO ---
        
        # Arbitragem: Compra se YES + NO < 0.9995 (Aproveitando micro-ineficiências)
        if name == "CAIXA_01_ARB":
            pair_price = await self.core.get_real_price(data["pair_id"])
            soma_tokens = current_price + pair_price
            
            # Log constante para o usuário ver o trabalho do robô
            if random.random() > 0.90: 
                self.logger.info(f"[{name}] SCANNER: SOMA={soma_tokens:.4f} | ALVO < 0.9995")

            if soma_tokens < 0.9995:
                # OTIMIZAÇÃO: Compra CASADA Turbo
                qty = 40.0 
                cost_yes = (current_price * qty) * 1.0005
                cost_no = (pair_price * qty) * 1.0005
                total_cost = cost_yes + cost_no
                
                if data["cash"] >= total_cost:
                    res_yes = await self.core.execute_order(name, "buy", current_price, qty, data["token_id"])
                    res_no = await self.core.execute_order(name, "buy", pair_price, qty, data["pair_id"])
                    
                    data["cash"] = float(data["cash"] - (res_yes["cost"] + res_no["cost"]))
                    data["inventory"] = float(data["inventory"] + qty) 
                    
                    self.logger.info(f"[{name}] 🎯 MICRO-ARB EXECUTADA! +${(qty - total_cost):.3f}")

        # Módulo 2: Market Making (O motor de fluxo)
        elif name == "CAIXA_02_MM":
            inv = float(data.get("inventory", 0))
            cash = float(data.get("cash", 0))
            if inv < 40:
                buy_p = current_price * 0.998
                res = await self.core.execute_order(name, "buy", buy_p, 10.0, data["token_id"])
                if cash >= res["cost"]:
                    data["cash"] = float(cash - res["cost"])
                    data["inventory"] = float(inv + res["amount"])
                    self.logger.info(f"[{name}] MM COMPRA")
            elif inv >= 10.0:
                sell_p = current_price * 1.012 # 1.2% de lucro nominal
                res = await self.core.execute_order(name, "sell", sell_p, 10.0, data["token_id"])
                data["cash"] = float(cash + res["cost"])
                data["inventory"] = float(inv - res["amount"])
                self.logger.info(f"[{name}] MM VENDA (LUCRO)")

        # Módulo 3: SENTIMENTO (Momentum - Ativo e Agressivo)
        elif name == "CAIXA_03_SENT":
            inv = float(data.get("inventory", 0))
            cash = float(data.get("cash", 0))
            if random.random() > 0.5: # 50% de chance de atuação por tick
                 if inv < 100:
                    # Compra "Market" agressiva
                    res = await self.core.execute_order(name, "buy", current_price * 1.001, 20.0, data["token_id"])
                    if cash >= res["cost"]:
                        data["cash"] = float(cash - res["cost"])
                        data["inventory"] = float(inv + res["amount"])
                        self.logger.info(f"[{name}] MOMENTUM: ENTRADA AGRESSIVA")
                 elif inv >= 20.0:
                    # Alvo de lucro curto e certeiro
                    res = await self.core.execute_order(name, "sell", current_price * 1.008, 20.0, data["token_id"])
                    data["cash"] = float(cash + res["cost"])
                    data["inventory"] = float(inv - res["amount"])
                    self.logger.info(f"[{name}] MOMENTUM: LUCRO NO BOLSO")

        # Módulo 4: SNIPER (Caçador de Cisnes Negros / Oportunidades Extremas)
        elif name == "CAIXA_04_SNI":
            c_price = await self.core.get_real_price(data["token_id"])
            if c_price <= 0: c_price = 0.05

            # A estratégia do Sniper é comprar o que o mercado acha impossível (muito barato)
            if c_price < 0.10: # Se o contrato estiver abaixo de 10 centavos
                qty_snipe = 50.0
                cost_snipe = (c_price * qty_snipe) * 1.002
                if data["cash"] >= cost_snipe:
                    res = await self.core.execute_order(name, "buy", c_price, qty_snipe, data["token_id"])
                    data["cash"] = float(data["cash"] - res["cost"])
                    data["inventory"] = float(data["inventory"] + res["amount"])
                    self.logger.info(f"[{name}] 🔫 SNIPER DISPAROU! Alvo detectado a ${c_price:.2f}")

        # --- CÁLCULO DE PATRIMÔNIO (EQUITY) ---
        inv_f = float(data.get("inventory", 0))
        cash_f = float(data.get("cash", 0))
        start_f = float(data.get("start", 500.0))

        # Valor do estoque baseado no preço de mercado atual
        valor_estoque = round(inv_f * current_price, 4)
        patrimonio_atual = round(cash_f + valor_estoque, 4)
        
        # Histórico para ROI
        last_balance = float(data.get("balance", 500.0))
        lucro_no_tick = round(patrimonio_atual - last_balance, 6)
        
        # Lógica de Taxa de Sucesso: 10% do lucro vai para o Sniper
        if lucro_no_tick > 0.001 and name != "CAIXA_04_SNI":
            taxa = round(lucro_no_tick * 0.10, 6)
            data["cash"] = float(round(cash_f - taxa, 6))
            sni_cash = float(self.caixas["CAIXA_04_SNI"].get("cash", 0))
            self.caixas["CAIXA_04_SNI"]["cash"] = float(round(sni_cash + taxa, 6))
            patrimonio_atual = round(patrimonio_atual - taxa, 4)

        data["balance"] = float(patrimonio_atual)
        data["inventory"] = float(round(inv_f, 4))
        data["roi"] = float((data["balance"] - start_f) / start_f if start_f > 0 else 0)

        self.core.latency_metrics["compute"] = (time.time() - start_compute) * 1000

    async def main_loop(self):
        self.is_running = True
        self.logger.info(f"[BOOT] Jarvis Polymarket Stable v2.0 Iniciado.")
        
        while self.is_running:
            # Check de Termodinâmica (GTX 1660)
            if not self.telemetry.check_system_viability(0, self.core.latency_metrics):
                self.logger.critical("Interrupção por Temperatura Elevada.")
                break
            
            # Processa cada caixa com dados reais do Polymarket
            tasks = []
            for name, data in self.caixas.items():
                tasks.append(self.run_market_tick(name, data))
            
            await asyncio.gather(*tasks)
            
            # Limpeza periódica
            if int(time.time()) % 120 == 0: gc.collect()
            
            # Export para o Dashboard (Paper Mode)
            self.telemetry.export_dashboard_data(self.caixas, self.core.latency_metrics, mode="POLYMARKET-REALTIME")
            
            await asyncio.sleep(TICK_RATE)

    def stop(self):
        self.is_running = False
        self.logger.info("Encerrando bot com segurança.")

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    jarvis = JarvisPolymarketStable()
    try:
        asyncio.run(jarvis.main_loop())
    except KeyboardInterrupt:
        jarvis.stop()
