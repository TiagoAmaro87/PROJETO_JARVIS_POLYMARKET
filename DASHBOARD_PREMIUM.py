import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# Configuração da página - Dark Mode Premium
st.set_page_config(
    page_title="JARVIS MISSION CONTROL",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para visual "Gamer/Premium"
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #161B22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363D;
    }
    .status-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #1e1e2f 0%, #0d0d1a 100%);
        border: 1px solid #3d3d5c;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
    }
    .p-lucro {
        color: #3fb950;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh a cada 2 segundos
st_autorefresh(interval=2000, key="datarefresh")

def load_data():
    if os.path.exists("live_status.json"):
        with open("live_status.json", "r") as f:
            return json.load(f)
    return None

data = load_data()

# Processamento de Dados Global
finance = {}
active_opps = {}
hw = {}

if data:
    hw = data.get("hardware", {})
    payload = data.get("finance", {})
    # Suporte legado e nova estrutura
    if isinstance(payload, dict) and "finance" in payload and "active_opportunities" in payload:
        finance = payload.get("finance", {})
        active_opps = payload.get("active_opportunities", {})
    else:
        finance = payload

# Abas do Dashboard
tab_control, tab_active, tab_markets = st.tabs(["🚀 Mission Control", "⚡ Active Trades", "🔭 Market Explorer"])

with tab_control:
    if data:
        # --- HEADER METRICS ---
        try:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Cálculo seguro do balanço
            caixas_list = [v for v in finance.values() if isinstance(v, dict) and "balance" in v]
            total_balance = sum([v["balance"] for v in caixas_list])
            total_start = sum([v["start"] for v in caixas_list])
            total_roi = (total_balance / total_start - 1) * 100 if total_start > 0 else 0
            
            col1.metric("🌍 TOTAL PATRIMÔNIO", f"${total_balance:,.2f}", f"{total_roi:.2f}%")
            col2.metric("🌡️ GPU TEMP", f"{hw.get('gpu_temp', 0)}°C", delta_color="inverse")
            col3.metric("🧠 CPU LOAD", f"{hw.get('cpu_load', 0)}%", delta_color="inverse")
            col4.metric("📊 RAM USED", f"{hw.get('ram_used', 0)}%")
            col5.metric("📡 STATUS", data.get("status", "STANDBY"), delta="LIVE")
        except Exception as e:
            st.error(f"Erro ao processar métricas: {e}")
            finance = {} # Previne erros nos loops abaixo

        st.markdown("### 🏦 Gestão das Caixas (Polymarket Turbo)")
    
    # --- FINANCIAL GRID ---
    caixas_cols = st.columns(4)
    
    for i, (name, d) in enumerate(finance.items()):
        with caixas_cols[i]:
            roi_val = d['roi'] * 100
            st.markdown(f"""
            <div class='status-card'>
                <h3 style='margin-top:0;'>{name}</h3>
                <p>Cash: <span style='color:white'>${d['cash']:.2f}</span></p>
                <p>Inv: <span style='color:white'>${d['inventory'] * 0.5:.2f}</span></p>
                <p style='font-size:1.2em'>ROI: <span style='color:{"#3fb950" if roi_val >= 0 else "#f85149"}'>{roi_val:.2f}%</span></p>
            </div>
            """, unsafe_allow_html=True)

    # --- CHARTS ---
    st.markdown("---")
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.markdown("#### 📈 Distribuição de Capital")
        df_finance = pd.DataFrame([
            {"Caixa": k, "Investido": v["inventory"] * 0.5, "Cash": v["cash"]}
            for k, v in finance.items()
        ])
        fig = px.bar(df_finance, x="Caixa", y=["Investido", "Cash"], 
                     title="Alocação por Estratégia",
                     color_discrete_sequence=["#58a6ff", "#3fb950"],
                     template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # --- WEALTH HISTORY CHART ---
    st.markdown("---")
    st.markdown("#### 📈 Evolução do Patrimônio Total ($)")
    if os.path.exists("wealth_history.json"):
        with open("wealth_history.json", "r") as f:
            hist_data = json.load(f)
            if hist_data:
                df_hist = pd.DataFrame(hist_data)
                df_hist['time'] = pd.to_datetime(df_hist['timestamp'], unit='s')
                fig_hist = px.line(df_hist, x='time', y='balance', 
                                  line_shape='spline',
                                  color_discrete_sequence=["#58a6ff"],
                                  template="plotly_dark")
                fig_hist.update_layout(xaxis_title="", yaxis_title="Balance")
                st.plotly_chart(fig_hist, use_container_width=True)

    with c_right:
        st.markdown("#### ⚡ Latência do Sistema")
        latency = data.get("latency", {})
        fig_lat = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = latency.get("compute", 0),
            title = {'text': "Compute (ms)"},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "#58a6ff"},
                     'steps' : [
                         {'range': [0, 20], 'color': "green"},
                         {'range': [20, 50], 'color': "yellow"},
                         {'range': [50, 100], 'color': "red"}]}))
        fig_lat.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_lat, use_container_width=True)

    # --- TRADES AND LOGS ---
    st.markdown("---")
    l_col, r_col = st.columns(2)
    
    with l_col:
        st.markdown("#### 🛰️ Feed de Operações Recentes")
        if os.path.exists("trades_history.json"):
            with open("trades_history.json", "r") as f:
                trades = json.load(f)
                if trades:
                    df_trades = pd.DataFrame(trades).iloc[::-1] # Reverse for most recent first
                    st.dataframe(df_trades, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma operação registrada ainda.")
        else:
            st.info("Arquivo de trades não encontrado.")

    with r_col:
        st.markdown("#### 📝 Console Output (Last 10)")
        if os.path.exists("jarvis_stable.log"):
            with open("jarvis_stable.log", "r") as f:
                lines = f.readlines()
                # Clean up lines for better display
                clean_lines = [l.strip() for l in lines[-10:] if l.strip()]
                st.code("\n".join(clean_lines), language="log")



with tab_active:
    st.markdown("### ⚡ Oportunidades Ativas")
    st.info("Monitoramento detalhado de mercados do Explorer que dispararam execução.")
    
    if active_opps:
        opp_cols = st.columns(3)
        for i, (name, d) in enumerate(active_opps.items()):
            with opp_cols[i % 3]:
                roi_val = d.get('roi', 0) * 100
                st.markdown(f"""
                <div class='status-card' style='border-color: #58a6ff;'>
                    <h3 style='margin-top:0;'>🔥 {name}</h3>
                    <p>Cash Alocado: <span style='color:white'>${d.get('cash', 0):.2f}</span></p>
                    <p>Contratos: <span style='color:white'>{d.get('inventory', 0):.1f}</span></p>
                    <p style='font-size:1.2em'>ROI: <span style='color:{"#3fb950" if roi_val >= 0 else "#f85149"}'>{roi_val:.2f}%</span></p>
                    <small>Estratégia: {d.get('strategy', 'N/A')}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("---")
        st.empty()
        col_msg = st.columns([1, 2, 1])[1]
        col_msg.warning("Nenhuma oportunidade do Explorer está em fase de execução ativa no momento.")
        col_msg.info("O JARVIS continuará escaneando mercados na aba telescópio (Explorer).")

with tab_markets:
    st.markdown("### 🔭 Market Explorer")
    st.info("Esta aba monitora mercados em tempo real sem afetar o capital das caixas principais.")
    
    explorer_prices = payload.get("explorer_prices", {})
    
    # --- GLOBAL DISCOVERY SECTION ---
    st.write("#### 🌍 Global Discovery Scanner (Trending)")
    discovered_list = [t for t in payload.get("explorer_prices", {}).keys() if "GLOBAL_" in t][:21] # Limite para performance
    
    if discovered_list:
        with st.container(height=400):
            g_cols = st.columns(3)
            # Extrair os targets reais pelo nome (precisamos do dicionário original se possível, 
            # mas vamos simplificar usando o ID por enquanto)
            for j, g_id in enumerate(discovered_list):
                if "_yes" not in g_id: continue
                clean_id = g_id.replace("_yes", "")
                with g_cols[j % 3]:
                    price = explorer_prices.get(g_id, 0)
                    st.markdown(f"""
                    <div style='background:#161b22; padding:10px; border-radius:5px; border:1px solid #30363d; margin-bottom:10px;'>
                        <p style='font-size:0.8em; color:#8b949e; margin:0;'>ID: {clean_id}</p>
                        <p style='font-weight:bold; margin:0;'>PREÇO: ${price:.3f}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Scanner aguardando próxima rodada de descoberta global...")

    st.write("---")
    if os.path.exists("targets.json"):
        with open("targets.json", "r") as f:
            targets_data = json.load(f)
            st.write("#### 📡 Alvos VIP (targets.json):")
            
            ex_cols = st.columns(2)
            # Filtra apenas os manuais (não globais)
            manual_targets = [t for t in targets_data.get("targets", [])]
            for i, t in enumerate(manual_targets):
                with ex_cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"**📍 {t['name']}**")
                        
                        y_p = explorer_prices.get(f"{t['id']}_yes", 0.5)
                        n_p = explorer_prices.get(f"{t['id']}_no", 0)
                        
                        p_col1, p_col2 = st.columns(2)
                        p_col1.metric("YES", f"${y_p:.3f}")
                        if n_p > 0:
                            p_col2.metric("NO", f"${n_p:.3f}")
                        
                        st.caption(f"Estratégia: {t['strategy'].upper()} | Gatilho: < {t['threshold']}")
                        if t['strategy'] == "sniper":
                            prog = min(1.0, t['threshold'] / y_p) if y_p > 0 else 0
                            st.progress(prog, text=f"Proximidade: {prog*100:.1f}%")
    else:
        st.warning("Arquivo targets.json não encontrado.")

st.markdown(f"""
    <div style='text-align: center; color: #8b949e; padding: 20px;'>
        JARVIS v2.1-ULTIMATE | Host: WSL Ubuntu 24.04 | Last Update: {datetime.now().strftime('%H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
