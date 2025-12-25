import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Scout DNA Pro | DATALIG", page_icon="🧬", layout="wide")

# --- CSS (NEON TEMA) ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stSelectbox > div > div { background-color: #1e293b !important; color: white !important; }
    .stFileUploader { padding: 10px; border: 1px dashed #00e5ff; border-radius: 10px; }
    .stMetric { background-color: rgba(30, 41, 59, 0.5); padding: 10px; border-radius: 10px; border-left: 5px solid #00e5ff; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.markdown("### 🧬 SCOUT DNA PRO | <span style='color:#00e5ff;'>DATALIG</span>", unsafe_allow_html=True)
st.caption("Interaktif Oyuncu Karşılaştırma Paneli")
st.markdown("---")

# --- 1. VERİ YÖNETİMİ ---
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

with st.sidebar:
    st.header("📂 VERİ MERKEZİ")
    uploaded_file = st.file_uploader("Scout Dosyası Yükle (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("Veri seti yüklendi!")
        except:
            st.error("Hatalı dosya!")
            df = pd.DataFrame(default_data)
    else:
        df = pd.DataFrame(default_data)

# --- 2. OYUNCU SEÇİM EKRANI ---
col_select1, col_select2 = st.columns(2)
player_list = df['Oyuncu'].unique().tolist()
categories = ['HIZ', 'ŞUT', 'PAS', 'DRİBLİNG', 'DEFANS', 'FİZİK']

with col_select1:
    st.markdown("### 🔵 OYUNCU 1 (ODAK)")
    idx1 = player_list.index('Mauro Icardi') if 'Mauro Icardi' in player_list else 0
    p1_name = st.selectbox("Oyuncu Seç", player_list, index=idx1, key="p1_select")
    st.session_state['aktif_oyuncu'] = p1_name 
    
    p1_data = df[df['Oyuncu'] == p1_name].iloc[0]
    p1_stats = [p1_data[c] for c in categories]
    # Plotly radar için döngüyü kapatmak lazım (ilk elemanı sona ekle)
    p1_stats_plot = p1_stats + [p1_stats[0]]

with col_select2:
    st.markdown("### 🔴 OYUNCU 2 (RAKİP)")
    idx2 = player_list.index('Edin Dzeko') if 'Edin Dzeko' in player_list else 1
    p2_name = st.selectbox("Oyuncu Seç", player_list, index=idx2, key="p2_select")
    
    p2_data = df[df['Oyuncu'] == p2_name].iloc[0]
    p2_stats = [p2_data[c] for c in categories]
    p2_stats_plot = p2_stats + [p2_stats[0]]

# --- 3. INTERAKTIF RADAR GRAFİĞİ (PLOTLY) ---
st.markdown("---")
st.markdown("### 📊 Interaktif Radar Karşılaştırma")
st.info("Değerleri görmek için grafiğin üzerine gelin.")

categories_plot = categories + [categories[0]]

fig = go.Figure()

# Oyuncu 1 Trace
fig.add_trace(go.Scatterpolar(
    r=p1_stats_plot,
    theta=categories_plot,
    fill='toself',
    name=p1_name,
    line_color='#00e5ff',
    fillcolor='rgba(0, 229, 255, 0.3)',
    marker=dict(size=8)
))

# Oyuncu 2 Trace
fig.add_trace(go.Scatterpolar(
    r=p2_stats_plot,
    theta=categories_plot,
    fill='toself',
    name=p2_name,
    line_color='#ff0055',
    fillcolor='rgba(255, 0, 85, 0.3)',
    marker=dict(size=8)
))

fig.update_layout(
    polar=dict(
        bgcolor='#0b0f19',
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            gridcolor="#222222",
            linecolor="#444444",
            tickfont=dict(color="#94a3b8")
        ),
        angularaxis=dict(
            gridcolor="#222222",
            linecolor="#444444",
            tickfont=dict(color="white", size=12)
        )
    ),
    showlegend=True,
    paper_bgcolor='#0b0f19',
    plot_bgcolor='#0b0f19',
    legend=dict(font=dict(color="white", size=14), orientation="h", y=-0.1),
    margin=dict(t=20, b=20),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- 4. ÖZET İSTATİSTİK KARTLARI ---
st.markdown("---")
st.markdown("### 🧬 DNA ÖZETİ")
c1, c2, c3 = st.columns(3)

# Basit bir kıyaslama metriği
diff_score = sum(p1_stats) - sum(p2_stats)
color = "normal" if diff_score >= 0 else "inverse"

with c1:
    st.metric(f"{p1_name} Toplam", sum(p1_stats))
with c2:
    st.metric(f"{p2_name} Toplam", sum(p2_stats))
with c3:
    st.metric("Güç Farkı", diff_score)

# Sidebar alt bilgi
with st.sidebar:
    st.markdown("---")
    st.info(f"📍 Şu an odaklanılan: **{st.session_state['aktif_oyuncu']}**")
