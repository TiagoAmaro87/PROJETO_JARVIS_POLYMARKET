import asyncio
import aiohttp
import time
import logging
import json
from typing import Dict, List

class PolymarketAsyncCore:
    def __init__(self, paper_trading: bool = True):
        self.latency_metrics = {"network": 0.0, "compute": 0.0, "execution": 0.0}
        self.logger = logging.getLogger("JarvisAsync")
        self.paper_trading = paper_trading
        self.fee_rate = 0.001
        self.clob_url = "https://clob.polymarket.com"
        self._session = None
        
        # --- Simulação de Realidade Cruel ---
        self.polygon_gas_price = 0.051  # Custo médio em USDC por transação na Polygon (variável)
        self.log_gas_fees = True
        
        # Mapping de Tokens Reais para Simulação
        self.active_tokens = {
            "CAIXA_01_ARB": "110251828161543119357013227499774714771527179764174739487025581227481937033858",
            "CAIXA_02_MM": "65176388692130651396848427090788038285140833850265294793449655516920659740141"
        }

    async def get_session(self) -> aiohttp.ClientSession:
        session = self._session
        if session is None or session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_active_markets(self):
        """Busca mercados em destaque/ativos para o scanner global."""
        url = "https://clob.polymarket.com/markets"
        try:
            curr_session = await self.get_session()
            async with curr_session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
        except Exception as e:
            self.logger.error(f"Erro ao buscar mercados ativos: {e}")
            return []

    async def get_real_price(self, token_id: str):
        """Busca o preço médio real (midpoint) do CLOB do Polymarket."""
        start_time = time.time()
        url = f"{self.clob_url}/midpoint?token_id={token_id}"
        try:
            curr_session = await self.get_session()
            async with curr_session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.latency_metrics["network"] = (time.time() - start_time) * 1000
                    return float(data.get("mid", 0.5))
                return 0.5
        except Exception as e:
            self.logger.debug(f"Erro ao buscar preço: {e}")
            return 0.5

    async def get_orderbook(self, token_id: str):
        """Busca o livro de ofertas real do Polymarket."""
        url = f"{self.clob_url}/book?token_id={token_id}"
        try:
            curr_session = await self.get_session()
            async with curr_session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"bids": [], "asks": []}
        except Exception as e:
            self.logger.debug(f"Erro ao buscar orderbook: {e}")
            return {"bids": [], "asks": []}

    async def execute_order(self, pillar: str, side: str, price: float, amount: float, token_id: str):
        """Simula execução baseada no preço real do Polymarket."""
        start_exec = time.time()
        
        # Simula delay de execução real
        await asyncio.sleep(0.05) 
        
        # Preço final com slippage e taxas
        slippage = 1.001 if side == "buy" else 0.999
        sim_price = price * slippage
        
        # Custo total incluindo taxas de exchange e GAS da rede Polygon
        gas_impact = self.polygon_gas_price if not self.paper_trading else self.polygon_gas_price * 0.8 # Simula mesmo no paper
        
        if side == "buy":
            total_cost = (sim_price * amount) * (1 + self.fee_rate) + gas_impact
        else:
            total_cost = (sim_price * amount) * (1 - self.fee_rate) - gas_impact
            
        if self.log_gas_fees:
            self.logger.info(f"[GAS] Operação {side.upper()} consumiu ${gas_impact:.4f} em taxas de rede.")

        self.latency_metrics["execution"] = (time.time() - start_exec) * 1000
        
        return {
            "status": "FILLED",
            "price": sim_price,
            "amount": amount,
            "cost": total_cost,
            "timestamp": time.time(),
            "pillar": pillar,
            "token_id": token_id
        }

    async def close(self):
        s = self._session
        if s is not None:
            if not s.closed:
                await s.close()
