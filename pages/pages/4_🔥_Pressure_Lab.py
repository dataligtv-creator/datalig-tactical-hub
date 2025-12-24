import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pressure Lab | DATALIG", page_icon="🔥", layout="wide")

# --- CSS (ORTAK TASARIM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root { --primary: #00e5ff; --bg: #0b0f19; --surface: rgba(15, 23, 42, 0.6); }
    
    .stApp { 
        background-color: var(--bg); 
        background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); 
        background-size: 40px 40px; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Kart Tasarımları */
    .glass-card {
        background: var(--surface);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    /* Metin Stilleri */
    h1, h2, h3, h4 { color: white !important; font-family: 'Inter', sans-serif; }
    .mono-font { font-family: 'JetBrains Mono', monospace; }
    .neon-text { color: var(--primary); text-shadow: 0 0 10px rgba(0, 229, 255, 0.4); }
    .stat-label { color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { color: white; font-size: 32px; font-weight: bold; font-family: 'JetBrains Mono'; }
</style>
""", unsafe_allow_html=True)

# --- ÜST BAŞLIK ---
col_header, col_logo = st.columns([10, 1])
with col_header:
    st.markdown("## 🛡️ PRESSURE LAB")
    st.caption("Takım Pres Kalitesi ve Defansif Yoğunluk Analizi")
with col_logo:
    st.markdown("# 🔥")

st.markdown("---")

# --- ÜST METRİKLER (KARTLAR) ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="glass-card">
        <div class="stat-label">Avg. Pressure Height</div>
        <div class="stat-value">48.2m <span style="font-size:14px; color:#00e5ff;">▲ 2.1m</span></div>
        <div style="height:4px; width:100%; background:#334155; margin-top:10px; border-radius:2px;">
            <div style="height:100%; width:75%; background:#00e5ff; box-shadow: 0 0 10px #00e5ff;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="glass-card">
        <div class="stat-label">Possession Won</div>
        <div class="stat-value">14.5s <span style="font-size:14px; color:#94a3b8;">Avg</span></div>
        <div style="height:4px; width:100%; background:#334155; margin-top:10px; border-radius:2px;">
            <div style="height:100%; width:45%; background:#00e5ff; box-shadow: 0 0 10px #00e5ff;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    # Filtreler
    st.selectbox("Sezon Kesiti", ["2023/2024 Full", "Son 5 Maç", "vs Top 6"])

with c4:
    st.selectbox("Bölge Filtresi", ["Tüm Bölgeler", "3. Bölge (Hücum)", "Orta Saha"])

# --- GAUGE GRAFİKLERİ (PPDA & INTENSITY) ---
col_g1, col_g2 = st.columns(2)

def create_gauge(value, title, max_val, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 20, 'color': 'white'}},
        number = {'font': {'size': 40, 'color': 'white', 'family': 'JetBrains Mono'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, max_val], 'color': "rgba(15, 23, 42, 0.5)"}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': value}}))
    
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Inter"}, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

with col_g1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(create_gauge(6.4, "PPDA (Press Intensity)", 20, "#00e5ff"), use_container_width=True)
    st.caption("Düşük değer = Daha yoğun pres (Lider: 5.8)")
    st.markdown('</div>', unsafe_allow_html=True)

with col_g2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(create_gauge(7.2, "Challenge Intensity", 10, "#ef4444"), use_container_width=True)
    st.caption("Dakika başına düşen defansif aksiyon (Düello, Top Kapma)")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TABLO: HIGH REGAIN LEADERS ---
st.markdown("### 🏆 TOP KAPMA LİDERLERİ (High Regains)")

# Pandas ile şık bir tablo oluşturalım
data = {
    "Rank": ["01", "02", "03", "04"],
    "Player": ["Declan Rice", "Martin Ødegaard", "Gabriel Jesus", "William Saliba"],
    "Pos": ["DM", "CM", "FW", "CB"],
    "Total Regains": [34, 29, 22, 18],
    "Per 90": [1.8, 1.4, 1.1, 0.9]
}
df = pd.read_json(pd.DataFrame(data).to_json()) # Basit trick

# Tabloyu özelleştir
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.TextColumn("Rank", width="small"),
        "Player": st.column_config.TextColumn("Player", width="large"),
        "Total Regains": st.column_config.ProgressColumn(
            "Total Regains",
            format="%d",
            min_value=0,
            max_value=40,
        ),
        "Per 90": st.column_config.NumberColumn("Per 90", format="%.1f")
    }
)
