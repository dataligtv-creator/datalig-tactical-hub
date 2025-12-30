import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# --- 2. SESSION STATE (BELLEK) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "BEKLEMEDE",
        "formation": "4-3-3",
        "scouting_report": "Sistem aktif. Komut bekleniyor...",
        "last_update": time.time()
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. GİRİŞ KONTROLÜ ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#00E5FF; font-family:monospace;'>DATALIG COCKPIT</h1>", unsafe_allow_html=True)
    pw = st.text_input("Sistem Şifresi", type="password")
    if st.button("ERİŞİM SAĞLA"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 4. SİSTEM BAŞLATMA ---
@st.cache_resource
def init_system():
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

client, pinecone_index, embeddings = init_system()

# --- 5. ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "30 Aralık 2025" 
    config = types.GenerateContentConfig(
        tools=[search_tool], temperature=1.0,
        system_instruction=f"Tarih: {current_date}. Sen DATALIG Football OS Baş Stratejistisin. WhoScored ve FBref verilerini tara. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver."
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=[f"{current_date} verisiyle: {query}"], config=config)
    return response.text

# --- 6. 🚀 STITCH UI: CYBER-PITCH ENGINE ---
def render_cyber_ui(context):
    clean_report = context['scouting_report'].replace("\n", "<br>").replace("**", "")
    formation = context['formation']
    
    # --- DİKEY SAHA POZİSYONLARI (Alt Kale: Savunma, Üst Kale: Hücum) ---
    pos_db = {
        "4-3-3": [
            {"t": "92%", "l": "50%", "i": "shield"}, # Kaleci (Alt)
            {"t": "80%", "l": "20%"}, {"t": "82%", "l": "40%"}, {"t": "82%", "l": "60%"}, {"t": "80%", "l": "80%"}, # Defans
            {"t": "60%", "l": "30%"}, {"t": "65%", "l": "50%"}, {"t": "60%", "l": "70%"}, # Orta Saha
            {"t": "35%", "l": "20%"}, {"t": "28%", "l": "50%"}, {"t": "35%", "l": "80%"}  # Hücum (Üst)
        ],
        "4-2-3-1": [
            {"t": "92%", "l": "50%", "i": "shield"},
            {"t": "80%", "l": "15%"}, {"t": "82%", "l": "38%"}, {"t": "82%", "l": "62%"}, {"t": "80%", "l": "85%"},
            {"t": "68%", "l": "40%"}, {"t": "68%", "l": "60%"},
            {"t": "48%", "l": "20%"}, {"t": "45%", "l": "50%"}, {"t": "48%", "l": "80%"},
            {"t": "25%", "l": "50%"}
        ],
        "3-5-2": [
             {"t": "92%", "l": "50%", "i": "shield"},
             {"t": "82%", "l": "25%"}, {"t": "84%", "l": "50%"}, {"t": "82%", "l": "75%"},
             {"t": "60%", "l": "10%"}, {"t": "58%", "l": "35%"}, {"t": "58%", "l": "50%"}, {"t": "58%", "l": "65%"}, {"t": "60%", "l": "90%"},
             {"t": "30%", "l": "40%"}, {"t": "30%", "l": "60%"}
        ]
    }
    
    players = pos_db.get(formation, pos_db["4-3-3"])
    player_html = "".join([f"""
        <div class="absolute" style="top: {p['t']}; left: {p['l']}; transform: translate(-50%, -50%);">
            <div class="w-7 h-7 rounded-full border border-cyan-400 bg-slate-950 flex items-center justify-center shadow-[0_0_8px_rgba(0,229,255,0.6)]">
                <span class="material-icons-outlined text-cyan-400" style="font-size: 14px;">{p.get('i', 'person')}</span>
            </div>
        </div>
    """ for p in players])

    html_code = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600&family=Share+Tech+Mono&display=swap" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet"/>
        <style>
            body {{ background-color: #0B0E14; color: #cbd5e1; font-family: 'Rajdhani', sans-serif; overflow: hidden; }}
            .glass-panel {{ background: rgba(19, 27, 38, 0.85); backdrop-filter: blur(10px); border: 1px solid rgba(0, 229, 255, 0.15); }}
            .cyber-pitch {{ 
                background: #0B0E14;
                position: relative;
                background-image: radial-gradient(circle, #1e2937 1px, transparent 1px);
                background-size: 25px 25px;
                border: 1px solid #1e293b;
            }}
        </style>
    </head>
    <body class="p-2">
        <header class="flex justify-between items-center mb-4 px-2">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 border border-cyan-500 flex items-center justify-center rounded bg-slate-900">
                    <span class="material-icons-outlined text-cyan-500">radar</span>
                </div>
                <h1 class="text-xl font-bold tracking-widest text-white uppercase">Datalig <span class="text-cyan-400">OS</span></h1>
            </div>
            <div class="flex gap-4">
                <div class="glass-panel px-5 py-1 border-b border-red-500 text-[10px] tracking-widest uppercase">Target: {context['focus_team']}</div>
                <div class="glass-panel px-5 py-1 border-b border-cyan-500 text-[10px] tracking-widest uppercase text-cyan-400">System: {formation}</div>
            </div>
        </header>

        <main class="grid grid-cols-12 gap-4 h-[520px]">
            <div class="col-span-3 glass-panel p-4 rounded-lg flex flex-col">
                <div class="flex items-center gap-2 mb-3 border-b border-slate-700 pb-2">
                    <span class="material-icons-outlined text-cyan-400 text-sm">sensors</span>
                    <h4 class="text-cyan-400 text-[10px] uppercase tracking-widest font-mono">Scouting Feed</h4>
                </div>
                <div class="flex-1 overflow-y-auto font-mono text-[10px] leading-relaxed text-slate-400 pr-2">
                    {clean_report}
                </div>
            </div>

            <div class="col-span-9 cyber-pitch rounded-lg overflow-hidden border border-slate-700">
                <div class="absolute inset-x-12 inset-y-6 border border-white/10">
                    <div class="absolute top-1/2 left-0 right-0 h-[1px] bg-white/10"></div>
                    <div class="absolute top-1/2 left-1/2 w-28 h-28 border border-white/10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                    
                    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-20 border-b border-x border-white/10"></div>
                    <div class="absolute -top-1 left-1/2 -translate-x-1/2 w-20 h-2 bg-cyan-500/20 border border-cyan-500/50"></div>
                    
                    <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-48 h-20 border-t border-x border-white/10"></div>
                    <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-20 h-2 bg-red-500/20 border border-red-500/50"></div>
                </div>
                
                {player_html}

                <div class="absolute bottom-2 right-4 text-[8px] font-mono text-slate-600 uppercase">
                    Tactical Engine V6.2 // Vertical Matrix
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    return components.html(html_code, height=600)
