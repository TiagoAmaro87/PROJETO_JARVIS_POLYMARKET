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

        # Gestão de Oportunidades (Explorer -> Active Trades)
        self.active_opportunities: Dict[str, Any] = {}
        self.explorer_targets: List[Dict] = []
        self.load_explorer_targets()

        self.load_state() 
        self.is_running = False
        self._last_save = 0
        self._last_dash = 0
        self._last_history_save = 0
        self.trades_file = "trades_history.json"
        self.history_file = "wealth_history.json"
        self._last_discovery = 0
        self.discovered_targets: List[Dict] = []
        self.explorer_prices: Dict[str, float] = {}
        
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

    def load_explorer_targets(self):
        """Carrega os alvos do Explorer do arquivo targets.json."""
        if os.path.exists("targets.json"):
            try:
                with open("targets.json", "r") as f:
                    data = json.load(f)
                    self.explorer_targets = data.get("targets", [])
                self.logger.info(f"[EXPLORER] {len(self.explorer_targets)} alvos carregados para monitoramento.")
            except Exception as e:
                self.logger.error(f"[EXPLORER] Erro ao carregar targets: {e}")

    async def run_global_discovery(self):
        """Busca mercados de alto volume (Whales) e distorções via Gamma API."""
        t_now = time.time()
        if t_now - self._last_discovery < 600: # A cada 10 minutos
            return
            
        self.logger.info("[WHALE] Rastreando Smart Money e fluxo de grandes apostas...")
        trending = await self.core.get_trending_events()
        
        new_targets = []
        for event in trending:
            # Pegamos o mercado principal de cada evento tendendo
            markets = event.get("markets", [])
            if not markets: continue
            
            m = markets[0]
            m_id = m.get("conditionId")
            if not m_id: continue

            # Determina o token YES (geralmente o primeiro da lista)
            tokens = m.get("clobTokenIds", [])
            if len(tokens) < 2: 
                # Tenta formatar se for string única
                y_id = m.get("clobTokenIds") 
                if not isinstance(y_id, list): continue
            else:
                y_id, n_id = tokens[0], tokens[1]

            new_targets.append({
                "id": f"WHALE_{m_id[:8]}",
                "name": m.get("question", event.get("title")),
                "token_ids": {"yes": y_id, "no": n_id},
                "strategy": "sniper",
                "threshold": 0.15, # Gateway para o modo Global Hunter
                "max_investment": 20.0,
                "is_whale": True
            })
        
        self.discovered_targets = new_targets
        self._last_discovery = t_now
        self.logger.info(f"[WHALE] Scanner de Smart Money identificou {len(new_targets)} mercados de alto impacto.")

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

        # --- CAIXA 01: ARBITRAGEM (COMPLETAMENTE DESATIVADA) ---
        if name == "CAIXA_01_ARB":
            self.logger.warning(f"[{name}] BLOQUEADA POR ORDEM DO USUÁRIO.")
            return 

        # --- CAIXA 02: MARKET MAKING ---
        elif name == "CAIXA_02_MM":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            qty = 100.0 # Aumentado para diluir GAS (Mão de $50-$100)

            if inv < 200:
                buy_p = current_price * 0.998
                # Simulação de viabilidade: spread deve ser > GAS
                if (current_price - buy_p) * qty > (self.core.polygon_gas_price * 1.2):
                    res = await self.core.execute_order(name, "buy", buy_p, qty, data["token_id"])
                    if float(cash) >= float(res["cost"]):
                        data["cash"] = float(data["cash"]) - float(res["cost"])
                        data["inventory"] = float(data["inventory"]) + float(res["amount"])
                        self.logger.info(f"[{name}] MM COMPRA EFICIENTE (Vol: {qty})")
            elif inv >= qty:
                sell_p = current_price * 1.012
                if (sell_p - current_price) * qty > (self.core.polygon_gas_price * 2):
                    res = await self.core.execute_order(name, "sell", sell_p, qty, data["token_id"])
                    data["cash"] = float(data["cash"]) + float(res["cost"])
                    data["inventory"] = float(data["inventory"]) - float(res["amount"])
                    self.logger.info(f"[{name}] MM VENDA EFICIENTE (Lucro Real)")
                    self.log_trade(name, "SELL_MM", res["cost"], res["amount"], data["token_id"])

        # --- CAIXA 03: SENTIMENTO ---
        elif name == "CAIXA_03_SENT":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            qty = 100.0 # Aumentado para eficiência de Gás

            if random.random() > 0.4: # Mais agressivo para testes
                if inv < 300:
                    # Só entra se a tendência for forte e compensar o Gás
                    profit_potential = (current_price * 0.005) * qty
                    if profit_potential > (self.core.polygon_gas_price * 1.1):
                        res = await self.core.execute_order(name, "buy", current_price * 1.001, qty, data["token_id"])
                        if float(cash) >= float(res["cost"]):
                            data["cash"] = float(data["cash"]) - float(res["cost"])
                            data["inventory"] = float(data["inventory"]) + float(res["amount"])
                            self.logger.info(f"[{name}] SENTIMENTO: ENTRADA EXECUTADA")
                    else:
                        self.logger.info(f"[{name}] Trade ignorado: Lucro est. ${profit_potential:.3f} < Gás")
                elif inv >= qty:
                    res = await self.core.execute_order(name, "sell", current_price * 1.007, qty, data["token_id"])
                    data["cash"] = float(data["cash"]) + float(res["cost"])
                    data["inventory"] = float(data["inventory"]) - float(res["amount"])
                    self.logger.info(f"[{name}] SENTIMENTO: LUCRO REAL")

        # --- CAIXA 04: SAFE GRINDER (FAVORITOS 95%+) ---
        elif name == "CAIXA_04_SNI":
            current_price = await self.core.get_real_price(data["token_id"])
            inv, cash = data["inventory"], data["cash"]
            
            # Grinding de baixo risco: Compra a 0.96 para vender a 0.98+
            if current_price >= 0.95 and current_price < 0.97:
                qty = 100.0 # Volume alto para compensar margem pequena
                if cash >= (current_price * qty):
                    res = await self.core.execute_order(name, "buy", current_price, qty, data["token_id"])
                    data["cash"] = float(data["cash"]) - float(res["cost"])
                    data["inventory"] = float(data["inventory"]) + float(res["amount"])
                    self.logger.info(f"[{name}] SAFE GRIND: Compra em favorito 95%+")
            elif current_price >= 0.985 and inv > 0:
                res = await self.core.execute_order(name, "sell", current_price, inv, data["token_id"])
                data["cash"] = float(data["cash"]) + float(res["cost"])
                data["inventory"] = 0.0
                self.logger.info(f"[{name}] SAFE GRIND: Lucro realizado (Grinding)")

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

    async def process_explorer_target(self, target: Dict):
        """Processa um único alvo do explorer de forma assíncrona."""
        t_id = target["id"]
        y_token = target["token_ids"].get("yes")
        if not y_token: return

        try:
            y_p = await self.core.get_real_price(y_token)
            self.explorer_prices[f"{t_id}_yes"] = y_p

            if t_id in self.active_opportunities:
                opp = self.active_opportunities[t_id]
                opp["balance"] = opp["cash"] + (opp["inventory"] * y_p)
                opp["roi"] = (opp["balance"] - opp["start"]) / opp["start"] if opp["start"] > 0 else 0
                return

            # --- ESTRATÉGIA: GLOBAL HUNTER (AGRESSIVA) ---
            # 1. Extreme Sniper: Preço baixo com potencial de valorização
            if y_p <= 0.40 and y_p > 0.01: 
                qty = 10.0 / y_p 
                res = await self.core.execute_order(f"OPP_{t_id}", "buy", y_p, qty, y_token)
                self.active_opportunities[t_id] = {
                    "name": f"HUNT: {target['name'][:30]}...", 
                    "cash": 0.0, "inventory": qty, "start": res["cost"], 
                    "balance": res["cost"], "roi": 0.0, "strategy": "Hunter Sniper"
                }
                self.logger.info(f"[HUNT] Oportunidade Detectada ($10): {target['name']} a ${y_p:.3f}")
                return

            # 2. Contrarian: Preço alto, aposta na queda
            n_token = target["token_ids"].get("no")
            if y_p >= 0.85 and n_token:
                n_p = 1.0 - y_p
                if n_p > 0.01:
                    qty = 10.0 / n_p
                    res = await self.core.execute_order(f"OPP_{t_id}", "buy", n_p, qty, n_token)
                    self.active_opportunities[t_id] = {
                        "name": f"CONTRA: {target['name'][:30]}...", 
                        "cash": 0.0, "inventory": qty, "start": res["cost"], 
                        "balance": res["cost"], "roi": 0.0, "strategy": "Global Contrarian"
                    }
                    self.logger.info(f"[HUNT] Reversao Detectada ($10): {target['name']} (YES a ${y_p:.3f})")
                    return
            
            elif target.get("strategy") == "sniper" and y_p < target.get("threshold", 0.10):
                qty = 10.0 / y_p
                res = await self.core.execute_order(f"OPP_{t_id}", "buy", y_p, qty, y_token)
                self.active_opportunities[t_id] = {
                    "name": target["name"], "cash": 0.0, "inventory": qty, 
                    "start": res["cost"], "balance": res["cost"], "roi": 0.0, "strategy": "Sniper"
                }
                self.logger.info(f"🔫 [EXPLORER] Sniper Alvo Ativado ($10): {target['name']}")
        except:
            pass

    async def run_explorer_scan(self):
        """Varre os alvos de forma paralela para não bloquear o loop principal."""
        all_targets = self.explorer_targets + self.discovered_targets
        
        # Só varre o Global Hunter a cada 3 ticks para não sobrecarregar
        if not hasattr(self, "_explorer_tick"): self._explorer_tick = 0
        self._explorer_tick += 1
        
        targets_to_scan = self.explorer_targets # VIPs sempre
        if self._explorer_tick % 5 == 0:
            targets_to_scan = all_targets # Toda a lista a cada 5 ticks
            
        tasks = [self.process_explorer_target(t) for t in targets_to_scan]
        await asyncio.gather(*tasks)

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
            
            # 1. Run Fixed Pillars
            tasks = [self.run_market_tick(n, d) for n, d in self.caixas.items()]
            await asyncio.gather(*tasks)

            # 2. Run Global Discovery (Scanner em Massa)
            await self.run_global_discovery()

            # 3. Run Explorer Scan (Oportunista)
            await self.run_explorer_scan()
            
            # Persistência de lucro e Dashboard (Otimizado)
            t_now = int(time.time())
            
            # Dashboard a cada 1 segundo
            if t_now != self._last_dash:
                payload = {
                    "finance": self.caixas,
                    "active_opportunities": self.active_opportunities,
                    "explorer_prices": self.explorer_prices,
                    "active_total": sum(opp["balance"] for opp in self.active_opportunities.values())
                }
                self.telemetry.export_dashboard_data(payload, self.core.latency_metrics, mode="POLYMARKET-TURBO")
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
