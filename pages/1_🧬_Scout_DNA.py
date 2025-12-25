import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import PyPizza

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Scout DNA | DATALIG", page_icon="🧬", layout="wide")

# --- CSS (NEON TEMA) ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stSlider > div > div > div > div { background-color: #00e5ff !important; }
    .stTextInput input { color: #00e5ff !important; font-weight: bold; background-color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<div style='font-size: 40px;'>🧬</div>", unsafe_allow_html=True)
with col2:
    st.title("SCOUT DNA")
    st.caption("Oyuncu Karşılaştırma Modülü")

st.markdown("---")

# --- OYUNCU SEÇİMİ ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔵 OYUNCU 1")
    p1_name = st.text_input("İsim", "Mauro Icardi", key="p1")
    p1_team = st.text_input("Takım", "Galatasaray", key="t1")
    
    # Değerler
    p1_val = []
    p1_val.append(st.slider("HIZ", 0, 99, 75, key="s1_1"))
    p1_val.append(st.slider("ŞUT", 0, 99, 88, key="s1_2"))
    p1_val.append(st.slider("PAS", 0, 99, 70, key="s1_3"))
    p1_val.append(st.slider("DRİBLİNG", 0, 99, 78, key="s1_4"))
    p1_val.append(st.slider("DEFANS", 0, 99, 35, key="s1_5"))
    p1_val.append(st.slider("FİZİK", 0, 99, 82, key="s1_6"))

with col2:
    st.markdown("### 🔴 OYUNCU 2")
    p2_name = st.text_input("İsim", "Edin Dzeko", key="p2")
    p2_team = st.text_input("Takım", "Fenerbahçe", key="t2")
    
    # Değerler
    p2_val = []
    p2_val.append(st.slider("HIZ", 0, 99, 68, key="s2_1"))
    p2_val.append(st.slider("ŞUT", 0, 99, 85, key="s2_2"))
    p2_val.append(st.slider("PAS", 0, 99, 78, key="s2_3"))
    p2_val.append(st.slider("DRİBLİNG", 0, 99, 72, key="s2_4"))
    p2_val.append(st.slider("DEFANS", 0, 99, 45, key="s2_5"))
    p2_val.append(st.slider("FİZİK", 0, 99, 85, key="s2_6"))

# --- RADAR ÇİZİMİ ---
st.markdown("---")
st.markdown("### 📊 ANALİZ")

# Parametre İsimleri
params = ["HIZ", "ŞUT", "PAS", "DRİBLİNG", "DEFANS", "FİZİK"]

# Pizza Grafiği Ayarları
baker = PyPizza(
    params=params,                  
    background_color="#0b0f19",     
    straight_line_color="#222222",  
    straight_line_lw=1,                           
    last_circle_lw=1,
    other_circle_lw=1,
    other_circle_ls="-."
)

# Çizim (Hatasız Basit Versiyon)
try:
    fig, ax = baker.make_pizza(
        p1_val,                     # Oyuncu 1 Listesi
        compare_values=p2_val,      # Oyuncu 2 Listesi
        figsize=(10, 10),
        
        # Renk Ayarları (Parametre çakışmasını önlemek için sadeleştirildi)
        kwargs_slices=dict(facecolor="#00e5ff", edgecolor="#0b0f19", zorder=2, linewidth=1, alpha=0.8),
        kwargs_compare=dict(facecolor="#ff0055", edgecolor="#0b0f19", zorder=2, linewidth=1, alpha=0.8),
        
        # Yazı Ayarları
        kwargs_params=dict(color="#ffffff", fontsize=12, va="center"),
        kwargs_values=dict(color="#000000", fontsize=11, zorder=3, bbox=dict(edgecolor="#00e5ff", facecolor="#00e5ff", boxstyle="round,pad=0.2")),
        kwargs_compare_values=dict(color="#000000", fontsize=11, zorder=3, bbox=dict(edgecolor="#ff0055", facecolor="#ff0055", boxstyle="round,pad=0.2"))
    )

    # Başlıklar
    fig.text(0.515, 0.97, f"{p1_name} vs {p2_name}", size=24, ha="center", color="white", weight="bold")
    fig.text(0.515, 0.93, f"{p1_team} | {p2_team}", size=14, ha="center", color="#94a3b8")

    # Legend
    fig.text(0.35, 0.04, f"🔵 {p1_name}", size=14, color="#00e5ff", weight="bold")
    fig.text(0.65, 0.04, f"🔴 {p2_name}", size=14, color="#ff0055", weight="bold")

    st.pyplot(fig)

except Exception as e:
    st.error(f"Grafik çizilirken hata oluştu: {e}")
    st.info("Lütfen tüm değerlerin 0-99 arasında olduğundan emin olun.")
