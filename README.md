# 🤖 JARVIS MISSION CONTROL v2.1-ULTIMATE

O JARVIS é um sistema avançado de trading algorítmico para o mercado Polymarket, integrando monitoramento de hardware, quatro pilares de estratégia financeira e um dashboard premium em tempo real.

## 🏗️ Arquitetura do Sistema

### 1. Core Operacional (`polymarket_master.py`)
O cérebro principal que gerencia 4 caixas estratégicas:
- **CAIXA 01 (ARB):** Arbitragem entre YES/NO buscando distorções de soma < 1.0.
- **CAIXA 02 (MM):** Market Making com ordens de bid/ask dinâmicas baseadas no estoque.
- **CAIXA 03 (SENT):** Sentiment Analysis (Simulado) agindo em tendências de mercado.
- **CAIXA 04 (SNI):** Sniper focado em contratos de baixo custo (< $0.10).

### 2. Infraestrutura de Apoio
- **`polymarket_async_core.py`:** Interface assíncrona com o CLOB da Polymarket.
- **`hardware_engine.py`:** Telemetria de CPU/GPU para garantir segurança térmica.
- **`daily_health_check.py`:** Exportação de dados para o dashboard e verificações de segurança.

### 3. Interface Visual (`DASHBOARD_PREMIUM.py`)
Dashboard Streamlit de alto impacto com:
- Monitoramento de Hardware.
- Performance financeira por caixa (ROI e Balance).
- Gráfico de Evolução Patrimonial.
- Feed de Trades em Tempo Real.

## 🚀 Como Executar

1. **Inicie o Bot Principal:**
   ```bash
   python polymarket_master.py
   ```

2. **Inicie o Dashboard:**
   ```bash
   streamlit run DASHBOARD_PREMIUM.py
   ```

3. **Verifique os Logs:**
   Os logs detalhados ficam em `jarvis_stable.log`.

## 📈 Histórico de Atividade
- `jarvis_state.json`: Estado atual dos fundos e estoque.
- `trades_history.json`: Log das últimas 50 operações.
- `wealth_history.json`: Histórico temporal do patrimônio para gráficos.

---
*Developed by DeepMind Advanced Agentic Coding Team*
