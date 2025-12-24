import streamlit as st
import streamlit.components.v1 as components

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# 2. DİZİLİŞ VERİLERİ
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

# 3. HTML OLUŞTURUCU (Hata Riskini Önlemek İçin Basitleştirildi)
def create_board(formation_name):
    # Oyuncu HTML'ini oluştur
    players = FORMATIONS.get(formation_name, FORMATIONS["4-3-3"])
    players_divs = ""
    for p in players:
        players_divs += f'<div class="player-dot" style="left: {p["x"]}%; top: {p["y"]}%;">{p["l"]}</div>'

    # Tek parça HTML String (Parantez hatası olmaması için)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; overflow: hidden; background: transparent; }}
        .tactical-bg {{
            width: 100%; height: 600px; position: relative;
            background-color: #0b0f19;
            background-image: linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), 
                              linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 40px 40px;
            border-radius: 12px; border: 1px solid #333;
        }}
        .field-lines {{
            position: absolute; top: 20px; bottom: 20px; left: 20px; right: 20px;
            border: 2px solid rgba(255,255,255,0.2); pointer-events: none;
        }}
        .mid-line {{ position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: rgba(255,255,255,0.2); }}
        .center-circle {{ 
            position: absolute; top: 50%; left: 50%; width: 100px; height: 100px; 
            border: 2px solid rgba(255,255,255,0.2); border-radius: 50%; transform: translate(-50%, -50%); 
        }}
        .player-dot {{
            width: 32px; height: 32px; background: #0b0f19; border: 2px solid #00e5ff; color: #00e5ff;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 11px; position: absolute;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.3); z-index: 10;
            transform: translate(-50%, -50%); transition: all 0.5s ease; cursor: pointer;
        }}
        .player-dot:hover {{ transform: translate(-50%, -50%) scale(1.2); background: #00e5ff; color: #000; z-index: 20; }}
        .ball {{ position: absolute; font-size: 20px; transform: translate(-50%, -50%); top: 55%; left: 55%; }}
    </style>
    </head>
    <body>
        <div class="tactical-bg">
            <div class="field-lines">
                <div class="mid-line"></div>
                <div class="center-circle"></div>
            </div>
            {players_divs}
            <div class="ball">⚽</div>
        </div>
    </body>
    </html>
    """
    return html

# 4. EKRAN DÜZENİ
col_board, col_panel = st.columns([3, 1])

with col_panel:
    st.markdown("### ⚙️ TEKNİK HEYET")
    selected_formation = st.selectbox("Diziliş", list(FORMATIONS.keys()))
    mentalite = st.selectbox("Mentalite", ["Possession", "Counter Attack", "Gegenpressing"])
    
    st.markdown("---")
    
    # NEON TABELA (HTML KULLANARAK)
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.5); border-left: 4px solid #00e5ff; padding: 15px; border-radius: 0 10px 10px 0;">
        <div style="color:#94a3b8; font-size:10px;">AKTİF SİSTEM</div>
        <div style="color:white; font-size:24px; font-weight:bold;">{selected_formation}</div>
        <div style="color:#00e5ff; font-size:12px;">{mentalite}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Notlar", expanded=True):
        st.text_area("Not", "Bekleri ileri çıkar.", height=80)
        st.button("Kaydet", use_container_width=True)

with col_board:
    # HTML'i çiziyoruz
    components.html(create_board(selected_formation), height=620)

# --- KOD SONU ---
