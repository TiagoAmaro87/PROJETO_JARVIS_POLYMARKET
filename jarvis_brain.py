import sqlite3
import logging
from typing import Dict

class JarvisBrain:
    def __init__(self, db_path: str = "jarvis_brain.db"):
        self.logger = logging.getLogger("JarvisBrain")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    pillar TEXT,
                    side TEXT,
                    price REAL,
                    amount REAL,
                    status TEXT
                )
            """)
            
    def log_trade(self, trade_data: Dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO trades (timestamp, pillar, side, price, amount, status)
                    VALUES (:timestamp, :pillar, :side, :price, :amount, :status)
                """, trade_data)
        except Exception as e:
            self.logger.error(f"Erro ao logar trade: {e}")
