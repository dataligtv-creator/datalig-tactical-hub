import streamlit as st
import streamlit.components.v1 as components

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- 2. KOORDİNAT SİSTEMİ ---
FORMATIONS = {
    "4-3-3": [
        {"l": "GK", "x": 5, "y": 50},
        {"l": "LB", "x": 20, "y": 15}, {"l": "LCB", "x": 18, "y": 38}, {"l": "RCB", "x": 18, "y": 62}, {"l": "RB", "x": 20, "y": 85},
        {"l": "DM", "x": 35, "y": 50}, {"l": "LCM", "x": 45, "y": 30}, {"l": "RCM", "x": 45, "y": 70},
        {"l": "LW", "x": 75, "y": 15}, {"l": "ST", "x": 80, "y": 50}, {"l": "RW", "x": 75, "y": 85},
    ],
    "4-4-2": [
        {"l": "GK", "x": 5, "y": 50},
        {"l": "LB", "x": 20, "y": 15}, {"l": "LCB", "x": 18, "y": 38}, {"l": "RCB", "x": 18, "y": 62}, {"l": "RB", "x": 20, "y": 85},
        {"l": "LM", "x": 45, "y": 10}, {"l": "LCM", "x": 45, "y": 40}, {"l": "RCM", "x": 45, "y": 60}, {"l": "RM", "x": 45, "y": 90},
        {"l": "LST", "x": 75, "y": 40}, {"l": "RST", "x": 75, "y": 60},
    ],
    "4-2-3-1": [
        {"l": "GK", "x": 5, "y": 50},
        {"l": "LB", "x": 20, "y": 15}, {"l": "LCB", "x": 18, "y": 38}, {"l": "RCB", "x": 18, "y": 62}, {"l": "RB", "x": 20, "y": 85},
        {"l": "LDM", "x": 35, "y": 40}, {"l": "RDM", "x": 35, "y": 60},
        {"l": "LAM", "x": 60, "y": 20}, {"l": "CAM", "x": 60, "y": 50}, {"l": "RAM", "x": 60, "y": 80},
        {"l": "ST", "x": 80, "y": 50},
    ],
    "3-5-2": [
        {"l": "GK", "x": 5, "y": 50},
        {"l": "LCB", "x": 20, "y": 30}, {"l": "CB", "x": 18, "y": 50}, {"l": "RCB", "x": 20, "y": 70},
        {"l": "LWB", "x": 40, "y": 10}, {"l": "LCM", "x": 45, "y": 40}, {"l": "RCM", "x": 45, "y": 60}, {"l": "RWB", "x": 40, "y": 90},
        {"l": "AM", "x": 55, "y": 50},
        {"l": "LST", "x": 75, "y": 40}, {"l": "RST", "x": 75, "y": 60},
    ]
}

# --- 3. NEON TASARIM KODLARI (CSS) ---
# Burası o "Paint" görüntüsünü yok edip "Cyberpunk" havası veren yer.
NEON_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');

    body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'JetBrains Mono', monospace; }

    /* SAHA KUTUSU VE ZEMİNİ */
    .field-wrapper {
        width: 100%; height: 600px;
        display: flex; justify-content: center; align-items: center;
        background: transparent;
    }

    .tactical-field {
        position: relative;
        width: 95%; height: 550px;
        background-color: #0b0f19;
        /* Modern Grid Dokusu + Radyal Işık */
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(0, 229, 255, 0.1) 0%, transparent 60%),
            linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.8), inset 0 0 100px rgba(0,0,0,0.5);
    }

    /* ÇİZGİLER İÇİN ORTAK AYAR (NEON GLOW) */
    .line { 
        position: absolute; 
        border: 2px solid rgba(255, 255, 255, 0.6); 
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.2); /* Parlama Efekti */
        box-sizing: border-box; 
    }
    
    /* DIŞ ÇİZGİLER */
    .touch-line { top: 25px; bottom: 25px; left: 40px; right: 40px; border: 2px solid rgba(255, 255, 255, 0.8); }
    
    /* ORTA SAHA */
    .mid-line { top: 25px; bottom: 25px; left: 50%; width: 0; border-left: 2px solid rgba(255, 255, 255, 0.4); }
    .center-circle { 
        top: 50%; left: 50%; width: 110px; height: 110px; 
        border-radius: 50%; transform: translate(-50%, -50%); 
    }
    .center-spot {
        position: absolute; top: 50%; left: 50%; width: 8px; height: 8px; 
        background: white; border-radius: 50%; transform: translate(-50%, -50%);
        box-shadow: 0 0 10px white;
    }

    /* SOL KALE ALANI */
    .penalty-box-left { top: 50%; left: 40px; width: 140px; height: 280px; transform: translateY(-50%); border-left: none; background: rgba(255,255,255,0.03); }
    .six-yard-left { top: 50%; left: 40px; width: 50px; height: 110px; transform: translateY(-50%); border-left: none; }
    .penalty-arc-left { 
        position: absolute; top: 50%; left: 180px; width: 50px; height: 80px; 
        border: 2px solid rgba(255,255,255,0.6); border-radius: 0 50% 50% 0; border-left: none; transform: translateY(-50%);
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
    }
    .penalty-spot-left { position: absolute; top: 50%; left: 150px; width: 5px; height: 5px; background: white; border-radius: 50%; transform: translateY(-50%); box-shadow: 0 0 5px white; }

    /* SAĞ KALE ALANI */
    .penalty-box-right { top: 50%; right: 40px; width: 140px; height: 280px; transform: translateY(-50%); border-right: none; background: rgba(255,255,255,0.03); }
    .six-yard-right { top: 50%; right: 40px; width: 50px; height: 110px; transform: translateY(-50%); border-right: none; }
    .penalty-arc-right { 
        position: absolute; top: 50%; right: 180px; width: 50px; height: 80px; 
        border: 2px solid rgba(255,255,255,0.6); border-radius: 50% 0 0 50%; border-right: none; transform: translateY(-50%);
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
    }
    .penalty-spot-right { position: absolute; top: 50%; right: 150px; width: 5px; height: 5px; background: white; border-radius: 50%; transform: translateY(-50%); box-shadow: 0 0 5px white; }

    /* KÖŞE YAYLARI (CORNER ARCS) */
    .corner { position: absolute; width: 25px; height: 25px; border: 2px solid rgba(255,255,255,0.6); box-shadow: 0 0 5px rgba(255,255,255,0.2); }
    .corner-tl { top: 25px; left: 40px; border-radius: 0 0 100% 0; border-top: none; border-left: none; }
    .corner-tr { top: 25px; right: 40px; border-radius: 0 0 0 100%; border-top: none; border-right: none; }
    .corner-bl { bottom: 25px; left: 40px; border-radius: 0 100% 0 0; border-bottom: none; border-left: none; }
    .corner-br { bottom: 25px; right: 40px; border-radius: 100% 0 0 0; border-bottom: none; border-right: none; }

    /* GERÇEK KALE DİREKLERİ (3D Görünüm) */
    .goal-post {
        position: absolute; top: 50%; width: 10px; height: 60px;
        background: rgba(0, 229, 255, 0.1);
        border: 2px solid #00e5ff;
        transform: translateY(-50%);
        box-shadow: 0 0 15px #00e5ff;
    }
    .goal-left { left: 30px; border-right: none; border-radius: 5px 0 0 5px; }
    .goal-right { right: 30px; border-left: none; border-radius: 0 5px 5px 0; }

    /* OYUNCULAR (NEON KARTLAR) */
    .player {
        position: absolute;
        width: 40px; height: 40px;
        background: #0b0f19;
        color: #00e5ff;
        border: 2px solid #00e5ff;
        border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        font-size: 11px; font-weight: 800;
        transform: translate(-50%, -50%);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.5); /* Güçlü Neon */
        z-index: 10;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        cursor: grab;
    }
    .player:hover {
        transform: translate(-50%, -50%) scale(1.2);
        background: #00e5ff; color: #000;
        z-index: 20;
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.9);
    }

    /* TOP ANIMASYONU */
    .ball { 
        position: absolute; font-size: 24px; top: 50%; left: 50%; 
        transform: translate(-50%, -50%); 
        animation: bounce 2s infinite; 
        filter: drop-shadow(0 0 10px white);
        z-index: 5;
    }
    @keyframes bounce { 0%, 100% { transform: translate(-50%, -50%) scale(1); } 50% { transform: translate(-50%, -50%) scale(1.2); } }
</style>
"""

# --- 4. RENDER FONKSİYONU ---
def render_neon_board(formation_name):
    players = FORMATIONS.get(formation_name, FORMATIONS["4-3-3"])
    
    # Oyuncu HTML'ini oluştur
    players_html = ""
    for p in players:
        players_html += '<div class="player" style="left: ' + str(p["x"]) + '%; top: ' + str(p["y"]) + '%;">' + p["l"] + '</div>'

    # HTML GÖVDESİ (Parantez hatası olmaması için String toplama)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>""" + NEON_CSS + """</head>
    <body>
        <div class="field-wrapper">
            <div class="tactical-field">
                <div class="line touch-line"></div>
                <div class="line mid-line"></div>
                <div class="line center-circle"></div>
                <div class="center-spot"></div>

                <div class="line penalty-box-left"></div>
                <div class="line six-yard-left"></div>
                <div class="penalty-arc-left"></div>
                <div class="penalty-spot-left"></div>
                <div class="goal-post goal-left"></div>

                <div class="line penalty-box-right"></div>
                <div class="line six-yard-right"></div>
                <div class="penalty-arc-right"></div>
                <div class="penalty-spot-right"></div>
                <div class="goal-post goal-right"></div>

                <div class="corner corner-tl"></div>
                <div class="corner corner-tr"></div>
                <div class="corner corner-bl"></div>
                <div class="corner corner-br"></div>

                """ + players_html + """
                
                <div class="ball">⚽</div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# --- 5. ARAYÜZ ---
col_board, col_panel = st.columns([3, 1])

with col_panel:
    st.markdown("### ⚙️ TAKTİK MERKEZİ")
    formation = st.selectbox("Formasyon", list(FORMATIONS.keys()))
    tactic = st.selectbox("Oyun Stili", ["Possession", "Gegenpressing", "Counter", "Park the Bus"])
    
    st.markdown("---")
    
    # Bilgi Paneli (Hatasız Metric)
    st.metric(label="SİSTEM", value=formation, delta=tactic)
    
    with st.expander("📝 Teknik Notlar", expanded=True):
        st.text_area("Not", "Bekleri ileri çıkar.", height=100)
        if st.button("💾 Kaydet", use_container_width=True):
            st.toast("Kaydedildi!", icon="✅")

with col_board:
    components.html(render_neon_board(formation), height=620, scrolling=False)
