import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# --- 2. SESSION STATE (BELLEK) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "scouting_report": "Sistem başlatıldı. Teknik direktör girişi bekleniyor...",
        "last_update": time.time()
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. GİRİŞ KONTROLÜ ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center; color:#00E5FF;'>DATALIG COCKPIT</h2>", unsafe_allow_html=True)
    pw = st.text_input("Şifre", type="password")
    if st.button("SİSTEME GİRİŞ"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 4. SİSTEM BAŞLATMA (API & DB) ---
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
        system_instruction=f"Tarih: {current_date}. Sen DATALIG Football OS Baş Stratejistisin. Profesyonel analiz yap. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver."
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=[f"{current_date} verisiyle: {query}"], config=config)
    return response.text

# --- 6. STITCH UI ŞABLONU (HTML/Tailwind) ---
def render_stitch_ui(context):
    # Rapor metnini HTML dostu yapıyoruz
    clean_report = context['scouting_report'].replace("\n", "<br>").replace("**", "")
    
    html_code = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
        <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600&family=Share+Tech+Mono&display=swap" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet"/>
        <style>
            body {{ background-color: #0B0E14; color: #cbd5e1; font-family: 'Rajdhani', sans-serif; overflow: hidden; }}
            .glass-panel {{ background: rgba(19, 27, 38, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(0, 229, 255, 0.2); }}
            .border-glow-cyan {{ box-shadow: 0 0 15px rgba(0, 229, 255, 0.1); }}
            .pitch-bg {{ background-color: #131B26; background-image: radial-gradient(#1f2937 1px, transparent 1px); background-size: 30px 30px; }}
        </style>
    </head>
    <body class="p-2">
        <header class="flex justify-between items-center mb-4">
            <div class="flex items-center gap-2">
                <span class="material-icons-outlined text-red-500 text-3xl">shield</span>
                <h1 class="text-2xl font-bold tracking-tighter text-white">DATALIG <span class="text-xs text-slate-500 font-mono">V6.0</span></h1>
            </div>
            <div class="flex gap-2">
                <div class="glass-panel px-4 py-1 border-b-2 border-red-500 text-xs uppercase font-bold text-white tracking-widest">TAKIM: {context['focus_team']}</div>
                <div class="glass-panel px-4 py-1 border-b-2 border-cyan-400 text-xs uppercase font-bold text-cyan-400 tracking-widest">DİZİLİŞ: {context['formation']}</div>
            </div>
        </header>

        <main class="grid grid-cols-12 gap-4 h-[450px]">
            <div class="col-span-3 glass-panel p-4 rounded-lg flex flex-col h-full">
                <h4 class="text-cyan-400 text-xs uppercase tracking-tighter mb-2 border-b border-slate-700 pb-1">Intelligence Report</h4>
                <div class="flex-1 overflow-y-auto font-mono text-[11px] leading-relaxed text-slate-400">
                    {clean_report[:800]}...
                </div>
            </div>

            <div class="col-span-9 pitch-bg border border-slate-700 rounded-lg relative overflow-hidden flex items-center justify-center">
                 <div class="absolute inset-4 border-2 border-white/10 rounded">
                    <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-white/10 -translate-y-1/2"></div>
                    <div class="absolute top-1/2 left-1/2 w-24 h-24 border-2 border-white/10 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
                 </div>
                 <div class="text-center z-10">
                    <span class="material-icons-outlined text-cyan-400 text-6xl animate-pulse">radar</span>
                    <p class="text-[10px] font-mono text-cyan-400 mt-2 tracking-widest">TACTICAL COMMAND ACTIVE</p>
                 </div>
            </div>
        </main>
    </body>
    </html>
    """
    return components.html(html_code, height=520)

# --- 7. ANA ARAYÜZ ---
# Stitch Tasarımını Ekrana Bas
render_stitch_ui(st.session_state.tactic_context)

# Chat Alanı (Alt Kısım)
st.markdown("---")
if "messages" not in st.session_state: st.session_state.messages = []

# Chat Geçmişini Sınırlı Tut (Arayüzü bozmasın diye)
for msg in st.session_state.messages[-4:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Giriş ve Analiz İşlemi
if prompt := st.chat_input("Taktiksel komutunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.status("🔍 Veri Katmanları Harmanlanıyor...", expanded=False):
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            ans = get_manager_analysis(prompt, archive)
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # --- Dinamik Bağlam Güncelleme ---
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        elif "Galatasaray" in ans: st.session_state.tactic_context['focus_team'] = "GALATASARAY"
        
        for f in ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"]:
            if f in ans or f in prompt: st.session_state.tactic_context['formation'] = f
            
        st.session_state.tactic_context['scouting_report'] = ans
        st.session_state.tactic_context['last_update'] = time.time()
        st.rerun()
