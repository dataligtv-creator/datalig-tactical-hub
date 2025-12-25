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
</style>
""", unsafe_allow_html=True)

st.title("📋 THE WAR ROOM")
st.caption("Otomatik Taktiksel Planlama & Rakip Panzehiri")
st.markdown("---")

# --- HAFIZA KONTROLÜ ---
aktif_oyuncu = st.session_state.get('aktif_oyuncu', "Genel Rakip")

# --- SOL PANEL: TAKTİK AYARLARI ---
col_sidebar, col_pitch = st.columns([1, 2])

with col_sidebar:
    st.markdown(f"### 🛡️ RAKİP ANALİZİ: <span style='color:#ff0055;'>{aktif_oyuncu}</span>", unsafe_allow_html=True)
    st.info(f"Sistem, {aktif_oyuncu} üzerine bir savunma planı hazırlıyor.")
    
    st.markdown("### ⚙️ DİZİLİŞ SEÇİMİ")
    formation = st.selectbox("Kendi Dizilişimiz", ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"])
    
    st.markdown("### 🏹 HÜCUM STRATEJİSİ")
    focus_zone = st.radio("Odak Bölgesi", ["Kanat Organizasyonu", "Merkez Delici Paslar", "Bek Arkası Koşular"])
    
    if st.button("Taktiği Sahaya Uygula"):
        st.balloons()
        st.success("Taktiksel plan senkronize edildi.")

# --- SAHA ÇİZİMİ ---
with col_pitch:
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555', half=False)
    fig, ax = pitch.draw(figsize=(8, 11))
    fig.set_facecolor('#0b0f19')

    # Dizilişlere Göre Oyuncu Pozisyonları (Örnek: 4-3-3)
    if formation == "4-3-3":
        # Defans
        pitch.scatter(15, 40, s=400, color='#0b0f19', edgecolor='#00e5ff', linewidth=2, ax=ax) # GK
        pitch.scatter(35, 15, s=400, color='#00e5ff', ax=ax); pitch.scatter(35, 65, s=400, color='#00e5ff', ax=ax) # Bekler
        pitch.scatter(30, 30, s=400, color='#00e5ff', ax=ax); pitch.scatter(30, 50, s=400, color='#00e5ff', ax=ax) # Stoperler
        # Orta Saha
        pitch.scatter(55, 40, s=400, color='#00e5ff', ax=ax) # CDM
        pitch.scatter(65, 25, s=400, color='#00e5ff', ax=ax); pitch.scatter(65, 55, s=400, color='#00e5ff', ax=ax) # CMler
        # Forvet
        pitch.scatter(95, 15, s=400, color='#00e5ff', ax=ax); pitch.scatter(95, 65, s=400, color='#00e5ff', ax=ax) # Kanatlar
        pitch.scatter(105, 40, s=400, color='#00e5ff', ax=ax) # ST

    # Dinamik Oklar (Stratejiye Göre)
    if focus_zone == "Kanat Organizasyonu":
        pitch.arrows(35, 15, 80, 10, width=2, color='#00e5ff', alpha=0.6, ax=ax) # Sol bek bindirme
        pitch.arrows(35, 65, 80, 70, width=2, color='#00e5ff', alpha=0.6, ax=ax) # Sağ bek bindirme
    elif focus_zone == "Merkez Delici Paslar":
        pitch.arrows(65, 40, 95, 40, width=3, color='#f59e0b', ax=ax) # Merkez dikine pas
    
    # Rakip Odak Noktası (Scout DNA'dan gelen oyuncu nerede durabilir?)
    pitch.scatter(85, 40, s=500, color='none', edgecolor='#ff0055', linewidth=3, linestyle='--', ax=ax)
    ax.text(40, 85, f"HEDEF: {aktif_oyuncu}", color='#ff0055', fontsize=12, ha='center', fontweight='bold')

    st.pyplot(fig)

# --- AI TAKTİKSEL ANALİZ NOTU ---
st.markdown("---")
with st.expander("🤖 AI TAKTİKSEL TAVSİYESİ (ÖZEL)"):
    st.write(f"Hocam, {aktif_oyuncu} genellikle defansif geçişlerde ağır kalıyor. Seçtiğiniz {formation} dizilişiyle {focus_zone} üzerinden yapacağımız baskı, rakibin dengesini bozacaktır. Özellikle 2. bölgedeki pres yoğunluğunu %15 artırmanızı öneririm.")
