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

# --- 3. CSS (PRO TASARIM) ---
# Buradaki CSS kodları sahaya "Derinlik" ve "Neon" havası katar.
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');

    body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'JetBrains Mono', monospace; }

    /* SAHA KUTUSU */
    .field-wrapper {
        width: 100%; height: 600px;
        display: flex; justify-content: center; align-items: center;
        background: transparent;
    }

    .tactical-field {
        position: relative;
        width: 95%; height: 550px;
        background-color: #0f172a;
        /* Modern Grid Dokusu */
        background-image: 
            linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        box-shadow: 0 0 50px rgba(0, 0, 0, 0.8);
    }

    /* ÇİZGİLER ORTAK AYAR */
    .line { position: absolute; border: 2px solid rgba(255, 255, 255, 0.3); box-sizing: border-box; }
    
    /* DIŞ ÇİZGİLER (TAÇ) */
    .touch-line { top: 20px; bottom: 20px; left: 40px; right: 40px; border: 2px solid rgba(255, 255, 255, 0.5); }
    
    /* ORTA SAHA */
    .mid-line { top: 20px; bottom: 20px; left: 50%; width: 0; border-left: 2px solid rgba(255, 255, 255, 0.3); }
    .center-circle { 
        top: 50%; left: 50%; width: 100px; height: 100px; 
        border-radius: 50%; transform: translate(-50%, -50%); 
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    .center-spot {
        top: 50%; left: 50%; width: 6px; height: 6px; 
        background: white; border-radius: 50%; transform: translate(-50%, -50%);
        box-shadow: 0 0 10px white;
    }

    /* SOL KALE ALANI */
    .penalty-box-left { top: 50%; left: 40px; width: 130px; height: 260px; transform: translateY(-50%); border-left: none; background: rgba(255,255,255,0.02); }
    .six-yard-left { top: 50%; left: 40px; width: 50px; height: 100px; transform: translateY(-50%); border-left: none; }
    .penalty-arc-left { 
        top: 50%; left: 170px; width: 50px; height: 80px; 
        border-radius: 0 50% 50% 0; border-left: none; transform: translateY(-50%);
    }
    .penalty-spot-left { top: 50%; left: 140px; width: 4px; height: 4px; background: white; border-radius: 50%; transform: translateY(-50%); }

    /* GERÇEK SOL KALE DİREĞİ (DIŞARI TAŞAN) */
    .goal-left {
        position: absolute; top: 50%; left: 25px; width: 15px; height: 60px;
        border: 3px solid #00e5ff; border-right: none; 
        transform: translateY(-50%);
        box-shadow: -5px 0 15px rgba(0, 229, 255, 0.5);
        border-radius: 4px 0 0 4px;
    }

    /* SAĞ KALE ALANI */
    .penalty-box-right { top: 50%; right: 40px; width: 130px; height: 260px; transform: translateY(-50%); border-right: none; background: rgba(255,255,255,0.02); }
    .six-yard-right { top: 50%; right: 40px; width: 50px; height: 100px; transform: translateY(-50%); border-right: none; }
    .penalty-arc-right { 
        top: 50%; right: 170px; width: 50px; height: 80px; 
        border-radius: 50% 0 0 50%; border-right: none; transform: translateY(-50%);
    }
    .penalty-spot-right { top: 50%; right: 140px; width: 4px; height: 4px; background: white; border-radius: 50%; transform: translateY(-50%); }

    /* GERÇEK SAĞ KALE DİREĞİ (DIŞARI TAŞAN) */
    .goal-right {
        position: absolute; top: 50%; right: 25px; width: 15px; height: 60px;
        border: 3px solid #00e5ff; border-left: none; 
        transform: translateY(-50%);
        box-shadow: 5px 0 15px rgba(0, 229, 255, 0.5);
        border-radius: 0 4px 4px 0;
    }

    /* KÖŞE YAYLARI (CORNER ARCS) */
    .corner-tl { top: 20px; left: 40px; width: 20px; height: 20px; border-radius: 0 0 100% 0; border-top: none; border-left: none; }
    .corner-tr { top: 20px; right: 40px; width: 20px; height: 20px; border-radius: 0 0 0 100%; border-top: none; border-right: none; }
    .corner-bl { bottom: 20px; left: 40px; width: 20px; height: 20px; border-radius: 0 100% 0 0; border-bottom: none; border-left: none; }
    .corner-br { bottom: 20px; right: 40px; width: 20px; height: 20px; border-radius: 100% 0 0 0; border-bottom: none; border-right: none; }

    /* OYUNCU STİLİ (PARLAYAN) */
    .player {
        position: absolute;
        width: 34px; height: 34px;
        background: #0b0f19;
        color: #00e5ff;
        border: 2px solid #00e5ff;
        border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        font-size: 10px; font-weight: bold;
        transform: translate(-50%, -50%);
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        z-index: 10;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); /* Havalı geçiş animasyonu */
        cursor: grab;
    }
    .player:hover {
        transform: translate(-50%, -50%) scale(1.2);
        background: #00e5ff; color: #0b0f19;
        z-index: 20;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.8);
    }

    .ball { position: absolute; font-size: 20px; transform: translate(-50%, -50%); animation: bounce 2s infinite; z-index: 5; }
    @keyframes bounce { 0%, 100% { transform: translate(-50%, -50%) scale(1); } 50% { transform: translate(-50%, -50%) scale(1.2); } }

</style>
"""

# --- 4. HTML OLUŞTURUCU (MODÜLER) ---
def render_field(formation_name):
    players = FORMATIONS.get(formation_name, FORMATIONS["4-3-3"])
    
    # Oyuncu HTML'ini oluştur
    players_html = ""
    for p in players:
        # Oyuncu koordinatlarını ekle
        players_html += '<div class="player" style="left: ' + str(p["x"]) + '%; top: ' + str(p["y"]) + '%;">' + p["l"] + '</div>'

    # SAHA İSKELETİ
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>""" + CSS_STYLE + """</head>
    <body>
        <div class="field-wrapper">
            <div class="tactical-field">
                <div class="line touch-line"></div>
                <div class="line mid-line"></div>
                <div class="line center-circle"></div>
                <div class="center-spot"></div>

                <div class="line penalty-box-left"></div>
                <div class="line six-yard-left"></div>
                <div class="line penalty-arc-left"></div>
                <div class="penalty-spot-left"></div>
                <div class="goal-left"></div> <div class="line penalty-box-right"></div>
                <div class="line six-yard-right"></div>
                <div class="line penalty-arc-right"></div>
                <div class="penalty-spot-right"></div>
                <div class="goal-right"></div> <div class="line corner-tl"></div>
                <div class="line corner-tr"></div>
                <div class="line corner-bl"></div>
                <div class="line corner-br"></div>

                """ + players_html + """
                <div class="ball" style="top: 50%; left: 50%;">⚽</div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# --- 5. ARAYÜZ ---
col_board, col_panel = st.columns([3, 1])

with col_panel:
    st.markdown("### 🛠️ TAKTİK MERKEZİ")
    
    formation = st.selectbox("Formasyon", list(FORMATIONS.keys()))
    tactic = st.selectbox("Oyun Stili", ["Possession (Topa Sahip Olma)", "Gegenpressing", "Counter Attack", "Low Block"])
    
    st.markdown("---")
    
    # BİLGİ KARTI (Streamlit Metrikleri ile - Temiz ve Şık)
    st.metric(label="SEÇİLEN SİSTEM", value=formation, delta=tactic.split(" ")[0])
    
    with st.expander("📝 Teknik Direktör Notu", expanded=True):
        st.text_area("Notlar", "Rakip savunma arkasına sarku koşularını artır.", height=100)
        if st.button("💾 Varyasyonu Kaydet", use_container_width=True):
            st.toast("Taktik başarıyla kaydedildi.", icon="✅")

with col_board:
    # Sahayı Çiz
    components.html(render_field(formation), height=620, scrolling=False)
