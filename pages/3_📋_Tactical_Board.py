import streamlit as st
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- HTML & CSS & JS (YATAY SAHA) ---
tactical_board_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: { primary: '#00e5ff', bgDark: '#0b0f19' },
                    fontFamily: { mono: ['JetBrains Mono', 'monospace'], sans: ['Inter', 'sans-serif'] }
                }
            }
        }
    </script>
    <style>
        body { background-color: transparent; color: white; overflow: hidden; }
        
        .tactical-bg {
            background-color: #0b0f19;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
        }
        
        /* OYUNCU NOKTALARI */
        .player-dot {
            width: 32px; height: 32px;
            background: #0b0f19;
            border: 2px solid #00e5ff;
            color: #00e5ff;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 11px; font-family: 'JetBrains Mono';
            position: absolute;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
            cursor: grab;
            transition: all 0.2s;
            z-index: 10;
            transform: translate(-50%, -50%); /* Tam merkezleme */
        }
        .player-dot:hover {
            transform: translate(-50%, -50%) scale(1.1);
            background: #00e5ff; color: #0b0f19;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.6); z-index: 20;
        }
        
        /* TOP */
        .ball {
            position: absolute; font-size: 18px;
            filter: drop-shadow(0 0 8px rgba(255,255,255,0.5));
            animation: bounce 2s infinite;
            transform: translate(-50%, -50%);
        }
        @keyframes bounce { 0%, 100% { transform: translate(-50%, -50%) scale(1); } 50% { transform: translate(-50%, -50%) scale(1.2); } }
    </style>
</head>
<body>

<div class="flex h-screen w-full items-center justify-center p-4">
    <div class="relative w-full aspect-[16/9] max-h-[600px] bg-slate-950 rounded-xl border border-white/10 overflow-hidden shadow-2xl">
        
        <div class="absolute inset-0 tactical-bg"></div>
        
        <div class="absolute inset-5 border border-white/20 rounded-sm opacity-80 pointer-events-none">
            
            <div class="absolute left-1/2 top-0 bottom-0 w-px bg-white/20"></div>
            
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 border border-white/20 rounded-full"></div>
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-1 bg-white rounded-full"></div>
            
            <div class="absolute top-1/2 left-0 -translate-y-1/2 w-40 h-80 border-r border-y border-white/20"></div> <div class="absolute top-1/2 left-0 -translate-y-1/2 w-16 h-40 border-r border-y border-white/20"></div> <div class="absolute top-1/2 left-[11%] -translate-y-1/2 w-1 h-1 bg-white rounded-full"></div> <div class="absolute top-1/2 right-0 -translate-y-1/2 w-40 h-80 border-l border-y border-white/20"></div> <div class="absolute top-1/2 right-0 -translate-y-1/2 w-16 h-40 border-l border-y border-white/20"></div> <div class="absolute top-1/2 right-[11%] -translate-y-1/2 w-1 h-1 bg-white rounded-full"></div> <div class="absolute top-0 left-0 w-4 h-4 border-b border-r border-white/20 rounded-br-full"></div>
            <div class="absolute top-0 right-0 w-4 h-4 border-b border-l border-white/20 rounded-bl-full"></div>
            <div class="absolute bottom-0 left-0 w-4 h-4 border-t border-r border-white/20 rounded-tr-full"></div>
            <div class="absolute bottom-0 right-0 w-4 h-4 border-t border-l border-white/20 rounded-tl-full"></div>
        </div>

        <div class="player-dot" style="top: 50%; left: 5%;">GK</div>
        
        <div class="player-dot" style="top: 15%; left: 20%;">LB</div>
        <div class="player-dot" style="top: 38%; left: 20%;">LCB</div>
        <div class="player-dot" style="top: 62%; left: 20%;">RCB</div>
        <div class="player-dot" style="top: 85%; left: 20%;">RB</div>
        
        <div class="player-dot" style="top: 50%; left: 35%;">DM</div>
        <div class="player-dot" style="top: 30%; left: 45%;">LCM</div>
        <div class="player-dot" style="top: 70%; left: 45%;">RCM</div>
        
        <div class="player-dot" style="top: 20%; left: 75%;">LW</div>
        <div class="player-dot" style="top: 50%; left: 80%;">ST</div>
        <div class="player-dot" style="top: 80%; left: 75%;">RW</div>

        <div class="ball" style="top: 55%; left: 55%;">⚽</div>
        
        <div class="absolute bottom-4 left-4 text-xs text-slate-500 font-mono">
            Attack Direction ➜
        </div>
    </div>
</div>

</body>
</html>
"""

# --- STREAMLIT ARAYÜZÜ ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 TAKTİK TAHTASI (YATAY)")
    components.html(tactical_board_html, height=600, scrolling=False)

with col2:
    st.markdown("### ⚙️ SAHA KENARI")
    
    with st.container():
        st.markdown("""
        <div style="background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
            <div style="color: #94a3b8; font-size: 12px; margin-bottom: 5px;">DİZİLİŞ</div>
            <div style="color: white; font-weight: bold; font-size: 18px;">4-3-3 ATTACK</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        formation = st.selectbox("Formasyon", ["4-3-3", "4-2-3-1", "3-5-2"])
        style = st.selectbox("Oyun Anlayışı", ["Possession", "Gegenpressing", "Counter"])
        
        st.markdown("---")
        st.info("💡 **Not:** Sol kanattan (LW) bindirme yaparken LCB'nin kademeye girmesi gerekiyor.")
        
        if st.button("💾 Kaydet", use_container_width=True):
            st.success("Taktik kaydedildi.")
