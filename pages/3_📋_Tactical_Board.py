import streamlit as st
import streamlit.components.v1 as components

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Tactical Board | DATALIG", page_icon="📋", layout="wide")

# --- HTML & CSS & JS ENTEGRASYONU ---
# Burası senin orijinal board.html tasarımının Streamlit içinde çalışmasını sağlar.
tactical_board_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#00e5ff',
                        bgDark: '#0b0f19',
                        surface: '#1e293b'
                    },
                    fontFamily: {
                        mono: ['JetBrains Mono', 'monospace'],
                        sans: ['Inter', 'sans-serif']
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: transparent; color: white; overflow: hidden; }
        
        /* SAHA ZEMİN EFEKTLERİ */
        .tactical-bg {
            background-color: #0b0f19;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 60px 60px;
        }
        .pitch-lines {
            background-image: 
                linear-gradient(rgba(0, 229, 255, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 229, 255, 0.1) 1px, transparent 1px);
            background-size: 30px 30px;
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
        }
        .player-dot:hover {
            transform: scale(1.1);
            background: #00e5ff;
            color: #0b0f19;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.6);
            z-index: 20;
        }
        
        /* TOP */
        .ball {
            position: absolute; font-size: 20px;
            filter: drop-shadow(0 0 8px rgba(255,255,255,0.5));
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }

        /* HEATMAP EFEKTİ */
        .heatmap-overlay {
            background: radial-gradient(circle at 60% 40%, rgba(0, 229, 255, 0.15) 0%, transparent 50%);
            mix-blend-mode: screen;
            pointer-events: none;
        }
    </style>
</head>
<body>

<div class="flex h-screen w-full gap-4">
    <div class="relative flex-1 bg-slate-950 rounded-xl border border-white/10 overflow-hidden shadow-2xl">
        <div class="absolute inset-0 tactical-bg"></div>
        <div class="absolute inset-0 pitch-lines opacity-30"></div>
        <div class="absolute inset-0 heatmap-overlay"></div>
        
        <div class="absolute inset-4 border border-white/20 rounded-sm opacity-80 pointer-events-none">
            <div class="absolute top-1/2 left-0 right-0 h-px bg-white/20"></div>
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 border border-white/20 rounded-full"></div>
            
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-32 border-b border-x border-white/20"></div>
            <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-64 h-32 border-t border-x border-white/20"></div>
        </div>

        <div class="player-dot" style="bottom: 5%; left: 50%;">GK</div>
        
        <div class="player-dot" style="bottom: 20%; left: 15%;">LB</div>
        <div class="player-dot" style="bottom: 20%; left: 38%;">LCB</div>
        <div class="player-dot" style="bottom: 20%; left: 62%;">RCB</div>
        <div class="player-dot" style="bottom: 20%; left: 85%;">RB</div>
        
        <div class="player-dot" style="bottom: 38%; left: 50%;">DM</div>
        <div class="player-dot" style="bottom: 48%; left: 30%;">CM</div>
        <div class="player-dot" style="bottom: 48%; left: 70%;">CM</div>
        
        <div class="player-dot" style="bottom: 70%; left: 15%;">LW</div>
        <div class="player-dot" style="bottom: 75%; left: 50%;">ST</div>
        <div class="player-dot" style="bottom: 70%; left: 85%;">RW</div>

        <div class="ball" style="bottom: 60%; left: 65%;">⚽</div>
        
        <div class="absolute top-4 right-4 bg-slate-900/90 backdrop-blur px-3 py-1.5 rounded border border-white/10 flex items-center gap-2 shadow-lg">
            <span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            <span class="text-xs font-mono text-primary">LIVE ANALYSIS</span>
        </div>
    </div>
</div>

</body>
</html>
"""

# --- STREAMLIT ARAYÜZÜ ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 TAKTİK TAHTASI PRO")
    # HTML Kodu Güvenli Bir Şekilde Iframe İçine Gömüyoruz
    # Bu yöntem CSS çakışmalarını ve Syntax hatalarını engeller.
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
        
        formation = st.selectbox("Formasyon Değiştir", ["4-3-3", "4-2-3-1", "3-5-2", "WM"])
        style = st.selectbox("Oyun Anlayışı", ["Possession", "Gegenpressing", "Counter"])
        
        st.markdown("---")
        
        st.info("💡 **Analist Notu:** Rakip stoperlerin arası 15 metreden fazla açılıyor. ST'yi bu boşluğa koştur.")
        
        if st.button("💾 Taktikleri Kaydet", use_container_width=True):
            st.success("Taktik varyasyonu veritabanına işlendi.")
