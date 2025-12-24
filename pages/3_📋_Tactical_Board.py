
import streamlit as st

st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root { --primary: #00e5ff; --bg: #0b0f19; }
    .stApp { background-color: var(--bg); font-family: 'Inter', sans-serif; }
    .tactic-board {
        background-color: #1e293b;
        border: 2px solid rgba(0,229,255,0.2);
        border-radius: 12px;
        padding: 20px;
        position: relative;
        height: 500px;
        background-image: radial-gradient(rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 20px 20px;
    }
    .player-dot {
        width: 30px; height: 30px; background: #00e5ff; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: bold; color: black; position: absolute;
        box-shadow: 0 0 10px #00e5ff; cursor: pointer;
    }
    .player-dot.away { background: #ef4444; box-shadow: 0 0 10px #ef4444; color: white; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 Interactive Tactical Board")
    
    # Basit bir HTML Saha Simülasyonu
    # (Normalde burası canvas ile çizilir ama hızlı çözüm için HTML/CSS)
    st.markdown("""
    <div class="tactic-board">
        <div style="position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: rgba(255,255,255,0.2);"></div>
        <div style="position: absolute; top: 50%; left: 50%; width: 100px; height: 100px; border: 1px solid rgba(255,255,255,0.2); border-radius: 50%; transform: translate(-50%, -50%);"></div>
        
        <div class="player-dot" style="bottom: 10%; left: 50%;">GK</div>
        <div class="player-dot" style="bottom: 25%; left: 20%;">LB</div>
        <div class="player-dot" style="bottom: 25%; left: 40%;">CB</div>
        <div class="player-dot" style="bottom: 25%; left: 60%;">CB</div>
        <div class="player-dot" style="bottom: 25%; left: 80%;">RB</div>
        
        <div class="player-dot" style="bottom: 45%; left: 30%;">CM</div>
        <div class="player-dot" style="bottom: 40%; left: 50%;">DM</div>
        <div class="player-dot" style="bottom: 45%; left: 70%;">CM</div>
        
        <div class="player-dot" style="bottom: 65%; left: 20%;">LW</div>
        <div class="player-dot" style="bottom: 70%; left: 50%;">ST</div>
        <div class="player-dot" style="bottom: 65%; left: 80%;">RW</div>

        <div style="position: absolute; top: 60%; left: 60%; font-size: 20px;">⚽</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("⚙️ Settings")
    formation = st.selectbox("Formation", ["4-3-3", "4-2-3-1", "3-5-2"])
    style = st.selectbox("Play Style", ["Possession", "Counter Attack", "Gegenpress"])
    
    st.markdown("### 📝 Notes")
    st.text_area("Coach Notes", "Rakip sol beki zayıf, kanatlardan yüklenelim.", height=200)
    
    st.button("💾 Save Tactic")
