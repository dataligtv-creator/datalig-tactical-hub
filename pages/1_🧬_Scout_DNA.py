import streamlit as st
import pandas as pd
import plotly.express as px

# --- 🛰️ ORACLE BAĞLANTISI (CONTEXT) ---
tactic_context = st.session_state.get('tactic_context', {})
focus_team = tactic_context.get('focus_team', 'Genel')
focus_formation = tactic_context.get('formation', '4-3-3')
oracle_report = tactic_context.get('scouting_report', "")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Scout DNA | DATALIG", page_icon="🧬", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .scout-card { background: rgba(30, 41, 59, 0.5); border: 1px solid #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 10px; }
    .highlight-text { color: #00e5ff; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🧬 SCOUT DNA")
st.caption("Veri Odaklı Oyuncu Seçimi ve Taktiksel Uyum")
st.markdown("---")

# --- 🎯 AKILLI FİLTRELEME PANELİ ---
with st.sidebar:
    st.markdown(f"### 🎯 MEVCUT ODAK")
    st.info(f"**Takım:** {focus_team}\n\n**Diziliş:** {focus_formation}")
    
    st.markdown("### 🔍 ÖZEL FİLTRELER")
    age_range = st.slider("Yaş Aralığı", 16, 38, (18, 28))
    market_value = st.slider("Piyasa Değeri (M€)", 0, 150, (0, 30))
    
    if st.button("Filtreleri Sıfırla"):
        st.rerun()

# --- 🤖 ORACLE'DAN GELEN TALİMAT ---
if focus_team != "Genel":
    st.markdown(f"""
    <div class="scout-card" style="border-left: 5px solid #00e5ff;">
        <h4>🧠 Oracle Analiz Notları (Otomatik)</h4>
        <p>{oracle_report[:400]}...</p>
    </div>
    """, unsafe_allow_html=True)

# --- 📊 OYUNCU LİSTESİ VE KARŞILAŞTIRMA ---
col1, col2 = st.columns([1, 1])

# Örnek Veri Seti (Gerçek yapında bunu Pandas veya Pinecone'dan çekeceğiz)
data = {
    "Oyuncu": ["Archie Brown", "Filip Kostić", "Levent Mercan", "Oosterwolde"],
    "Yaş": [23, 33, 24, 24],
    "Hız": [92, 84, 86, 94],
    "Defans": [78, 72, 75, 85],
    "Hücum": [85, 89, 79, 74],
    "Taktik Uyum (%)": [92, 88, 76, 95]
}
df = pd.DataFrame(data)

# Eğer Archie Brown konuşuluyorsa onu listenin başına al veya vurgula
with col1:
    st.markdown(f"### 📋 {focus_team} İçin Önerilen Listesi")
    
    # Oracle'da geçen oyuncuları filtreleme mantığı
    search_term = ""
    if "Archie Brown" in oracle_report:
        search_term = "Archie Brown"
        st.success(f"💡 Oracle: **{search_term}** profili {focus_formation} için %92 uyumlu!")

    # Tablo Görünümü
    st.dataframe(df.style.background_gradient(subset=['Taktik Uyum (%)'], cmap='Blues'), use_container_width=True)

with col2:
    st.markdown("### 📈 Performans Karşılaştırması")
    fig = px.bar(df, x="Oyuncu", y="Taktik Uyum (%)", color="Hız", 
                 title=f"{focus_formation} Sistemine Uyum Skorları",
                 color_continuous_scale='Bluered_r')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

# --- 🛡️ DETAYLI RADAR ANALİZİ ---
st.markdown("---")
st.markdown("### 🕸️ Oyuncu DNA Profili")
selected_player = st.selectbox("Analiz edilecek oyuncuyu seçin", df["Oyuncu"])

player_stats = df[df["Oyuncu"] == selected_player].iloc[0]
radar_data = pd.DataFrame(dict(
    r=[player_stats['Hız'], player_stats['Defans'], player_stats['Hücum'], player_stats['Taktik Uyum (%)'], 80],
    theta=['Hız', 'Savunma', 'Hücum', 'Uyum', 'Pas']
))

fig_radar = px.line_polar(radar_data, r='r', theta='theta', line_close=True, range_r=[0,100])
fig_radar.update_traces(fill='toself', line_color='#00e5ff')
fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
st.plotly_chart(fig_radar, use_container_width=True)
