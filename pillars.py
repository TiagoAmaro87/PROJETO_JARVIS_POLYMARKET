import logging
import re
from typing import Dict, List
import numpy as np

class TradingPillars:
    def __init__(self, brain):
        self.brain = brain
        self.logger = logging.getLogger("JarvisPillars")

    def pillar_01_arbitrage(self, books_matrix: List[List[float]]):
        if not books_matrix: return []
        np_books = np.array(books_matrix)
        inefficiency = np.sum(np_books, axis=1) - 1.0
        return np.where(inefficiency < -0.01)[0].tolist()

    def pillar_02_market_making(self, market_id: str, inventory: float):
        return {"bid": 0.50 - (inventory * 0.01), "ask": 0.52 + (inventory * 0.01)}

    def pillar_03_sentiment_nlp(self, headline: str):
        score = 0.5
        pos = ["victory", "win", "surge", "success"]
        neg = ["defeat", "loss", "crash", "failure"]
        for k in pos:
            if re.search(k, headline, re.IGNORECASE): score += 0.1
        for k in neg:
            if re.search(k, headline, re.IGNORECASE): score -= 0.1
        return min(max(score, 0.0), 1.0)
