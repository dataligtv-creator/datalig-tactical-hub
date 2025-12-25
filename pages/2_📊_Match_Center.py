# Scout DNA sayfasında seçim yapınca:
st.session_state['secilen_oyuncu'] = p1_name

# Match Center sayfasında okurken:
if 'secilen_oyuncu' in st.session_state:
    varsayilan_oyuncu = st.session_state['secilen_oyuncu']
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
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stMetric { background-color: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown("<div style='font-size: 40px;'>📊</div>", unsafe_allow_html=True)
with col2:
    st.title("MATCH CENTER")
    st.caption("Veri Görselleştirme & Pas Ağları")

st.markdown("---")

# --- DEMO VERİ ÜRETİCİLERİ ---
def get_shot_data():
    # Rastgele şut verisi üret
    return pd.DataFrame({
        'x': np.random.uniform(60, 118, 15),
        'y': np.random.uniform(10, 70, 15),
        'xg': np.random.uniform(0.05, 0.7, 15),
        'is_goal': np.random.choice([True, False], 15, p=[0.2, 0.8])
    })

def get_pass_network_data():
    # 11 Oyuncu için sabit pozisyonlar (4-3-3 gibi)
    # x: saha boyu (0-120), y: saha eni (0-80)
    players = {
        1: {'name': 'GK', 'x': 5, 'y': 40, 'passes': 25},
        2: {'name': 'RB', 'x': 30, 'y': 10, 'passes': 45},
        3: {'name': 'RCB', 'x': 25, 'y': 30, 'passes': 60},
        4: {'name': 'LCB', 'x': 25, 'y': 50, 'passes': 62},
        5: {'name': 'LB', 'x': 30, 'y': 70, 'passes': 48},
        6: {'name': 'CDM', 'x': 50, 'y': 40, 'passes': 75},
        7: {'name': 'RCM', 'x': 65, 'y': 25, 'passes': 55},
        8: {'name': 'LCM', 'x': 65, 'y': 55, 'passes': 58},
        9: {'name': 'RW', 'x': 90, 'y': 15, 'passes': 30},
        10: {'name': 'ST', 'x': 100, 'y': 40, 'passes': 20},
        11: {'name': 'LW', 'x': 90, 'y': 65, 'passes': 32}
    }
    return players

# --- SEKME YAPISI ---
tabs = st.tabs(["🕸️ PAS AĞI (NETWORK)", "🎯 ŞUT ANALİZİ (xG)", "🔥 ISI HARİTASI"])

# --- 1. SEKME: PAS AĞI ---
with tabs[0]:
    col_info, col_pitch = st.columns([1, 3])
    
    with col_info:
        st.info("Bu grafik oyuncuların ortalama pozisyonlarını ve pas bağlantılarını gösterir.")
        st.metric("Toplam Pas", "512", delta="+%12")
        st.metric("Pas İsabeti", "%84", delta="Başarılı")
        st.markdown("### 🔑 Kilit Bağlantı")
        st.write("CDM ➡️ LCM (18 Pas)")

    with col_pitch:
        # Saha Çizimi
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555')
        fig, ax = pitch.draw(figsize=(10, 7))
        fig.set_facecolor('#0b0f19')
        
        players = get_pass_network_data()
        
        # Pas Bağlantılarını Çiz (Lines)
        # Basitlik için CDM'den herkese hat çekiyoruz (Demo)
        cdm = players[6]
        for pid, p in players.items():
            if pid != 6:
                pitch.lines(cdm['x'], cdm['y'], p['x'], p['y'],
                            lw=p['passes']/10, color='#00e5ff', alpha=0.3, zorder=1, ax=ax)

        # Oyuncuları Çiz (Nodes)
        for pid, p in players.items():
            pitch.scatter(p['x'], p['y'], s=p['passes']*8, 
                          color='#0b0f19', edgecolor='#00e5ff', linewidth=2, zorder=2, ax=ax)
            
            pitch.annotate(p['name'], xy=(p['x'], p['y']), 
                           va='center', ha='center', color='white', fontsize=10, zorder=3, ax=ax)

        st.pyplot(fig)

# --- 2. SEKME: ŞUT HARİTASI ---
with tabs[1]:
    col_viz, col_stat = st.columns([3, 1])
    
    shots = get_shot_data()
    
    with col_stat:
        st.markdown("### 📈 xG ÖZETİ")
        st.metric("Toplam Şut", len(shots))
        st.metric("Toplam xG", f"{shots['xg'].sum():.2f}")
        st.caption("Daire büyüklüğü gol beklentisini (xG) ifade eder.")

    with col_viz:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555')
        fig, ax = pitch.draw(figsize=(10, 7))
        fig.set_facecolor('#0b0f19')
        
        # Gol Olmayanlar
        miss = shots[~shots['is_goal']]
        pitch.scatter(miss.x, miss.y, s=miss.xg*500, c='#ef4444', alpha=0.6, marker='x', label='Kaçan', ax=ax)
        
        # Gol Olanlar
        goal = shots[shots['is_goal']]
        pitch.scatter(goal.x, goal.y, s=goal.xg*500, c='#22c55e', edgecolors='white', marker='football', label='GOL', ax=ax)
        
        ax.legend(facecolor='#0b0f19', edgecolor='white', labelcolor='white')
        st.pyplot(fig)

# --- 3. SEKME: ISI HARİTASI ---
with tabs[2]:
    st.markdown("### 🔥 TAKIM YOĞUNLUK HARİTASI")
    
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#0b0f19', line_color='#555555')
    fig, ax = pitch.draw(figsize=(10, 7))
    fig.set_facecolor('#0b0f19')
    
    # Rastgele yoğunluk verisi (Demo)
    x = np.random.normal(60, 20, 100)
    y = np.random.normal(40, 15, 100)
    
    # KDE Plot (Isı Haritası)
    # Hata almamak için 'shade' yerine 'fill' kullanıyoruz (yeni sürüm uyumlu)
    sns_cmap = "magma"
    pitch.kdeplot(x, y, ax=ax, cmap=sns_cmap, fill=True, levels=100, alpha=0.6)
    
    st.pyplot(fig)
