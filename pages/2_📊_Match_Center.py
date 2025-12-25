import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import Pitch

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Match Center Pro | DATALIG", page_icon="📊", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stMetric { background-color: rgba(30, 41, 59, 0.5); padding: 15px; border-radius: 10px; border: 1px solid #00e5ff; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("📊 MATCH CENTER PRO")
st.caption("Interaktif Veri Analiz Paneli")
st.markdown("---")

# --- DATA SİMÜLASYONU (Daha detaylı) ---
def get_advanced_shots():
    return pd.DataFrame({
        'Oyuncu': np.random.choice(['Icardi', 'Rafa Silva', 'Immobile', 'Dzeko'], 20),
        'x': np.random.uniform(70, 115, 20),
        'y': np.random.uniform(20, 60, 20),
        'xG': np.random.uniform(0.1, 0.8, 20).round(2),
        'Dakika': np.random.randint(1, 90, 20),
        'Sonuç': np.random.choice(['Gol', 'Kaçtı'], 20, p=[0.3, 0.7])
    })

shots_df = get_advanced_shots()

# --- METRİKLER ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam xG", f"{shots_df['xG'].sum():.2f}")
c2.metric("Şut Başı xG", f"{shots_df['xG'].mean():.2f}")
c3.metric("Gol", len(shots_df[shots_df['Sonuç'] == 'Gol']))
c4.metric("İsabetli Şut", "12/20")

st.markdown("---")

# --- PLOTLY INTERAKTİF ŞUT HARİTASI ---
st.markdown("### 🎯 Interaktif Şut Analizi")
st.info("İncelemek istediğiniz şutun üzerine gelin veya grafiği yakınlaştırın.")

# Saha Çizimi (Plotly Arkaplanı olarak)
fig = go.Figure()

# Plotly ile Şutları Çiz
for result in ['Gol', 'Kaçtı']:
    mask = shots_df['Sonuç'] == result
    color = '#22c55e' if result == 'Gol' else '#ef4444'
    symbol = 'circle' if result == 'Gol' else 'x'
    
    fig.add_trace(go.Scatter(
        x=shots_df[mask]['x'],
        y=shots_df[mask]['y'],
        mode='markers',
        name=result,
        marker=dict(
            size=shots_df[mask]['xG'] * 40,
            color=color,
            symbol=symbol,
            line=dict(width=1, color='white')
        ),
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                      "Dakika: %{customdata[1]}<br>" +
                      "xG: %{marker.size}<br>" +
                      "Sonuç: %{text}<extra></extra>",
        customdata=shots_df[mask][['Oyuncu', 'Dakika']],
        text=shots_df[mask]['Sonuç']
    ))

# Saha Çizgilerini Ekle (Plotly üzerine futbol sahası şablonu)
fig.update_layout(
    width=900, height=600,
    template="plotly_dark",
    paper_bgcolor='#0b0f19',
    plot_bgcolor='#0b0f19',
    xaxis=dict(range=[0, 120], showgrid=False, zeroline=False, visible=False),
    yaxis=dict(range=[0, 80], showgrid=False, zeroline=False, visible=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# Kale ve Ceza Sahası Çizgileri (Opsiyonel görsel dokunuş)
fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line_color="white") # Ceza sahası
fig.add_shape(type="rect", x0=114, y0=30, x1=120, y1=50, line_color="white") # 6 pas

st.plotly_chart(fig, use_container_width=True)

# --- ALT ANALİZ: OYUNCU BAZLI ŞUT DAĞILIMI ---
st.markdown("### 📊 Oyuncu Performans Kıyaslama")
fig_bar = px.bar(
    shots_df, x='Oyuncu', y='xG', color='Sonuç',
    title="Oyuncuların Toplam xG Katkısı",
    color_discrete_map={'Gol': '#22c55e', 'Kaçtı': '#ef4444'},
    template="plotly_dark"
)
st.plotly_chart(fig_bar, use_container_width=True)
