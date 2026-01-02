import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Mastermind OS", page_icon="🧬", layout="wide")

# --- 2. MASTERMIND SESSION STATE ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "opponent_dna": "Veri yok. Analiz bekleniyor...",
        "scouting_report": "Sistem aktif. Mastermind hazır.",
    }

# --- 3. SİSTEM BAŞLATMA (GEMINI 2.5 FLASH MÜHÜRLÜ) ---
@st.cache_resource
def init_system():
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        idx = pc.Index("regista-arsiv")
        embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return client, idx, embeds
    except: return None, None, None

client, pinecone_index, embeddings = init_system()

def get_mastermind_analysis(query, mode="TACTIC"):
    MODEL_ID = "gemini-2.5-flash" # HAFIZAYA KAYDEDİLDİ: GEMINI 2.5
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # Mode bazlı sistem talimatı
    if mode == "OPPONENT_DNA":
        instruction = "Sen Domenico Tedesco ve Luis Enrique'sin. Rakibin WhoScored/FBref verilerini tara. Zayıf halkayı, pres altındaki hata payını ve en çok gol yedikleri bölgeyi sayısal dök."
    else:
        instruction = "Sen Pep, Mourinho ve Klopp'un birleşimi olan bir taktik dehasısın."

    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=f"Tarih: 2 Ocak 2026. {instruction} Yanıtın sonunda [TEAM: ..., FORMATION: ...] ekle."
    )
    response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
    return response.text

# --- 4. 🏟️ MASTERMIND UI (DNA PANEL ENTEGRELİ) ---
def render_mastermind_ui(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    dna = context['opponent_dna'].replace("\n", "<br>").replace('"', "'")
    phase = context['game_phase']
    
    html_template = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: #0b1011; color: white; font-family: sans-serif; margin:0; overflow:hidden; }}
            .panel {{ background: #111718; border: 1px solid #283639; border-radius: 8px; padding: 15px; }}
            .dna-box {{ border-left: 4px solid #facc15; background: rgba(250, 204, 21, 0.05); padding: 10px; font-size: 11px; color: #fbbf24; }}
            .pitch-stripes {{ background-color: #173828; background-image: repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255, 255, 255, 0.03) 50px, rgba(255, 255, 255, 0.03) 100px); }}
        </style>
    </head>
    <body class="p-4">
        <div class="grid grid-cols-12 gap-4 h-screen">
            <div class="col-span-4 flex flex-col gap-4 overflow-y-auto">
                <div class="panel">
                    <h2 class="text-yellow-400 font-bold text-xs tracking-widest uppercase mb-2">🧬 OPPONENT DNA (DEŞİFRE)</h2>
                    <div class="dna-box">{dna}</div>
                </div>
                <div class="panel flex-1 overflow-y-auto">
                    <h2 class="text-cyan-400 font-bold text-xs tracking-widest uppercase mb-2">🧠 STRATEJİK RAPOR</h2>
                    <div class="text-[11px] leading-relaxed text-gray-400">{report}</div>
                </div>
            </div>

            <div class="col-span-8 panel relative flex items-center justify-center bg-[#0f1516]">
                 <div class="relative w-[400px] h-[580px] pitch-stripes rounded-lg border-2 border-white/10 overflow-hidden">
                    <div style="position:absolute; inset:20px; border:1px solid rgba(255,255,255,0.2);">
                        <div style="position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.2);"></div>
                    </div>
                    </div>
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_template, height=720)

# --- 5. SIDEBAR KONTROLLERİ ---
with st.sidebar:
    st.title("🧬 MASTERMIND SCOUT")
    st.markdown("---")
    
    if st.button("🔬 RAKİBİ DEŞİFRE ET (Tedesco Modu)"):
        team = st.session_state.tactic_context['focus_team']
        # Gemini 2.5 Flash ile internet taraması
        dna_results = get_mastermind_analysis(f"{team} takımının sıradaki rakibinin WhoScored ve FBref verilerini analiz et. Zayıf noktaları bul.", mode="OPPONENT_DNA")
        st.session_state.tactic_context['opponent_dna'] = dna_results
        st.rerun()

    st.markdown("---")
    phase = st.radio("OYUN EVRESİ", ["SET HÜCUMU", "SAVUNMA", "GEÇİŞ"])
    st.session_state.tactic_context['game_phase'] = phase

# Render UI
render_mastermind_ui(st.session_state.tactic_context)

if prompt := st.chat_input("Mastermind'a direktif ver..."):
    ans = get_mastermind_analysis(prompt)
    st.session_state.tactic_context['scouting_report'] = ans
    st.rerun()
