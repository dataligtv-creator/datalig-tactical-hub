import streamlit as st

st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- CSS (TASARIM) ---
st.markdown("""
<style>
    /* Yazı Tipleri */
    @import url('[https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap)');
    
    :root { --primary: #00e5ff; --bg: #0b0f19; }
    
    .stApp { 
        background-color: var(--bg); 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Saha Tasarımı */
    .tactic-board {
        background-color: #1e293b;
        border: 2px solid rgba(0,229,255,0.2);
        border-radius: 12px;
        padding: 0;
        position: relative;
        height: 600px; /* Sabit yükseklik */
        width: 100%;
        max-width: 400px; /* Dikey saha genişliği */
        margin: 0 auto; /* Ortala */
        background-image: 
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 40px 40px;
        box-shadow: 0 0 30px rgba(0,0,0,0.5);
        overflow: hidden;
    }

    /* Orta Saha Çizgisi */
    .midfield-line {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background: rgba(255,255,255,0.1);
    }
    
    /* Orta Yuvarlak */
    .center-circle {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100px;
        height: 100px;
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 50%;
        transform: translate(-50%, -50%);
    }

    /* Ceza Sahaları */
    .box-top {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 15%;
        border: 2px solid rgba(255,255,255,0.1);
        border-top: none;
    }
    
    .box-bottom {
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 15%;
        border: 2px solid rgba(255,255,255,0.1);
        border-bottom: none;
    }

    /* Oyuncu Noktaları */
    .player-dot {
        width: 35px; 
        height: 35px; 
        background: #00e5ff; /* Neon Mavi */
        border: 2px solid rgba(255,255,255,0.8);
        border-radius: 50%;
        display: flex; 
        align-items: center; 
        justify-content: center;
        font-weight: bold; 
        font-size: 12px;
        font-family: 'JetBrains Mono';
        color: #0b0f19; 
        position: absolute;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.6); 
        cursor: pointer;
        transform: translate(-50%, 50%); /* Merkezleme */
        z-index: 10;
        transition: transform 0.2s;
    }
    
    .player-dot:hover {
        transform: translate(-50%, 50%) scale(1.2);
        z-index: 20;
    }

    /* Top */
    .ball {
        position: absolute;
        font-size: 24px;
        transform: translate(-50%, -50%);
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-50%, -50%) scale(1.2); }
    }
</style>
""", unsafe_allow_html=True)

# --- SAYFA DÜZENİ ---
col_board, col_settings = st.columns([1, 1])

with col_board:
    st.markdown('<h3 style="text-align: center; color: white;">📋 TAKTİK TAHTASI</h3>', unsafe_allow_html=True)
    
    # HTML SAHA SİMÜLASYONU
    st.markdown("""
    <div class="tactic-board">
        <div class="midfield-line"></div>
        <div class="center-circle"></div>
        <div class="box-top"></div>
        <div class="box-bottom"></div>
        
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

with col_settings:
    st.markdown("### ⚙️ AYARLAR & ANALİZ")
    
    with st.expander("🛠️ Diziliş Ayarları", expanded=True):
        formation = st.selectbox("Diziliş Seç", ["4-3-3 (Attack)", "4-2-3-1", "3-5-2", "4-4-2 Diamond"])
        style = st.selectbox("Oyun Stili", ["Topa Sahip Olma (Possession)", "Gegenpressing", "Kontra Atak", "Otobüsü Çek"])
        intensity = st.slider("Pres Şiddeti", 0, 100, 85)
    
    with st.container():
        st.markdown("### 📝 Teknik Direktör Notları")
        st.text_area("Maç Notları", "Rakip savunma arkasına atılan toplarda zayıf. Bekleri çok öne çıkıyor, kanat forvetleri (LW/RW) çizgiye basarak oynat.", height=150)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.button("💾 Taktikleri Kaydet", use_container_width=True)
        with col_b2:
            st.button("📤 PDF Olarak İndir", use_container_width=True)

    # Mini Analiz Paneli
    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
        <h4 style="color: #00e5ff; margin: 0; font-size: 14px;">🤖 AI ASİSTAN ANALİZİ</h4>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 5px;">
            "Hocam, 4-3-3 dizilişinde <b>LCM</b> ve <b>LW</b> arasındaki bağlantı kopuk görünüyor. 
            Sol iç koridoru (Half-space) kullanmak için LCM'i biraz daha ileri itebiliriz."
        </p>
    </div>
    """, unsafe_allow_html=True)
