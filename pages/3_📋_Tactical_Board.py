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

# --- 3. HTML PARÇALARI (CSS) ---
CSS_CODE = """
<style>
    body { background-color: transparent; color: white; margin: 0; overflow: hidden; font-family: sans-serif; }
    .tactical-bg {
        background-color: #0b0f19;
        background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        position: absolute; width: 100%; height: 100%;
    }
    .field-border {
        position: absolute; top: 20px; bottom: 20px; left: 20px; right: 20px;
        border: 2px solid rgba(255,255,255,0.2); border-radius: 4px; pointer-events: none;
    }
    .mid-line { position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: rgba(255,255,255,0.2); }
    .center-circle {
        position: absolute; top: 50%; left: 50%; width: 100px; height: 100px;
        border: 2px solid rgba(255,255,255,0.2); border-radius: 50%; transform: translate(-50%, -50%);
    }
    .box-left { position: absolute; top: 50%; left: 0; width: 120px; height: 250px; border-right: 2px solid rgba(255,255,255,0.2); border-top: 2px solid rgba(255,255,255,0.2); border-bottom: 2px solid rgba(255,255,255,0.2); transform: translateY(-50%); }
    .box-right { position: absolute; top: 50%; right: 0; width: 120px; height: 250px; border-left: 2px solid rgba(255,255,255,0.2); border-top: 2px solid rgba(255,255,255,0.2); border-bottom: 2px solid rgba(255,255,255,0.2); transform: translateY(-50%); }
    
    .player-dot {
        width: 32px; height: 32px; background: #0b0f19; border: 2px solid #00e5ff; color: #00e5ff;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: bold; font-size: 11px; position: absolute;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.3); z-index: 10;
        transform: translate(-50%, -50%); transition: all 0.5s ease; cursor: pointer;
    }
    .player-dot:hover { transform: translate(-50%, -50%) scale(1.2); background: #00e5ff; color: #000; z-index: 20; }
    .ball { position: absolute; font-size: 20px; transform: translate(-50%, -50%); animation: bounce 2s infinite; }
    @keyframes bounce { 0%, 100% { transform: translate(-50%, -50%) scale(1); } 50% { transform: translate(-50%, -50%) scale(1.2); } }
</style>
"""

FIELD_HTML = """
<div class="tactical-bg"></div>
<div class="field-border">
    <div class="mid-line"></div>
    <div class="center-circle"></div>
    <div class="box-left"></div>
    <div class="box-right"></div>
</div>
"""

# --- 4. HTML OLUŞTURUCU FONKSİYON ---
def get_final_html(formation_name):
    players = FORMATIONS.get(formation_name, FORMATIONS["4-3-
