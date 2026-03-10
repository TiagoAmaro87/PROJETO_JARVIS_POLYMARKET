import os
import time
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# SDK Oficial do Polymarket
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    from py_clob_client.models import OrderArgs
except ImportError:
    ClobClient = None

# Aceleração por GPU (GTX 1660) via PyTorch (estável)
try:
    import torch
    HAS_GPU = torch.cuda.is_available()
    DEVICE = torch.device("cuda" if HAS_GPU else "cpu")
except ImportError:
    HAS_GPU = False
    DEVICE = "cpu"

load_dotenv()

class PolymarketCore:
    """
    JARVIS_POLYMARKET Core - Sistema de Execução e Estratégia.
    """
    def __init__(self):
        self.logger = self.setup_logger()
        self.api_key = os.getenv("POLYMARKET_API_KEY")
        self.api_secret = os.getenv("POLYMARKET_API_SECRET")
        self.passphrase = os.getenv("POLYMARKET_API_PASSPHRASE")
        self.private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
        
        self.has_gpu = HAS_GPU
        if self.has_gpu:
            self.logger.info(f"GPU {torch.cuda.get_device_name(0)} pronta para Otimização Convexa.")
        
        if ClobClient and self.private_key:
            self.client = ClobClient(
                host="https://clob.polymarket.com",
                key=self.private_key,
                chain_id=POLYGON,
                signature_type=1 # EOA
            )
            self.logger.info("Conectado à CLOB API do Polymarket.")
        else:
            self.client = None
            self.logger.warning("Client não inicializado. Verifique as chaves no arquivo .env")

    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - JARVIS - %(levelname)s - %(message)s'
        )
        return logging.getLogger("JarvisCore")

    def gpu_correlation_matrix(self, data_tensor: torch.Tensor):
        """
        Mapeia correlações entre múltiplos mercados instantaneamente via GPU.
        """
        if not self.has_gpu:
            return torch.corrcoef(data_tensor)
        
        data_tensor = data_tensor.to(DEVICE)
        return torch.corrcoef(data_tensor)

    def scan_zero_sum_arbitrage(self, markets: List[Dict]):
        """
        Arbitragem de Soma Zero: YES + NO < 1.00
        """
        for m in markets:
            total = m['yes_price'] + m['no_price']
            if total < 0.995:
                self.logger.warning(f"Arbitragem Detectada: {m['name']} | Soma: {total}")
                self.execute_arbitrage(m)

    def stoikov_market_making(self, mid_price: float, vol: float, time_left: float, inventory: int):
        """
        Modelo de Stoikov adaptado para Polymarket.
        Ajusta spread bid-ask com base no risco de inventário.
        """
        gamma = 0.1 # Aversão ao risco
        k = 1.5 # Liquidez do mercado
        
        # Preço de reserva
        reservation_price = mid_price - (inventory * gamma * (vol**2) * time_left)
        
        # Spread ótimo
        spread = (gamma * (vol**2) * time_left) + (2/gamma) * torch.log(torch.tensor(1 + gamma/k))
        
        bid = reservation_price - (spread / 2)
        ask = reservation_price + (spread / 2)
        
        return float(bid), float(ask)

    def apply_kelly_criterion(self, win_prob: float, odds: float):
        """
        Kelly Criterion Dinâmico. p: prob de vitória, b: odds decimais (ex: 2.0 para 50/50).
        """
        b = odds - 1
        if b <= 0: return 0.0
        
        f = (win_prob * (b + 1) - 1) / b
        return float(torch.clamp(torch.tensor(f * 0.05), 0.0, 0.05)) # Limitado a 5%

    def execute_arbitrage(self, market: Dict):
        self.logger.info(f"Executando Arbitragem em {market['name']}")
        # Ordem casada YES/NO

# Inicialização e Teste
if __name__ == "__main__":
    core = PolymarketCore()
    
    # Teste Stoikov
    bid, ask = core.stoikov_market_making(0.5, 0.02, 100, 5)
    core.logger.info(f"Stoikov MM -> Bid: {bid:.4f}, Ask: {ask:.4f}")
    
    # Teste Kelly
    size = core.apply_kelly_criterion(0.6, 2.0) # 60% prob, 2.0 odds
    core.logger.info(f"Kelly Risk Manager -> Size: {size:.2%}")
