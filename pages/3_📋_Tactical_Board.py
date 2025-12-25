import streamlit as st
import pandas as pd
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="War Room | DATALIG", page_icon="📋", layout="wide")

# --- CSS (KURUMSAL VE SADE) ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stButton button { background-color: #00e5ff !important; color: #0b0f19 !important; font-weight: bold; border-radius: 5px; }
    .report-box { background-color: rgba(30, 41, 59, 0.4); padding: 20px; border-left: 4px solid #ff0055; border-radius: 8px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("📋 THE WAR ROOM")
st.caption("Savunma Kurgusu ve Stratejik Planlama")
st.markdown("---")

# --- HAFIZA KONTROLÜ ---
aktif_oyuncu = st.session_state.get('aktif_oyuncu', "Genel Rakip")

# --- SOL PANEL: TAKTİK AYARLARI ---
col_sidebar, col_pitch = st.columns([1, 2])

with col_sidebar:
    st.markdown(f"### 🛡️ HEDEF ANALİZİ: <span style='color:#ff0055;'>{aktif_oyuncu}</span>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ SAVUNMA KURGUSU")
    formation = st.selectbox("Dizilişimiz", ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"])
    
    st.markdown("### 🏹 ÖNLEMLER")
    defense_style = st.radio("Savunma Tipi", ["Adam Adama Markaj", "Alan Savunması", "Yüksek Prese Dayalı"])
    
    if st.button("Taktiği Onayla"):
        # Balonlar uçuruldu! Artık sadece ciddi bir onay mesajı var.
        st.success("Taktiksel plan savaş odasına gönderildi.")

# --- SAHA ÇİZİMİ ---
with col_pitch:
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555', half=False)
    fig, ax = pitch.draw(figsize=(8, 11))
    fig.set_facecolor('#0b0f19')

    # Dizilişlere Göre Oyuncu Pozisyonları
    if formation == "4-2-3-1":
        # Defans
        pitch.scatter(15, 40, s=400, color='#0b0f19', edgecolor='#00e5ff', linewidth=2, ax=ax) # GK
        pitch.scatter(30, 15, s=400, color='#00e5ff', ax=ax); pitch.scatter(30, 65, s=400, color='#00e5ff', ax=ax) # Bekler
        pitch.scatter(25, 32, s=400, color='#00e5ff', ax=ax); pitch.scatter(25, 48, s=400, color='#00e5ff', ax=ax) # Stoperler
        # Ön Libero
        pitch.scatter(45, 30, s=400, color='#00e5ff', ax=ax); pitch.scatter(45, 50, s=400, color='#00e5ff', ax=ax)
        # Ofansif Hat
        pitch.scatter(75, 40, s=400, color='#00e5ff', ax=ax) # CAM
        pitch.scatter(85, 15, s=400, color='#00e5ff', ax=ax); pitch.scatter(85, 65, s=400, color='#00e5ff', ax=ax) # Kanatlar
        # Forvet
        pitch.scatter(105, 40, s=400, color='#00e5ff', ax=ax) # ST

    # Rakip Odak Noktası (Kırmızı Halka)
    pitch.scatter(85, 40, s=600, color='none', edgecolor='#ff0055', linewidth=3, linestyle='--', ax=ax)
    ax.text(40, 85, f"TEHLİKE: {aktif_oyuncu}", color='#ff0055', fontsize=12, ha='center', fontweight='bold')

    st.pyplot(fig)

# --- ALT ANALİZ: GOL VE SAVUNMA ANALİZİ ---
st.markdown("---")
st.markdown(f"### 📋 {aktif_oyuncu} | Kritik Savunma Raporu")

# Bu kısım normalde Oracle'dan dinamik gelebilir, şimdilik akıllı bir mantık kuruyoruz:
col_info1, col_info2 = st.columns(2)

with col_info1:
    st.markdown('<div class="report-box">', unsafe_allow_html=True)
    st.markdown("#### ⚽ Gol Analizi")
    if "Icardi" in aktif_oyuncu:
        st.write("Oyuncu ceza sahası içinde 'tek dokunuş' gollerinde uzman. Genellikle arka direk koşuları ve kaleciden dönen topları takip ediyor.")
    elif "Rafa" in aktif_oyuncu:
        st.write("Merkezden driplingle girip uzak köşeye plase bırakmayı seviyor. Kontrataklarda en tehlikeli silah.")
    else:
        st.write("Oyuncu son vuruşlarda soğukkanlı. Özellikle kanat ortalarında markajdan kurtulma becerisi çok yüksek.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_info2:
    st.markdown('<div class="report-box" style="border-left-color: #00e5ff;">', unsafe_allow_html=True)
    st.markdown("#### 🛡️ Savunma Panzehiri")
    st.write(f"Hocam, {aktif_oyuncu} için seçtiğiniz **{defense_style}** kurgusu doğru.")
    st.write("Tavsiyem: Rakibin pas kanallarını kapatmak için ön liberolardan birini 'gölge markaj' görevine çekin. Rakip arkaya koşu attığında ofsayt tuzağı yerine derin savunmayı tercih edin.")
    st.markdown('</div>', unsafe_allow_html=True)
