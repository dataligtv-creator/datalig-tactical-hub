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
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stSelectbox > div > div { background-color: #1e293b !important; color: white !important; }
    .stFileUploader { padding: 20px; border: 1px dashed #00e5ff; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<div style='font-size: 40px;'>🧬</div>", unsafe_allow_html=True)
with col2:
    st.title("SCOUT DNA")
    st.caption("Veri Tabanlı Oyuncu Karşılaştırma")

st.markdown("---")

# --- 1. VERİ YÖNETİMİ (DATA HANDLING) ---
# Varsayılan (Demo) Veri Seti
default_data = {
    'Oyuncu': ['Mauro Icardi', 'Edin Dzeko', 'Ciro Immobile', 'Rafa Silva', 'Gedson Fernandes', 'Fred'],
    'Takım': ['Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Beşiktaş', 'Beşiktaş', 'Fenerbahçe'],
    'HIZ': [75, 68, 80, 88, 85, 82],
    'ŞUT': [88, 85, 87, 78, 70, 75],
    'PAS': [70, 78, 72, 84, 82, 85],
    'DRİBLİNG': [78, 72, 79, 89, 86, 84],
    'DEFANS': [35, 45, 38, 45, 75, 78],
    'FİZİK': [82, 85, 78, 65, 80, 76]
}

# Yan Menüden Dosya Yükleme
with st.sidebar:
    st.header("📂 VERİ MERKEZİ")
    uploaded_file = st.file_uploader("Scout Dosyası Yükle (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("Veri seti başarıyla yüklendi!")
        except:
            st.error("Dosya formatı hatalı!")
            df = pd.DataFrame(default_data)
    else:
        st.info("Demo veri seti kullanılıyor.")
        df = pd.DataFrame(default_data)

# --- 2. OYUNCU SEÇİM EKRANI ---
col_select1, col_select2 = st.columns(2)

player_list = df['Oyuncu'].unique().tolist()

with col_select1:
    st.markdown("### 🔵 OYUNCU 1")
    # Icardi'yi varsayılan seç (listede varsa)
    idx1 = player_list.index('Mauro Icardi') if 'Mauro Icardi' in player_list else 0
    p1_name = st.selectbox("Oyuncu Seç", player_list, index=idx1, key="p1_select")
    
    # Seçilen oyuncunun verilerini çek
    p1_data = df[df['Oyuncu'] == p1_name].iloc[0]
    p1_stats = [p1_data['HIZ'], p1_data['ŞUT'], p1_data['PAS'], p1_data['DRİBLİNG'], p1_data['DEFANS'], p1_data['FİZİK']]
    p1_team = p1_data['Takım']

with col_select2:
    st.markdown("### 🔴 OYUNCU 2")
    # Dzeko'yu varsayılan seç
    idx2 = player_list.index('Edin Dzeko') if 'Edin Dzeko' in player_list else 1
    p2_name = st.selectbox("Oyuncu Seç", player_list, index=idx2, key="p2_select")
    
    # Seçilen oyuncunun verilerini çek
    p2_data = df[df['Oyuncu'] == p2_name].iloc[0]
    p2_stats = [p2_data['HIZ'], p2_data['ŞUT'], p2_data['PAS'], p2_data['DRİBLİNG'], p2_data['DEFANS'], p2_data['FİZİK']]
    p2_team = p2_data['Takım']

# --- 3. RADAR GRAFİĞİ (GÖRSELLEŞTİRME) ---
st.markdown("---")

params = ["HIZ", "ŞUT", "PAS", "DRİBLİNG", "DEFANS", "FİZİK"]

baker = PyPizza(
    params=params,                  
    background_color="#0b0f19",     
    straight_line_color="#222222",  
    straight_line_lw=1,                           
    last_circle_lw=1,
    other_circle_lw=1,
    other_circle_ls="-."
)

try:
    fig, ax = baker.make_pizza(
        p1_stats,                     
        compare_values=p2_stats,      
        figsize=(10, 10),
        
        # Renk Ayarları (P1: Mavi, P2: Kırmızı)
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
    st.error(f"Grafik hatası: {e}")

# --- 4. EXCEL ŞABLONU İNDİRME ---
with st.sidebar:
    st.markdown("---")
    st.info("💡 Kendi verini yüklemek için aşağıdaki formatta bir Excel hazırla:")
    st.code("Oyuncu, Takım, HIZ, ŞUT, PAS, DRİBLİNG, DEFANS, FİZİK", language="csv")
