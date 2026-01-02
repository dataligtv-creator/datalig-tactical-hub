import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Mastermind OS", page_icon="🧠", layout="wide")

# --- 2. MASTERMIND SESSION STATE ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU", # Yeni: Oyun Fazı
        "scouting_report": "Efsanelerin ortak aklı devreye alınıyor. Veri girişi bekleniyor...",
        "last_update": time.time()
    }

# --- 3. SİSTEM BAŞLATMA (PAID TIER GEMINI 2.5) ---
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

def get_mastermind_analysis(query, phase):
    MODEL_ID = "gemini-2.0-flash" 
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "2 Ocak 2026"
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=f"""
        Sen Pep, Mourinho, Klopp ve Ancelotti'nin futbol zekalarının birleşimisin. 
        Analizini şu 3 evreye göre yap: 
        1. Savunma (Simeone/Mourinho perspektifi)
        2. Set Hücumu (Pep/Enrique perspektifi)
        3. Geçiş Hücumu (Klopp/Ferguson perspektifi).
        Şu anki odak evren: {phase}. 
        Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] ekle.
        """
    )
    response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
    return response.text

# --- 4. 🏟️ MASTERMIND DİNAMİK SAHA (V1.0) ---
def render_mastermind_ui(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    phase = context['game_phase']
    form = context['formation']
    
    # Koordinatlar ve Taktiksel Oklar (Faz bazlı dinamik yapı)
    arrows_html = ""
    if phase == "SET HÜCUMU":
        # Pep usulü beklerin içeri kat etmesi ve kanat genişliği okları
        arrows_html = """
        <line x1="15%" y1="80%" x2="35%" y2="70%" stroke="#13c8ec" stroke-dasharray="4" stroke-width="2" marker-end="url(#arrowhead)" />
        <line x1="85%" y1="80%" x2="65%" y2="70%" stroke="#13c8ec" stroke-dasharray="4" stroke-width="2" marker-end="url(#arrowhead)" />
        <circle cx="50%" cy="30%" r="40" fill="rgba(0,229,255,0.05)" stroke="rgba(0,229,255,0.2)" stroke-dasharray="2" />
        """
    elif phase == "SAVUNMA":
        # Simeone usulü dar blok ve kompakt yapı çizgileri
        arrows_html = """
        <rect x="20%" y="70%" width="60%" height="20%" fill="rgba(239,68,68,0.1)" stroke="rgba(239,68,68,0.3)" stroke-width="1" />
        <line x1="50%" y1="60%" x2="50%" y2="90%" stroke="#ef4444" stroke-width="1" stroke-dasharray="2" />
        """

    # Piyon Yerleşimi
    pos_db = {
        "4-3-3": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (55, 30, "8"), (60, 50, "6"), (55, 70, "10"), (30, 20, "7"), (25, 50, "9"), (30, 80, "11")],
        "4-2-3-1": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (65, 40, "6"), (65, 60, "8"), (45, 20, "7"), (42, 50, "10"), (45, 80, "11"), (25, 50, "9")]
    }
    players_html = "".join([f"<div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:20;'><div style='width:24px; height:24px; border-radius:50%; background:white; border:2px solid #13c8ec; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:bold; color:black; box-shadow: 0 0 10px rgba(19,200,236,0.6);'>{num}</div></div>" for t, l, num in pos_db.get(form, pos_db["4-3-3"])])

    html_template = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: #0b1011; color: white; font-family: sans-serif; margin:0; overflow:hidden; }}
            .pitch-stripes {{ background-color: #173828; background-image: repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255, 255, 255, 0.03) 50px, rgba(255, 255, 255, 0.03) 100px); }}
            .master-panel {{ background: #111718; border: 1px solid #283639; border-radius: 8px; padding: 15px; }}
        </style>
    </head>
    <body class="p-4">
        <div class="grid grid-cols-12 gap-4">
            <div class="col-span-4 flex flex-col gap-4 h-[650px]">
                <div class="master-panel bg-primary/5 border-primary/20">
                    <h2 class="text-primary font-bold text-sm tracking-widest uppercase mb-1">🧠 MASTERMIND CORE</h2>
                    <p class="text-[10px] text-gray-500 uppercase">Phase: {phase} | Style: Hybrid Elite</p>
                </div>
                <div class="master-panel flex-1 overflow-y-auto font-mono text-xs leading-relaxed text-gray-400">
                    {report}
                </div>
            </div>

            <div class="col-span-8 master-panel relative flex items-center justify-center bg-[#0f1516]">
                <div class="relative w-[420px] h-[580px] pitch-stripes rounded-lg border-2 border-white/10 overflow-hidden">
                    <svg style="position:absolute; inset:0; width:100%; height:100%; z-index:15;">
                        <defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#13c8ec"/></marker></defs>
                        {arrows_html}
                    </svg>
                    <div style="position:absolute; inset:20px; border:1px solid rgba(255,255,255,0.2);">
                        <div style="position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.2);"></div>
                    </div>
                    {players_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_template, height=700)

# --- 5. ANA KONTROLLER ---
with st.sidebar:
    st.title("🧠 MASTERMIND OS")
    st.markdown("---")
    phase = st.radio("OYUN EVRESİ SEÇİN", ["SET HÜCUMU", "SAVUNMA", "GEÇİŞ ATATKI"])
    st.session_state.tactic_context['game_phase'] = phase
    
    st.markdown("---")
    st.subheader("🎯 Efsanevi Direktifler")
    if st.button("RAKİBİ DEŞİFRE ET (Enrique/Tedesco)"):
        team = st.session_state.tactic_context['focus_team']
        ans = get_mastermind_analysis(f"{team} için rakip analizi yap.", phase)
        st.session_state.tactic_context['scouting_report'] = ans
        st.rerun()

# Render UI
render_mastermind_ui(st.session_state.tactic_context)

# Sohbet Girişi
if prompt := st.chat_input("Mastermind'a bir soru sor (Örn: Pep gibi hücum setleri kur)"):
    ans = get_mastermind_analysis(prompt, st.session_state.tactic_context['game_phase'])
    st.session_state.tactic_context['scouting_report'] = ans
    st.rerun()
