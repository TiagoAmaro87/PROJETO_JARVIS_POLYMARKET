import asyncio
import logging
import time
import os
import gc
import random
import sys
import io
from typing import Dict, List, Any, cast
from datetime import datetime
from dotenv import load_dotenv

from hardware_engine import HardwareEngine
from jarvis_brain import JarvisBrain
from polymarket_async_core import PolymarketAsyncCore
from pillars import TradingPillars
from daily_health_check import DailyHealthCheck

import json

load_dotenv()

# Melhora a compatibilidade UTF-8 no console do Windows
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

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
        self.caixas: Dict[str, Any] = {
            "CAIXA_01_ARB": {
                "cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, 
                "active_index": 0,
                "targets": [
                    {"yes": "75467129615908319583031474642658885479135630431889036121812713428992454630178", "no": "3842963720267267286970642336860752782302644680156535061700039388405652129691"}, # BitBoy Convicted
                    {"yes": "8501497159083948713316135768103773293754490207922884688769443031624417212426", "no": "2527312495175492857904889758552137141356236738032676480522356889996545113869"}, # RU-UK Ceasefire
                    {"yes": "98022490269692409998126496127597032490334070080325855126491859374983463996227", "no": "53831553061883006530739877284105938919721408776239639687877978808906551086026"}  # Rihanna Album
                ]
            },
            "CAIXA_02_MM":  {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "110251828161543119357013227499774714771527179764174739487025581227481937033858"},
            "CAIXA_03_SENT": {"cash": 500.0, "inventory": 0.0, "start": 500.0, "balance": 500.0, "roi": 0.0, "token_id": "65176388692130651396848427090788038285140833850265294793449655516920659740141"},
            "CAIXA_04_SNI":  {"cash": 40.0,  "inventory": 0.0, "start": 40.0,  "balance": 40.0,  "roi": 0.0, "token_id": "90435811253665578014957380826505992530054077692143838383981805324273750424057"}
        }

        self.load_state() 
        self.is_running = False
        self._last_save = 0
        self._last_dash = 0
        self._last_history_save = 0
        self.trades_file = "trades_history.json"
        self.history_file = "wealth_history.json"
        
        # Load or init trade history
        if not os.path.exists(self.trades_file):
            with open(self.trades_file, "w") as f:
                json.dump([], f)

    def load_state(self):
        """Carrega o lucro e o estoque salvos anteriormente."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    saved_data = json.load(f)
                    # Mescla os dados salvos com a estrutura básica (mantendo IDs e alvos)
                    for k, v in cast(Dict[str, Any], saved_data).items():
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

    async def run_market_tick(self, name: str, data: Dict[str, Any]):
        start_compute = time.time()
        current_price = 0.5

        # --- CAIXA 01: ARBITRAGEM (MODO HUNTER) ---
        if name == "CAIXA_01_ARB":
            target = data["targets"][data["active_index"]]
            y_p = await self.core.get_real_price(target["yes"])
            n_p = await self.core.get_real_price(target["no"])
            soma = y_p + n_p
            current_price = float(soma) # Na arbitragem, o preço do conjunto é a soma
            
            if random.random() > 0.98:
                self.logger.info(f"[{name}] ESCANEANDO MERCADO #{data['active_index']} | SOMA: {float(soma):.4f}")

            # --- CÁLCULO DE VIABILIDADE REAL (NET PROFIT) ---
            qty = 60.0 # Aumentamos o volume para diluir o custo do GAS
            est_gas = self.core.polygon_gas_price * 2 # YES + NO
            payout = qty # Cada par YES/NO vale $1.00 no vencimento
            est_cost = (y_p + n_p) * qty * (1 + self.core.fee_rate) + est_gas
            
            potential_net_profit = payout - est_cost
            
            # Só executa se o lucro líquido estimado for maior que $0.20 (Buffer de segurança)
            if potential_net_profit > 0.20:
                # Executa ordens e usa os custos reais retornados pela simulação
                res_y = await self.core.execute_order(name, "buy", y_p, qty, target["yes"])
                res_n = await self.core.execute_order(name, "buy", n_p, qty, target["no"])
                
                total_cost = float(res_y["cost"]) + float(res_n["cost"])
                if float(data["cash"]) >= total_cost:
                    data["cash"] = float(data["cash"]) - total_cost
                    data["inventory"] = float(data["inventory"]) + qty
                    self.logger.info(f"[{name}] 🎯 ARBITRAGEM INTELIGENTE | Lucro Est: ${potential_net_profit:.2f}")
                    self.log_trade(name, "BUY_ARB", total_cost, qty, target["yes"])
                else:
                    self.logger.warning(f"[{name}] Saldo insuficiente para arbitragem inteligente!")

            data["active_index"] = (int(data["active_index"]) + 1) % len(cast(list, data["targets"]))

        # --- CAIXA 02: MARKET MAKING ---
        elif name == "CAIXA_02_MM":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            if inv < 50:
                buy_p = current_price * 0.998
                res = await self.core.execute_order(name, "buy", buy_p, 10.0, data["token_id"])
                if float(cash) >= float(res["cost"]):
                    data["cash"] = float(data["cash"]) - float(res["cost"])
                    data["inventory"] = float(data["inventory"]) + float(res["amount"])
                    self.logger.info(f"[{name}] MM COMPRA")
            elif inv >= 10:
                sell_p = current_price * 1.012
                res = await self.core.execute_order(name, "sell", sell_p, 10.0, data["token_id"])
                data["cash"] = float(data["cash"]) + float(res["cost"])
                data["inventory"] = float(data["inventory"]) - float(res["amount"])
                self.logger.info(f"[{name}] MM VENDA (LUCRO)")
                self.log_trade(name, "SELL_MM", res["cost"], res["amount"], data["token_id"])

        # --- CAIXA 03: SENTIMENTO ---
        elif name == "CAIXA_03_SENT":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            if random.random() > 0.6: # Agressivo
                if inv < 80:
                    res = await self.core.execute_order(name, "buy", current_price * 1.001, 15.0, data["token_id"])
                    if float(cash) >= float(res["cost"]):
                        data["cash"] = float(data["cash"]) - float(res["cost"])
                        data["inventory"] = float(data["inventory"]) + float(res["amount"])
                        self.logger.info(f"[{name}] SENTIMENTO: ENTRADA")
                elif inv >= 15:
                    res = await self.core.execute_order(name, "sell", current_price * 1.007, 15.0, data["token_id"])
                    data["cash"] = float(data["cash"]) + float(res["cost"])
                    data["inventory"] = float(data["inventory"]) - float(res["amount"])
                    self.logger.info(f"[{name}] SENTIMENTO: LUCRO")

        # --- CAIXA 04: SNIPER ---
        elif name == "CAIXA_04_SNI":
            current_price = await self.core.get_real_price(data["token_id"])
            if current_price < 0.10: # Contratos baratos
                qty = 50.0
                cost = current_price * qty * 1.001
                if data["cash"] >= cost:
                    res = await self.core.execute_order(name, "buy", current_price, qty, data["token_id"])
                    if res["status"] == "FILLED":
                        data["cash"] = float(data["cash"]) - float(res["cost"])
                        data["inventory"] = float(data["inventory"]) + float(res["amount"])
                        self.logger.info(f"[{name}] 🔫 SNIPER DISPAROU!")

        # --- ATUALIZAÇÃO PATRIMONIAL ---
        inv_v = float(data["inventory"]) * current_price
        patrimonio = float(float(data["cash"]) + inv_v)
        
        # Lucro para o Sniper (10%)
        lucro = patrimonio - data["balance"]
        if lucro > 0.001 and name != "CAIXA_04_SNI":
            taxa = lucro * 0.10
            data["cash"] = float(data["cash"]) - taxa
            # Com a tipagem explícita de self.caixas, o analisador não se confunde mais
            self.caixas["CAIXA_04_SNI"]["cash"] = float(self.caixas["CAIXA_04_SNI"]["cash"]) + taxa
            patrimonio -= taxa

        data["balance"] = float(patrimonio)
        start_cap = float(data["start"])
        data["roi"] = float((patrimonio - start_cap) / start_cap if start_cap > 0 else 0)
        
        self.core.latency_metrics["compute"] = (time.time() - start_compute) * 1000

    def log_trade(self, pillar: str, type: str, cost: float, amount: float, token: str):
        """Registra uma operação no histórico de trades."""
        trade = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pillar": pillar,
            "type": type,
            "cost": float(cost),
            "amount": float(amount),
            "token": token[:10] + "..." + token[-10:]
        }
        try:
            trades = []
            if os.path.exists(self.trades_file):
                with open(self.trades_file, "r") as f:
                    trades = json.load(f)
            trades.append(trade)
            # Keep only last 50 trades
            if len(trades) > 50:
                trades = trades[-50:]
            with open(self.trades_file, "w") as f:
                json.dump(trades, f, indent=4)
        except Exception as e:
            self.logger.error(f"Erro ao logar trade: {e}")

    def save_history(self):
        """Salva o histórico de patrimônio para o gráfico."""
        total_balance = sum([v["balance"] for v in self.caixas.values()])
        point = {
            "timestamp": time.time(),
            "balance": total_balance
        }
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    history = json.load(f)
            history.append(point)
            # Keep last 500 points
            if len(history) > 500:
                history = history[-500:]
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {e}")

    async def main_loop(self):
        self.is_running = True
        self.logger.info(f"[BOOT] Jarvis {self.os_version} Inicializado com Sucesso.")
        
        while self.is_running:
            if not self.telemetry.check_system_viability(0):
                self.logger.critical("ALERTA TÉRMICO: Encerrando por segurança.")
                break
            
            tasks = [self.run_market_tick(n, d) for n, d in self.caixas.items()]
            await asyncio.gather(*tasks)
            
            # Persistência de lucro e Dashboard (Otimizado)
            t_now = int(time.time())
            
            # Dashboard a cada 1 segundo
            if t_now != self._last_dash:
                self.telemetry.export_dashboard_data(self.caixas, self.core.latency_metrics, mode="POLYMARKET-TURBO")
                self._last_dash = t_now
                
            # Salva estado a cada 60 segundos
            if t_now % 60 == 0 and t_now != self._last_save:
                self.save_state()
                self.save_history() # Salva histórico junto com o estado
                gc.collect()
                self._last_save = t_now

            # Salva histórico a cada 10 segundos também para gráficos mais fluidos
            if t_now % 10 == 0 and t_now != self._last_history_save:
                self.save_history()
                self._last_history_save = t_now

            await asyncio.sleep(TICK_RATE)

    async def stop(self):
        self.is_running = False
        await self.core.close()
        self.logger.info("Sistema encerrado.")

if __name__ == "__main__":
    jarvis = JarvisPolymarketStable()
    try:
        asyncio.run(jarvis.main_loop())
    except KeyboardInterrupt:
        asyncio.run(jarvis.stop())
