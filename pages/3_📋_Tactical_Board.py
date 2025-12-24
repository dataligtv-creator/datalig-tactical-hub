import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- CSS TASARIM ---
st.markdown("""
<style>
    .tactic-board {
        background-color: #1e293b;
        border: 2px solid rgba(0,229,255,0.2);
        border-radius: 12px;
        position: relative;
        height: 600px;
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
        background-image: radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 40px 40px;
        box-shadow: 0 0 30px rgba(0,0,0,0.5);
        overflow: hidden;
    }
    .player-dot {
        width: 35px; height: 35px;
        background: #00e5ff;
        border: 2px solid white;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 12px; color: black;
        position: absolute;
        box-shadow: 0 0 15px #00e5ff;
        cursor: pointer;
        transform: translate(-50%, 50%);
        z-index: 10;
    }
    .ball {
        position: absolute; font-size: 24px;
        transform: translate(-50%, -50%);
    }
    .line { position: absolute; background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# --- SAYFA DÜZENİ ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Taktik Tahtası")
    
    # HTML KODLARI GÜVENLİ ALANDA
    st.markdown("""
    <div class="tactic-board">
        <div class="line" style="top: 50%; left: 0; right: 0; height: 2px;"></div>
        <div class="line" style="top: 50%; left: 50%; width: 100px; height: 100px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.2); transform: translate(-50%, -50%); background: transparent;"></div>
        
        <div class="player-dot" style="bottom: 5%; left: 50%;">GK</div>
        <div class="player-dot" style="bottom: 20%; left: 15%;">LB</div>
        <div class="player-dot" style="bottom: 20%; left: 38%;">LCB</div>
        <div class="player-dot" style="bottom: 20%; left: 62%;">RCB</div>
        <div class="player-dot" style="bottom: 20%; left: 85%;">RB</div>
        <div class="player-dot" style="bottom: 35%; left: 50%;">DM</div>
        <div class="player-dot" style="bottom: 45%; left: 30%;">LCM</div>
        <div class="player-dot" style="bottom: 45%; left: 70%;">RCM</div>
        <div class="player-dot" style="bottom: 65%; left: 15%;">LW</div>
        <div class="player-dot" style="bottom: 70%; left: 50%;">ST</div>
        <div class="player-dot" style="bottom: 65%; left: 85%;">RW</div>
        
        <div class="ball" style="bottom: 55%; left: 60%;">⚽</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("⚙️ Ayarlar")
    formasyon = st.selectbox("Diziliş", ["4-3-3", "4-4-2", "3-5-2"])
    notlar = st.text_area("Maç Notları", "Sol kanattan bindirme yapılacak.")
    st.button("Kaydet")
