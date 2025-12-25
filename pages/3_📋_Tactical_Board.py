import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="War Room | DATALIG", page_icon="📋", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stButton button { background-color: #00e5ff !important; color: #0b0f19 !important; font-weight: bold; }
    .report-box { background-color: rgba(30, 41, 59, 0.4); padding: 20px; border-left: 4px solid #ff0055; border-radius: 8px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("📋 THE WAR ROOM")
st.caption("Stratejik Formasyon ve Savunma Planlama")
st.markdown("---")

# --- HAFIZA KONTROLÜ ---
aktif_oyuncu = st.session_state.get('aktif_oyuncu', "Genel Rakip")

# --- SOL PANEL ---
col_sidebar, col_pitch = st.columns([1, 2])

with col_sidebar:
    st.markdown(f"### 🛡️ HEDEF: <span style='color:#ff0055;'>{aktif_oyuncu}</span>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ TAKTİKSEL KURGU")
    formation = st.selectbox("Diziliş Seçin", ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"])
    defense_style = st.radio("Savunma Tipi", ["Adam Adama Markaj", "Alan Savunması", "Yüksek Pres"])
    
    if st.button("Taktiği Onayla"):
        st.success("Taktiksel plan başarıyla kaydedildi.")

# --- SAHA VE FORMASYON MANTIĞI ---
with col_pitch:
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555', half=False)
    fig, ax = pitch.draw(figsize=(8, 11))
    fig.set_facecolor('#0b0f19')

    # --- OYUNCU POZİSYONLARI (SÖZLÜK YAPISI) ---
    formations_db = {
        "4-3-3": [
            (15, 40), # GK
            (30, 15), (30, 65), (25, 30), (25, 50), # Defans
            (50, 40), (65, 25), (65, 55), # Orta Saha
            (95, 15), (95, 65), (105, 40) # Hücum
        ],
        "4-2-3-1": [
            (15, 40), # GK
            (30, 15), (30, 65), (25, 32), (25, 48), # Defans
            (45, 30), (45, 50), # Ön Libero
            (75, 40), (85, 15), (85, 65), # Ofansif Hat
            (105, 40) # ST
        ],
        "3-5-2": [
            (15, 40), # GK
            (25, 25), (25, 40), (25, 55), # 3 Stoper
            (50, 10), (50, 70), (55, 40), (65, 28), (65, 52), # 5'li Orta Saha
            (100, 30), (100, 50) # 2 Forvet
        ],
        "4-4-2": [
            (15, 40), # GK
            (30, 15), (30, 65), (25, 32), (
