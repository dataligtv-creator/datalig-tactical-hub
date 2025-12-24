import streamlit as st
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- 1. KOORDİNAT SİSTEMİ ---
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
    ],
    "3-4-3": [
        {"l": "GK", "x": 5, "y": 50},
        {"l": "LCB", "x": 20, "y": 30}, {"l": "CB", "x": 18, "y": 50}, {"l": "RCB", "x": 20, "y": 70},
        {"l": "LM", "x": 45, "y": 15}, {"l": "LCM", "x": 40, "y": 40}, {"l": "RCM", "x": 40, "y": 60}, {"l": "RM", "x": 45, "y": 85},
        {"l": "LW", "x": 70, "y": 20}, {"l": "ST", "x": 75, "y": 50}, {"l": "RW", "x": 70, "y": 80},
    ]
}

# --- 2. HTML ŞABLONU (DEĞİŞKEN YOK - DÜZ METİN) ---
# Buradaki { } işaretleri Python'ı etkilemez çünkü f harfi koymadık.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: { extend: { colors: { primary: '#00e5ff', bgDark: '#0b0f19' }, fontFamily: { mono: ['JetBrains Mono', 'monospace'] } } }
        }
    </script>
    <style>
        body { background-color: transparent; color: white; overflow: hidden; }
        .tactical-bg {
            background-color: #0b0f19;
            background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
        }
        .player-dot {
            width: 32px; height: 32px; background: #0b0f19; border: 2px solid #00e5ff; color: #00e5ff;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 10px; font-family: 'JetBrains Mono'; position: absolute;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.3); cursor: grab; transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 10; transform: translate(-50%, -50%);
        }
        .player-dot:hover { transform: translate(-50%, -50%) scale(1.1); background: #00e5ff; color: #0b0f19; z-index: 20; }
        .ball { position: absolute; font-size: 18px; filter: drop-shadow(0 0 8px rgba(255,255,255,0.5)); animation: bounce 2s infinite; transform: translate(-50%, -50%); }
        @keyframes bounce { 
            0%, 100% { transform: translate(-50%, -50%) scale(1); } 
            50% { transform: translate(-50%, -50%) scale(1.2); } 
        }
    </style>
</head>
<body>
<div class="flex h-screen w-full items-center justify-center p-4">
    <div class="relative w-full aspect-[16/9] max-h-[600px] bg-slate-950 rounded-xl border border-white/10 overflow-hidden shadow-2xl">
        <div class="absolute inset-0 tactical-bg"></div>
        <div class="absolute inset-5 border border-white/20 rounded-sm opacity-80 pointer-events-none">
            <div class="absolute left-1/2 top-0 bottom-0 w-px bg-white/20"></div>
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 border border-white/20 rounded-full"></div>
            <div class="absolute top-1/2 left-0 -translate-y-1/2 w-40 h-80 border-r border-y border-white/20"></div>
            <div class="absolute top-1/2 left-0 -translate-y-1/2 w-16 h-40 border-r border-y border-white/20"></div>
            <div class="absolute top-1/2 right-0 -translate-y-1/2 w-40 h-80 border-l border-y border-white/20"></div>
            <div class="absolute top-1/2 right-0 -translate-y-1/2 w-16 h-40 border-l border-y border-white/20"></div>
        </div>
        
        __PLAYERS_PLACEHOLDER__
        
        <div class="ball" style="top: 55%; left: 55%;">⚽</div>
        
        <div class="absolute bottom-4 right-4 flex items-center gap-2">
             <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
             <span class="text-xs font-mono text-white/50">__FORMATION_NAME__ ACTIVE</span>
        </div>
    </div>
</div>
</body>
</html>
"""

# --- 3. HTML OLUŞTURUCU FONKSİYON ---
def generate_board_html(formation_name):
    players = FORMATIONS.get(formation_name, FORMATIONS["4-3-3"])
    players_html
