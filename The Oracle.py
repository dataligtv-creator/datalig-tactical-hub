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
    
    # Dizilişe Göre Dinamik Piyon Pozisyonları
    pos_db = {
        "4-3-3": [
            {"t": "92%", "l": "50%", "i": "shield"}, # GK
            {"t": "78%", "l": "15%"}, {"t": "80%", "l": "38%"}, {"t": "80%", "l": "62%"}, {"t": "78%", "l": "85%"}, # DEF
            {"t": "55%", "l": "30%"}, {"t": "60%", "l": "50%"}, {"t": "55%", "l": "70%"}, # MID
            {"t": "30%", "l": "20%"}, {"t": "25%", "l": "50%"}, {"t": "30%", "l": "80%"}  # FWD
        ],
        "4-2-3-1": [
            {"t": "92%", "l": "50%", "i": "shield"},
            {"t": "78%", "l": "12%"}, {"t": "80%", "l": "35%"}, {"t": "80%", "l": "65%"}, {"t": "78%", "l": "88%"},
            {"t": "65%", "l": "40%"}, {"t": "65%", "l": "60%"},
            {"t": "45%", "l": "20%"}, {"t": "40%", "l": "50%"}, {"t": "45%", "l": "80%"},
            {"t": "20%", "l": "50%"}
        ],
        "3-5-2": [
             {"t": "92%", "l": "50%", "i": "shield"},
             {"t": "80%", "l": "25%"}, {"t": "82%", "l": "50%"}, {"t": "80%", "l": "75%"},
             {"t": "55%", "l": "10%"}, {"t": "50%", "l": "35%"}, {"t": "52%", "l": "50%"}, {"t": "50%", "l": "65%"}, {"t": "55%", "l": "90%"},
             {"t": "25%", "l": "40%"}, {"t": "25%", "l": "60%"}
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
            .scan-line {{
                position: absolute; width: 100%; h-1px; background: linear-gradient(90deg, transparent, #00e5ff, transparent);
                opacity: 0.3; animation: scan 4s linear infinite;
            }}
            @keyframes scan {{ 0% {{ top: 0%; }} 100% {{ top: 100%; }} }}
        </style>
    </head>
    <body class="p-2">
        <header class="flex justify-between items-center mb-4 px-2">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 border border-red-500 flex items-center justify-center rounded bg-slate-900 shadow-[0_0_10px_rgba(255,0,0,0.2)]">
                    <span class="material-icons-outlined text-red-500">terminal</span>
                </div>
                <h1 class="text-xl font-bold tracking-widest text-white uppercase">Datalig <span class="text-cyan-400 italic">OS</span></h1>
            </div>
            <div class="flex gap-4">
                <div class="glass-panel px-5 py-1 border-b border-red-500 text-[10px] tracking-widest uppercase">Target: <span class="text-white">{context['focus_team']}</span></div>
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

            <div class="col-span-9 cyber-pitch rounded-lg overflow-hidden">
                <div class="scan-line"></div>
                <div class="absolute inset-6 border border-white/5">
                    <div class="absolute top-1/2 left-0 right-0 h-[1px] bg-white/10"></div>
                    <div class="absolute top-1/2 left-1/2 w-28 h-28 border border-white/10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-40 h-16 border-b border-x border-white/10"></div>
                    <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-40 h-16 border-t border-x border-white/10"></div>
                </div>
                
                {player_html}

                <div class="absolute bottom-4 right-4 text-[9px] font-mono text-slate-600 tracking-widest">
                    DATALIG // TACTICAL_CORE_V6.1
                </div>
            </div>
        </main>
    </body>
    </html>
    """
    return components.html(html_code, height=600)

# --- 7. ANA ARAYÜZ ---
# Dashboard'u render et
render_cyber_ui(st.session_state.tactic_context)

# Chat Alanı
st.markdown("---")
if "messages" not in st.session_state: st.session_state.messages = []

# Mesaj Akışı (Sadece son 3 mesaj)
for msg in st.session_state.messages[-3:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Giriş ve Analiz
if prompt := st.chat_input("Taktiksel komut beklemede..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.status("🔍 Veri Katmanları Analiz Ediliyor...", expanded=False):
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            ans = get_manager_analysis(prompt, archive)
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Otomatik Bağlam Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        elif "Galatasaray" in ans: st.session_state.tactic_context['focus_team'] = "GALATASARAY"
        
        for f in ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"]:
            if f in ans or f in prompt: st.session_state.tactic_context['formation'] = f
            
        st.session_state.tactic_context['scouting_report'] = ans
        st.session_state.tactic_context['last_update'] = time.time()
        st.rerun()
