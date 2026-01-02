import streamlit as st
import pandas as pd
import plotly.express as px

# --- 🛰️ ORACLE BAĞLANTISI ---
tactic_context = st.session_state.get('tactic_context', {})
focus_team = tactic_context.get('focus_team', 'GENEL')
focus_formation = tactic_context.get('formation', '4-3-3')
oracle_report = tactic_context.get('scouting_report', "Oracle sayfasında henüz bir analiz yapılmadı.")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Scout DNA | DATALIG", page_icon="🧬", layout="wide")

# --- CSS (Stitch Temasına Uygun) ---
st.markdown("""
<style>
    .stApp { background: #0B0E14; color: #cbd5e1; }
    .scout-card { 
        background: rgba(19, 27, 38, 0.9); 
        border: 1px solid rgba(0, 229, 255, 0.2); 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 4px solid #00E5FF;
    }
    .stDataFrame { background: #131B26; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("🧬 SCOUT DNA")
st.caption(f"Aktif Odak: {focus_team} | Sistem: {focus_formation}")

# --- ÜST PANEL: ORACLE ÖZETİ ---
with st.expander("🧠 ORACLE STRATEJİK NOTLARI (Genişlet)", expanded=True):
    st.markdown(f'<div class="scout-card">{oracle_report[:500]}...</div>', unsafe_allow_html=True)

st.markdown("---")

# --- ANA İÇERİK ---
col1, col2 = st.columns([1, 1])

# Örnek Veri (Burayı kendi veri tabanına bağlayabilirsin)
data = {
    "Oyuncu": ["Archie Brown", "Filip Kostić", "Levent Mercan", "Jayden Oosterwolde"],
    "Yaş": [23, 33, 24, 24],
    "Hız": [92, 84, 86, 94],
    "Savunma": [78, 72, 75, 85],
    "Hücum": [85, 89, 79, 74],
    "Uyum (%)": [92, 88, 76, 95]
}
df = pd.DataFrame(data)

with col1:
    st.markdown("### 📋 ADAY LİSTESİ")
    # Oracle'da adı geçen oyuncuyu vurgulama
    st.dataframe(df.style.background_gradient(subset=['Uyum (%)'], cmap='Blues'), use_container_width=True)

with col2:
    st.markdown("### 📊 PERFORMANS KIYASI")
    fig = px.bar(df, x="Oyuncu", y="Uyum (%)", color="Hız", 
                 title=f"{focus_formation} Sistemine Göre Projeksiyon",
                 template="plotly_dark", color_continuous_scale='IceFire')
    st.plotly_chart(fig, use_container_width=True)

# --- OYUNCU DNA PROFİLİ (RADAR) ---
st.markdown("---")
st.markdown("### 🕸️ OYUNCU DNA PROFİLİ")
selected_p = st.selectbox("Detaylı analiz için oyuncu seçin:", df["Oyuncu"])

p_stats = df[df["Oyuncu"] == selected_p].iloc[0]
radar_df = pd.DataFrame(dict(
    r=[p_stats['Hız'], p_stats['Savunma'], p_stats['Hücum'], p_stats['Uyum (%)'], 80],
    theta=['Hız', 'Savunma', 'Hücum', 'Uyum', 'Pas']
))

fig_radar = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
fig_radar.update_traces(fill='toself', line_color='#00E5FF')
fig_radar.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
st.plotly_chart(fig_radar, use_container_width=True)
