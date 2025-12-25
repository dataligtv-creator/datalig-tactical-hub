# Scout DNA sayfasında seçim yapınca:
st.session_state['secilen_oyuncu'] = p1_name

# Match Center sayfasında okurken:
if 'secilen_oyuncu' in st.session_state:
    varsayilan_oyuncu = st.session_state['secilen_oyuncu']
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pressure Lab | DATALIG", page_icon="🔥", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stSlider > div > div > div > div { background-color: #ef4444 !important; } /* Kırmızı Slider */
    .stMetric { background-color: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown("<div style='font-size: 40px;'>🔥</div>", unsafe_allow_html=True)
with col2:
    st.title("PRESSURE LAB")
    st.caption("Gegenpressing & PPDA Analizi")

st.markdown("---")

# --- SOL PANEL: VERİ GİRİŞİ ---
col_input, col_viz = st.columns([1, 2])

with col_input:
    st.markdown("### 🎛️ PRES METRİKLERİ")
    
    st.info("Bölgelere göre pres yoğunluğunu (0-100) giriniz.")
    
    # Bölgesel Pres Girişleri
    zone3_press = st.slider("3. BÖLGE (Hücum Presi)", 0, 100, 85, key="z3")
    zone2_press = st.slider("2. BÖLGE (Orta Saha Blok)", 0, 100, 60, key="z2")
    zone1_press = st.slider("1. BÖLGE (Defansif Sertlik)", 0, 100, 40, key="z1")
    
    st.markdown("---")
    st.markdown("### 📉 PPDA HESAPLAYICI")
    st.caption("Rakibin yaptığı pas / Bizim savunma aksiyonumuz")
    
    opp_passes = st.number_input("Rakip Pas Sayısı", value=350, step=10)
    def_actions = st.number_input("Savunma Aksiyonları (Müdahale, Pas Arası)", value=45, step=1)
    
    if def_actions > 0:
        ppda = opp_passes / def_actions
    else:
        ppda = 0

with col_viz:
    st.markdown("### 🌡️ ISI HARİTASI & SONUÇ")
    
    # Metrik Gösterimi
    c1, c2, c3 = st.columns(3)
    c1.metric("PPDA SKORU", f"{ppda:.2f}", delta="-Düşük İyidir" if ppda < 10 else "Yüksek (Pasif)")
    
    avg_press = (zone3_press + zone2_press + zone1_press) / 3
    c2.metric("GENEL YOĞUNLUK", f"%{avg_press:.0f}", delta="Agresif" if avg_press > 70 else "Dengeli")
    
    press_style = "Yüksek Blok (Gegenpress)" if zone3_press > 75 else "Derin Blok (Park the Bus)"
    c3.metric("OYUN TARZI", press_style)

    # SAHA GÖRSELLEŞTİRME (Basit ve İşlevsel)
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='#0b0f19',
        line_color='#555555',
        line_zorder=2,
    )
    
    fig, ax = pitch.draw(figsize=(8, 10))
    fig.set_facecolor('#0b0f19')
    
    # 3 Bölgeyi Renklendir (Alpha değeri yoğunluğa göre değişir)
    # Zone 3 (Hücum) - En Üst
    ax.fill_between([0, 80], 80, 120, color='#ef4444', alpha=zone3_press/120, label='Zone 3')
    
    # Zone 2 (Orta) - Orta
    ax.fill_between([0, 80], 40, 80, color='#f59e0b', alpha=zone2_press/120, label='Zone 2')
    
    # Zone 1 (Defans) - Alt
    ax.fill_between([0, 80], 0, 40, color='#3b82f6', alpha=zone1_press/120, label='Zone 1')
    
    # Yazılar
    ax.text(40, 100, f"3. BÖLGE\n%{zone3_press}", ha='center', va='center', color='white', fontsize=15, fontweight='bold')
    ax.text(40, 60, f"2. BÖLGE\n%{zone2_press}", ha='center', va='center', color='white', fontsize=15, fontweight='bold')
    ax.text(40, 20, f"1. BÖLGE\n%{zone1_press}", ha='center', va='center', color='white', fontsize=15, fontweight='bold')

    st.pyplot(fig)
