import streamlit as st
import streamlit.components.v1 as components

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- 2. KOORDİNAT SİSTEMİ (Yatay Saha) ---
# x:0 (Sol Kale), x:100 (Sağ Kale)
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

# --- 3. GÖRSEL TASARIM (CSS) - AYRI TUTULDU ---
STYLE_CSS = """
<style>
    /* GENEL AYARLAR */
    body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'Courier New', monospace; }
    
    /* SAHA ZEMİNİ (NEON GRID) */
    .field-container {
        width: 100%; height: 600px;
        background-color: #0b0f19;
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
        position: relative;
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0,0,0,0.5);
        border: 1px solid #333;
    }

    /* SAHA ÇİZGİLERİ */
    .field-lines {
        position: absolute; top: 20px; bottom: 20px; left: 40px; right: 40px;
        border: 2px solid rgba(255,255,255,0.4);
        box-shadow: 0 0 10px rgba(255,255,255,0.1);
    }
    
    .mid-line { position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: rgba(255,255,255,0.4); }
    
    .center-circle {
        position: absolute; top: 50%; left: 50%; width: 120px; height: 120px;
        border: 2px solid rgba(255,255,255,0.4); border-radius: 50%;
        transform: translate(-50%, -50%);
    }
    
    .center-spot {
        position: absolute; top: 50%; left: 50%; width: 6px; height: 6px;
        background: white; border-radius: 50%; transform: translate(-50%, -50%);
    }

    /* SOL KALE BÖLGESİ */
    .penalty-area-left {
        position: absolute; top: 50%; left: 0; width: 15%; height: 60%;
        border-right: 2px solid rgba(255,255,255,0.4);
        border-top: 2px solid rgba(255,255,255,0.4);
        border-bottom: 2px solid rgba(255,255,255,0.4);
        transform: translateY(-50%);
        background: rgba(255,255,255,0.02);
    }
    .six-yard-left {
        position: absolute; top: 50%; left: 0; width: 5%; height: 30%;
        border-right: 2px solid rgba(255,255,255,0.4);
        border-top: 2px solid rgba(255,255,255,0.4);
        border-bottom: 2px solid rgba(255,255,255,0.4);
        transform: translateY(-50%);
    }
    .goal-post-left {
        position: absolute; top: 50%; left: -10px; width: 10px; height: 14%;
        border: 2px solid rgba(0, 229, 255, 0.8); border-right: none;
        transform: translateY(-50%);
        box-shadow: -5px 0 10px rgba(0, 229, 255, 0.4);
    }

    /* SAĞ KALE BÖLGESİ */
    .penalty-area-right {
        position: absolute; top: 50%; right: 0; width: 15%; height: 60%;
        border-left: 2px solid rgba(255,255,255,0.4);
        border-top: 2px solid rgba(255,255,255,0.4);
        border-bottom: 2px solid rgba(255,255,255,0.4);
        transform: translateY(-50%);
        background: rgba(255,255,255,0.02);
    }
    .six-yard-right {
        position: absolute; top: 50%; right: 0; width: 5%; height: 30%;
        border-left: 2px solid rgba(255,255,255,0.4);
        border-top: 2px solid rgba(255,255,255,0.4);
        border-bottom: 2px solid rgba(255,255,255,0.4);
        transform: translateY(-50%);
    }
    .goal-post-right {
        position: absolute; top: 50%; right: -10px; width: 10px; height: 14%;
        border: 2px solid rgba(0, 229, 255, 0.8); border-left: none;
        transform: translateY(-50%);
        box-shadow: 5px 0 10px rgba(0, 229, 255, 0.4);
    }

    /* OYUNCULAR */
    .player-dot {
        width: 36px; height: 36px;
        background: #0b0f19;
        border: 2px solid #00e5ff;
        color: #00e5ff;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 11px;
        position: absolute;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        z-index: 20;
        transform: translate(-50%, -50%);
        transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Yaylanma Efekti */
        cursor: pointer;
    }
    .player-dot:hover {
        transform: translate(-50%, -50%) scale(1.3);
        background: #00e5ff; color: #000;
        z-index: 30;
    }

    /* TOP VE BİLGİ */
    .ball { position: absolute; font-size: 24px; top: 50%; left: 50%; transform: translate(-50%, -50%); animation: bounce 2s infinite; }
    @keyframes bounce { 0%, 100% { transform: translate(-50%, -50%) scale(1); } 50% { transform: translate(-50%, -50%) scale(1.2); } }

    .info-tag {
        position: absolute; bottom: 15px; right: 20px;
        font-size: 10px; color: rgba(0, 229, 255, 0.6);
        letter-spacing: 2px;
    }
</style>
"""

# --- 4. HTML OLUŞTURUCU (MODÜLER YAPI) ---
def create_tactical_board(formation_name):
    # Oyuncuları Hazırla
    players = FORMATIONS.get(formation_name, FORMATIONS["4-3-3"])
    players_html = ""
    for p in players:
        # String birleştirme (Hatasız yöntem)
        players_html += '<div class="player-dot" style="left: ' + str(p["x"]) + '%; top: ' + str(p["y"]) + '%;">' + p["l"] + '</div>'

    # Nihai HTML Kodu (Tek Parça)
    final_html = """
    <!DOCTYPE html>
    <html>
    <head>""" + STYLE_CSS + """</head>
    <body>
        <div class="field-container">
            <div class="field-lines">
                <div class="mid-line"></div>
                <div class="center-circle"></div>
                <div class="center-spot"></div>
                
                <div class="penalty-area-left"></div>
                <div class="six-yard-left"></div>
                <div class="goal-post-left"></div> <div class="penalty-area-right"></div>
                <div class="six-yard-right"></div>
                <div class="goal-post-right"></div> </div>

            """ + players_html + """
            
            <div class="ball">⚽</div>
            
            <div class="info-tag">""" + formation_name + """ ACTIVE</div>
        </div>
    </body>
    </html>
    """
    return final_html

# --- 5. ARAYÜZ (LAYOUT) ---
col_board, col_panel = st.columns([3, 1])

with col_panel:
    st.markdown("### ⚙️ SAHA KENARI")
    
    # Seçimler
    selected_formation = st.selectbox("Diziliş", list(FORMATIONS.keys()))
    game_style = st.selectbox("Oyun Stili", ["Possession Game", "Gegenpressing", "Low Block Counter", "Wing Play"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # NEON BİLGİ KARTI (Streamlit Native - Hatasız)
    st.markdown(f"""
    <div style="
        background: rgba(30, 41, 59, 0.6); 
        border-left: 4px solid #00e5ff; 
        padding: 20px; 
        border-radius: 0 12px 12px 0;
        margin-bottom: 20px;
    ">
        <div style="color: #94a3b8; font-size: 10px; margin-bottom: 5px; letter-spacing: 1px;">AKTİF SİSTEM</div>
        <div style="color: white; font-size: 28px; font-weight: 900;">{selected_formation}</div>
        <div style="color: #00e5ff; font-size: 12px; margin-top: 5px;">★ {game_style}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 Teknik Notlar", expanded=True):
        st.text_area("Analiz", "Rakip savunma arkasına atılan toplarda zayıf.", height=100)
        if st.button("💾 Kaydet", use_container_width=True):
            st.toast("Taktik varyasyonu veritabanına işlendi!", icon="✅")

with col_board:
    # Render (Kaydırma çubuğu kapalı)
    components.html(create_tactical_board(selected_formation), height=620, scrolling=False)
