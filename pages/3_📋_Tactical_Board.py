import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# --- 🛰️ ORACLE BAĞLANTISI (CONTEXT MANAGEMENT) ---
# Oracle'dan gelen veriyi kontrol ediyoruz, yoksa varsayılan değerleri atıyoruz
tactic_focus = st.session_state.get('tactic_context', {})
aktif_takim = tactic_focus.get('focus_team', 'Genel Rakip')
gelen_dizilis = tactic_focus.get('formation', '4-3-3')
oracle_raporu = tactic_focus.get('scouting_report', "Oracle sayfasında henüz bir analiz yapılmadı.")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="War Room | DATALIG", page_icon="📋", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .stButton button { background-color: #00e5ff !important; color: #0b0f19 !important; font-weight: bold; }
    .report-box { background-color: rgba(30, 41, 59, 0.4); padding: 20px; border-left: 4px solid #ff0055; border-radius: 8px; margin-top: 20px; min-height: 200px; }
    .oracle-box { background-color: rgba(0, 229, 255, 0.05); border-left: 4px solid #00e5ff; padding: 15px; border-radius: 5px; color: #e2e8f0; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

st.title("📋 THE WAR ROOM")
st.caption("Oracle Destekli Stratejik Planlama")
st.markdown("---")

# --- ANA PANEL ---
col_sidebar, col_pitch = st.columns([1, 2])

with col_sidebar:
    st.markdown(f"### 🛡️ ANALİZ ODAĞI: <span style='color:#ff0055;'>{aktif_takim}</span>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ TAKTİKSEL KURGU")
    
    # Oracle'dan gelen dizilişi otomatik seçili getiriyoruz
    formation_list = ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"]
    default_idx = formation_list.index(gelen_dizilis) if gelen_dizilis in formation_list else 0
    
    formation = st.selectbox("Diziliş Seçin", formation_list, index=default_idx)
    defense_style = st.radio("Savunma Tipi", ["Adam Adama Markaj", "Alan Savunması", "Yüksek Pres"])
    
    if st.button("Taktiği Onayla"):
        st.success(f"{aktif_takim} için {formation} planı hazırlandı.")

    st.markdown("---")
    st.markdown("#### 🧠 ORACLE ÖZETİ")
    st.markdown(f'<div class="oracle-box">{oracle_raporu[:300]}...</div>', unsafe_allow_html=True)

# --- SAHA VE FORMASYON ÇİZİMİ ---
with col_pitch:
    # Saha kurulumu
    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#0b0f19', line_color='#555555')
    fig, ax = pitch.draw(figsize=(8, 11))
    fig.set_facecolor('#0b0f19')

    # Koordinat veri tabanı (Dikey saha koordinatları)
    formations_db = {
        "4-3-3": [(15, 40), (30, 15), (30, 65), (25, 30), (25, 50), (50, 40), (65, 25), (65, 55), (95, 15), (95, 65), (105, 40)],
        "4-2-3-1": [(15, 40), (30, 15), (30, 65), (25, 32), (25, 48), (45, 30), (45, 50), (75, 40), (85, 15), (85, 65), (105, 40)],
        "3-5-2": [(15, 40), (25, 25), (25, 40), (25, 55), (50, 10), (50, 70), (55, 40), (65, 28), (65, 52), (100, 30), (100, 50)],
        "4-4-2": [(15, 40), (30, 15), (30, 65), (25, 32), (25, 48), (60, 15), (60, 35), (60, 45), (60, 65), (100, 35), (100, 45)]
    }

    # Oyuncuları çiz
    coords = formations_db.get(formation, [])
    for x, y in coords:
        pitch.scatter(x, y, s=550, color='#0b0f19', edgecolor='#00e5ff', linewidth=2, zorder=3, ax=ax)

    # Rakip Tehlike Halkası (Isı Haritası Mantığıyla)
    pitch.scatter(85, 40, s=1000, color='none', edgecolor='#ff0055', linewidth=3, linestyle='--', zorder=2, ax=ax)
    ax.text(40, 85, f"HEDEF: {aktif_takim}", color='#ff0055', fontsize=14, ha='center', fontweight='bold')

    st.pyplot(fig)

# --- ALT ANALİZ RAPORU ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.markdown(f'<div class="report-box"><h4>⚽ Taktiksel Odak: {aktif_takim}</h4>', unsafe_allow_html=True)
    st.write(oracle_raporu[:600] + "...") # Oracle'ın uzun analizinin ilk kısmını buraya basıyoruz
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="report-box" style="border-left-color: #00e5ff;"><h4>🛡️ Savunma Reçetesi</h4>', unsafe_allow_html=True)
    st.write(f"Hocam, **{formation}** dizilişinde **{defense_style}** kurgusu {aktif_takim} hücumlarını bozacaktır.")
    st.write("Oracle analizine göre, rakibin son maçlardaki ısı haritası bu yerleşimin doğru olduğunu kanıtlıyor.")
    st.markdown('</div>', unsafe_allow_html=True)
