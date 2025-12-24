import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Scout DNA | DATALIG", page_icon="🧬", layout="wide")

# --- ORTAK TASARIM (CSS) ---
# app.py'deki tasarımın aynısı, bütünlük bozulmasın diye.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root { --primary: #00e5ff; --bg: #0b0f19; }
    .stApp { background-color: var(--bg); background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 40px 40px; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: white !important; font-family: 'Inter', sans-serif; }
    .metric-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px); }
    .neon-text { color: var(--primary); font-family: 'JetBrains Mono'; text-shadow: 0 0 10px rgba(0, 229, 255, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown('<div style="font-size: 40px;">🧬</div>', unsafe_allow_html=True)
with col2:
    st.title("SCOUT DNA PROFILER")
    st.caption("Oyuncu Karakteristiği ve Veri Analizi")

st.markdown("---")

# --- OYUNCU SEÇİMİ ---
col_search, col_filter = st.columns([3, 1])
with col_search:
    player = st.selectbox("Oyuncu Ara", ["Kevin De Bruyne", "Luka Modric", "Declan Rice", "Ferdi Kadıoğlu"])
with col_filter:
    season = st.selectbox("Sezon", ["2024-2025", "2023-2024"])

# --- ANA PROFİL (Scout DNA HTML'inden esinlenildi) ---
col_profile, col_radar = st.columns([1, 2])

with col_profile:
    # Oyuncu Kartı Tasarımı
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="width: 80px; height: 80px; background: #334155; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px;">👤</div>
            <div style="background: rgba(0,229,255,0.1); color: #00e5ff; padding: 5px 10px; border-radius: 5px; font-family: 'JetBrains Mono'; font-weight: bold;">8.9</div>
        </div>
        <h2 style="margin-top: 15px;">{player}</h2>
        <p style="color: #94a3b8; font-size: 14px;">Manchester City • CM / CAM</p>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px; color: #cbd5e1;">
            <div>AGE: <span style="color: white;">32</span></div>
            <div>FOOT: <span style="color: white;">Right</span></div>
            <div>HEIGHT: <span style="color: white;">1.81m</span></div>
            <div>VALUE: <span style="color: #00e5ff;">€60M</span></div>
        </div>
    </div>
    <br>
    <div class="metric-card">
        <h4 style="color: #94a3b8; font-size: 12px; margin-bottom: 10px;">KEY METRICS (per 90)</h4>
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: white;">
                <span>xA (Expected Assists)</span>
                <span class="neon-text">0.52</span>
            </div>
            <div style="width: 100%; height: 4px; background: #334155; border-radius: 2px; margin-top: 5px;">
                <div style="width: 95%; height: 100%; background: #00e5ff; border-radius: 2px; box-shadow: 0 0 10px #00e5ff;"></div>
            </div>
        </div>
         <div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: white;">
                <span>Progressive Passes</span>
                <span class="neon-text">9.4</span>
            </div>
            <div style="width: 100%; height: 4px; background: #334155; border-radius: 2px; margin-top: 5px;">
                <div style="width: 88%; height: 100%; background: #00e5ff; border-radius: 2px;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_radar:
    # RADAR GRAFİĞİ (Plotly ile interaktif)
    categories = ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Defending', 'Physical']
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[74, 86, 93, 87, 64, 74],
        theta=categories,
        fill='toself',
        name=player,
        line_color='#00e5ff',
        fillcolor='rgba(0, 229, 255, 0.2)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(tickfont=dict(size=12, color="white"), linecolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="JetBrains Mono"),
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- İSTATİSTİK GRID ---
st.markdown("### 📊 SEASON PERFORMANCE")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Matches", "24", "+2")
m2.metric("Goals", "6", "Top 5%")
m3.metric("Assists", "14", "Top 1%")
m4.metric("Rating", "8.9", "+0.3")
