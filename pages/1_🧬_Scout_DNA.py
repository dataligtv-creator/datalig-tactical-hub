import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import PyPizza

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Scout DNA | DATALIG", page_icon="🧬", layout="wide")

# --- CSS (NEON TEMA) ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'JetBrains Mono', monospace; }
    .stSlider > div > div > div > div { background-color: #00e5ff !important; }
    .stTextInput input { color: #00e5ff !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<div style='font-size: 40px;'>🧬</div>", unsafe_allow_html=True)
with col2:
    st.title("SCOUT DNA")
    st.caption("Player Comparison & Talent ID")

st.markdown("---")

# --- OYUNCU GİRİŞ PANELİ ---
col_p1, col_center, col_p2 = st.columns([1, 0.2, 1])

with col_p1:
    st.markdown("### 🔵 OYUNCU 1")
    p1_name = st.text_input("İsim", "Mauro Icardi", key="p1_name")
    p1_team = st.text_input("Takım", "Galatasaray", key="p1_team")
    
    st.markdown("---")
    p1_stats = []
    p1_stats.append(st.slider("HIZ", 0, 99, 75, key="p1_pac"))
    p1_stats.append(st.slider("ŞUT", 0, 99, 88, key="p1_sho"))
    p1_stats.append(st.slider("PAS", 0, 99, 70, key="p1_pas"))
    p1_stats.append(st.slider("DRİBLİNG", 0, 99, 78, key="p1_dri"))
    p1_stats.append(st.slider("DEFANS", 0, 99, 35, key="p1_def"))
    p1_stats.append(st.slider("FİZİK", 0, 99, 82, key="p1_phy"))

with col_p2:
    st.markdown("### 🔴 OYUNCU 2")
    p2_name = st.text_input("İsim", "Edin Dzeko", key="p2_name")
    p2_team = st.text_input("Takım", "Fenerbahçe", key="p2_team")
    
    st.markdown("---")
    p2_stats = []
    p2_stats.append(st.slider("HIZ", 0, 99, 68, key="p2_pac"))
    p2_stats.append(st.slider("ŞUT", 0, 99, 85, key="p2_sho"))
    p2_stats.append(st.slider("PAS", 0, 99, 78, key="p2_pas"))
    p2_stats.append(st.slider("DRİBLİNG", 0, 99, 72, key="p2_dri"))
    p2_stats.append(st.slider("DEFANS", 0, 99, 45, key="p2_def"))
    p2_stats.append(st.slider("FİZİK", 0, 99, 85, key="p2_phy"))

# --- RADAR GRAFİĞİ ÇİZİMİ ---
st.markdown("---")
st.markdown("### 📊 ANALİZ RAPORU")

params = ["HIZ", "ŞUT", "PAS", "DRİBLİNG", "DEFANS", "FİZİK"]

# PyPizza Ayarları (Neon Stil)
baker = PyPizza(
    params=params,                  # Parametre isimleri
    background_color="#0b0f19",     # Arka plan rengi (Koyu)
    straight_line_color="#222222",  # Grid çizgileri
    straight_line_lw=1,             # Çizgi kalınlığı
    last_circle_lw=1,               # Dış çember kalınlığı
    other_circle_lw=1,              # İç çemberler
    other_circle_ls="-."            # Çizgi stili
)

# Grafiği Çiz
fig, ax = baker.make_pizza(
    p1_stats,                       # Oyuncu 1 verileri
    compare_values=p2_stats,        # Oyuncu 2 verileri (Karşılaştırma)
    figsize=(10, 10),               # Boyut
    color_blank_roots=None,
    slice_colors=["#00e5ff"] * 6,   # Dilim renkleri (Gerekirse değiştirilir)
    
    # Renkler ve Tasarım
    kwargs_slices=dict(
        facecolor="#00e5ff", edgecolor="#0b0f19",
        zorder=2, linewidth=1
    ),                          
    kwargs_compare=dict(
        facecolor="#ff0055", edgecolor="#0b0f19",
        zorder=2, linewidth=1
    ),
    kwargs_params=dict(
        color="#ffffff", fontsize=12,
        fontfamily="monospace", va="center"
    ),
    kwargs_values=dict(
        color="#000000", fontsize=12,
        fontfamily="monospace", zorder=3,
        bbox=dict(edgecolor="#000000", facecolor="#00e5ff", boxstyle="round,pad=0.2", lw=1)
    ),
    kwargs_compare_values=dict(
        color="#000000", fontsize=12,
        fontfamily="monospace", zorder=3,
        bbox=dict(edgecolor="#000000", facecolor="#ff0055", boxstyle="round,pad=0.2", lw=1)
    )
)

# Başlıklar
fig.text(
    0.515, 0.97, f"{p1_name} vs {p2_name}", size=20,
    ha="center", color="#ffffff", fontfamily="monospace", weight="bold"
)

fig.text(
    0.515, 0.94,
    f"{p1_team} | {p2_team}", size=12,
    ha="center", color="#94a3b8", fontfamily="monospace"
)

# Legend (Açıklama)
fig.text(0.35, 0.05, f"🔵 {p1_name}", size=14, color="#00e5ff", weight="bold", fontfamily="monospace")
fig.text(0.65, 0.05, f"🔴 {p2_name}", size=14, color="#ff0055", weight="bold", fontfamily="monospace")

st.pyplot(fig)

# --- AI YORUMU ---
st.markdown("---")
st.info(f"💡 **AI Analizi:** {p1_name}, bitiricilik ve hız konusunda daha etkiliyken; {p2_name} fiziksel güç ve bağlantı oyununda (Pas) öne çıkıyor.")
