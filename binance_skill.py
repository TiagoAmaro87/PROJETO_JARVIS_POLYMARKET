import logging
import aiohttp
import asyncio
from typing import Dict, List

class BinanceSniper:
    def __init__(self):
        self.logger = logging.getLogger("JarvisSniper")
        self.base_url = "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money"
        self.headers = {
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": "binance-web3/1.0 (Skill)"
        }

    async def get_smart_money_signals(self, chain_id: str = "CT_501"): # Default Solana
        """
        Busca sinais de Smart Money on-chain via API Web3 da Binance.
        """
        payload = {
            "smartSignalType": "",
            "page": 1,
            "pageSize": 10,
            "chainId": chain_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=self.headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Debug structure
                        # print(f"[DEBUG] Binance Data: {data}") 
                        
                        # Estrutura esperada: {"data": {"list": [...]}} ou as vezes direto
                        if isinstance(data.get("data"), dict):
                            return data.get("data", {}).get("list", [])
                        return data.get("data", []) # Caso seja lista direta
                    else:
                        self.logger.error(f"Erro Binance API: {resp.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Falha na Sniper Skill: {e}")
            return []

    def analyze_signal(self, signal: Dict):
        """
        Filtra apenas sinais de alta convicção (Multi-Smart Money Buying).
        """
        # Exemplo de lógica de filtragem simples
        is_buy = signal.get("signalType") == 1 # 1 = Buy (supondo baseado no link do repo)
        price_gain = float(signal.get("maxGain", 0))
        
        if is_buy and price_gain > 50: # Sinais com potencial histórico > 50%
            return True
        return False
