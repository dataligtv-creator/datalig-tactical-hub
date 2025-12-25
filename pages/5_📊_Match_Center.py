import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Match Center | DATALIG", page_icon="📊", layout="wide")

# --- CSS (NEON TEMA) ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'JetBrains Mono', monospace; }
    .stMetric { background-color: rgba(30, 41, 59, 0.5); padding: 10px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .stMetric label { color: #00e5ff !important; }
    .stMetric div { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<div style='font-size: 40px;'>📊</div>", unsafe_allow_html=True)
with col2:
    st.title("MATCH CENTER")
    st.caption("Advanced Data Visualization Hub")

st.markdown("---")

# --- DEMO VERİ ÜRETİCİ (GERÇEK MAÇ GİBİ) ---
def generate_shot_data():
    # Rastgele şut verisi (x, y koordinatları, xG değeri, Gol mü?)
    shots = pd.DataFrame({
        'x': np.random.uniform(60, 115, 20), # Sadece hücum sahası
        'y': np.random.uniform(10, 70, 20),
        'xg': np.random.uniform(0.05, 0.6, 20),
        'is_goal': np.random.choice([True, False], 20, p=[0.2, 0.8])
    })
    return shots

# --- ANALİZ SEKMELERİ ---
tabs = st.tabs(["🎯 ŞUT HARİTASI (xG)", "🔥 ISI HARİTASI", "🕸️ PAS AĞI"])

# 1. ŞUT HARİTASI
with tabs[0]:
    col_viz, col_stat = st.columns([3, 1])
    
    with col_stat:
        st.markdown("### 📈 İSTATİSTİKLER")
        shots_df = generate_shot_data()
        total_shots = len(shots_df)
        total_goals = len(shots_df[shots_df['is_goal'] == True])
        total_xg = shots_df['xg'].sum()
        
        st.metric("Toplam Şut", f"{total_shots}", delta="Maç Başı Ort. Üstü")
        st.metric("Goller", f"{total_goals}", delta="Etkili Bitiricilik")
        st.metric("Toplam xG", f"{total_xg:.2f}", delta_color="off")
        
        st.info("💡 **Analist Notu:** Ceza sahası dışından çok fazla düşük xG'li şut deneniyor. Set oyununa dönülmeli.")

    with col_viz:
        # MPLSOCCER PITCH KURULUMU
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#00e5ff', linewidth=2)
        fig, ax = pitch.draw(figsize=(10, 7))
        fig.set_facecolor('#0b0f19')

        # Şutları Çiz
        # Gol Olmayanlar (Kırmızı X)
        no_goals = shots_df[~shots_df['is_goal']]
        pitch.scatter(no_goals.x, no_goals.y, s=no_goals.xg*500, c='#ef4444', alpha=0.7, marker='x', ax=ax, label='Miss')
        
        # Gol Olanlar (Yeşil Top)
        goals = shots_df[shots_df['is_goal']]
        pitch.scatter(goals.x, goals.y, s=goals.xg*500, c='#22c55e', edgecolors='white', marker='o', ax=ax, label='Goal')

        ax.legend(facecolor='#1e293b', edgecolor='white', labelcolor='white', loc='upper left')
        st.pyplot(fig)

# 2. ISI HARİTASI (DEMO)
with tabs[1]:
    st.markdown("### 🔥 TAKIM PRESLENME HARİTASI")
    
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#0b0f19', line_color='#00e5ff')
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#0b0f19')
    
    # Rastgele yoğunluk verisi
    x = np.random.uniform(0, 120, 1000)
    y = np.random.uniform(0, 80, 1000)
    
    # KDE Plot (Isı Haritası)
    sns_cmap = "magma"
    pitch.kdeplot(x, y, ax=ax, cmap=sns_cmap, fill=True, levels=100, alpha=0.6, shade_lowest=False)
    
    st.pyplot(fig)

# 3. PAS AĞI (STATİK GÖRSEL - GELİŞTİRİLECEK)
with tabs[2]:
    st.warning("🚧 Pas Ağı modülü StatsBomb verisi entegrasyonu bekliyor.")
    
    # Basit bir pas görselleştirmesi (Demo)
    pitch = Pitch(pitch_color='#0b0f19', line_color='#555555')
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#0b0f19')
    
    # Örnek Paslar
    pitch.arrows(20, 40, 50, 60, width=2, headwidth=10, color='#00e5ff', ax=ax, label="Progressive Pass")
    pitch.arrows(50, 60, 80, 40, width=2, headwidth=10, color='#00e5ff', ax=ax)
    pitch.arrows(80, 40, 110, 40, width=4, headwidth=15, color='#22c55e', ax=ax, label="Assist")
    
    ax.legend(facecolor='#1e293b', labelcolor='white')
    st.pyplot(fig)
