import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

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
        st.success("Taktiksel plan kaydedildi.")

# --- SAHA VE FORMASYON ÇİZİMİ ---
with col_pitch:
    # Saha kurulumu
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555')
    fig, ax = pitch.draw(figsize=(8, 11))
    fig.set_facecolor('#0b0f19')

    # Koordinat veri tabanı
    formations_db = {
        "4-3-3": [(15, 40), (30, 15), (30, 65), (25, 30), (25, 50), (50, 40), (65, 25), (65, 55), (95, 15), (95, 65), (105, 40)],
        "4-2-3-1": [(15, 40), (30, 15), (30, 65), (25, 32), (25, 48), (45, 30), (45, 50), (75, 40), (85, 15), (85, 65), (105, 40)],
        "3-5-2": [(15, 40), (25, 25), (25, 40), (25, 55), (50, 10), (50, 70), (55, 40), (65, 28), (65, 52), (100, 30), (100, 50)],
        "4-4-2": [(15, 40), (30, 15), (30, 65), (25, 32), (25, 48), (60, 15), (60, 35), (60, 45), (60, 65), (100, 35), (100, 45)]
    }

    # Oyuncuları çiz
    coords = formations_db.get(formation, [])
    for x, y in coords:
        pitch.scatter(x, y, s=500, color='#0b0f19', edgecolor='#00e5ff', linewidth=2, zorder=3, ax=ax)

    # Rakip Tehlike Halkası
    pitch.scatter(85, 40, s=800, color='none', edgecolor='#ff0055', linewidth=3, linestyle='--', zorder=2, ax=ax)
    ax.text(40, 85, f"TEHLİKE: {aktif_oyuncu}", color='#ff0055', fontsize=14, ha='center', fontweight='bold')

    st.pyplot(fig)

# --- ANALİZ RAPORU ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.markdown(f'<div class="report-box"><h4>⚽ {aktif_oyuncu} Analizi</h4>', unsafe_allow_html=True)
    if "Icardi" in aktif_oyuncu:
        st.write("Ceza sahası içinde öldürücü. Kaleye sırtı dönükken bile tehlikeli.")
    elif "Dzeko" in aktif_oyuncu:
        st.write("Bağlantı oyununda usta. Hava toplarında mutlak üstünlüğü var.")
    elif "Rafa" in aktif_oyuncu:
        st.write("Patlayıcı hızı var. Geçiş hücumlarında durdurulması imkansız.")
    else:
        st.write("Teknik kapasitesi yüksek, dar alanda çözüm üretebilen bir oyuncu.")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="report-box" style="border-left-color: #00e5ff;"><h4>🛡️ Savunma Reçetesi</h4>', unsafe_allow_html=True)
    st.write(f"Hocam, {formation} dizilişinde {defense_style} kurgusu rakibi bozacaktır.")
    st.write("Özellikle merkez bloktaki oyuncuların rakiple temaslı oynaması gerekiyor.")
    st.markdown('</div>', unsafe_allow_html=True)
