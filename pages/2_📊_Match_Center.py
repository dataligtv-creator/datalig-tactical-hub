import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Match Center | DATALIG", page_icon="📊", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root { --primary: #00e5ff; --alert: #ef4444; --bg: #0b0f19; }
    .stApp { background-color: var(--bg); background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 40px 40px; }
    .scoreboard { background: linear-gradient(180deg, rgba(15,23,42,0.8) 0%, rgba(15,23,42,0.95) 100%); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; text-align: center; color: white; margin-bottom: 20px; }
    .score { font-size: 60px; font-weight: 700; font-family: 'JetBrains Mono'; letter-spacing: -2px; }
    .team-name { font-size: 24px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .live-badge { background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid rgba(239, 68, 68, 0.4); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# --- SKORBORD ---
st.markdown("""
<div class="scoreboard">
    <span class="live-badge">● LIVE 74:12</span>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
        <div style="flex: 1;">
            <div class="team-name">Man City</div>
            <div style="color: #94a3b8; font-size: 14px;">(2.34 xG)</div>
        </div>
        <div class="score">2 - 1</div>
        <div style="flex: 1;">
            <div class="team-name">Liverpool</div>
            <div style="color: #94a3b8; font-size: 14px;">(0.98 xG)</div>
        </div>
    </div>
    <div style="margin-top: 15px; width: 100%; height: 6px; background: #334155; border-radius: 3px; overflow: hidden;">
        <div style="width: 62%; height: 100%; background: #00e5ff; float: left;"></div>
        <div style="width: 38%; height: 100%; background: #ef4444; float: right;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; margin-top: 5px; font-family: 'JetBrains Mono';">
        <span>POSSESSION: 62%</span>
        <span>38%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- MOMENTUM VE İSTATİSTİKLER ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Momentum Swing")
    # Rastgele momentum verisi üretelim
    chart_data = pd.DataFrame(np.random.randn(90, 1), columns=["Momentum"]).cumsum()
    st.area_chart(chart_data, color="#00e5ff", height=250)
    
    st.markdown("### 🔑 Key Events")
    st.markdown("""
    - **72'** ⚽ **GOAL!** Phil Foden (Assist: K. De Bruyne)
    - **45'** 🟨 Yellow Card - Rodri
    - **12'** ⚽ **GOAL!** Erling Haaland
    """)

with col2:
    st.subheader("📊 Match Stats")
    
    stats = {
        "Shots": ("14", "8"),
        "On Target": ("6", "3"),
        "Passes": ("542", "312"),
        "Pass Accuracy": ("89%", "81%"),
        "Corners": ("8", "2")
    }
    
    for stat, values in stats.items():
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px;">
            <span style="color: #00e5ff; font-weight: bold;">{values[0]}</span>
            <span style="color: #94a3b8; font-size: 14px;">{stat}</span>
            <span style="color: #ef4444; font-weight: bold;">{values[1]}</span>
        </div>
        """, unsafe_allow_html=True)
