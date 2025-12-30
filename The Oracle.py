import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
import time

# --- 1. GLOBAL KONFİGÜRASYON VE CSS ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    /* Global Tema */
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }
    
    /* Neon Başlık */
    .main-title {
        font-family: 'Monospace';
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #00e5ff, #7dd3fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        margin-bottom: 0px;
    }

    /* Cam Efektli Metrik Kartları */
    .metric-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
        padding: 20px;
        border-radius: 16px;
        flex: 1;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #00e5ff;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: #00e5ff;
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 5px;
    }

    /* Chat Mesaj Tasarımı */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.2) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Şablon Butonları */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid rgba(0, 229, 255, 0.3);
        color: #00e5ff;
        font-weight: 600;
        padding: 10px;
        transition: 0.3s all;
    }
    .stButton>button:hover {
        background: #00e5ff !important;
        color: #020617 !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE YÖNETİMİ ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Hafıza Bekliyor...",
        "formation": "4-3-3",
        "scouting_report": "Henüz analiz yapılmadı.",
        "last_update": time.time()
    }

# --- 3. GİRİŞ VE SİSTEM BAŞLATMA ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 class='main-title' style='text-align:center;'>DATALIG</h1>", unsafe_allow_html=True)
    pw = st.text_input("Şifre", type="password", key="login_pw")
    if st.button("SİSTEME GİRİŞ"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Erişim Reddedildi")
    st.stop()

@st.cache_resource
def init_system():
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

client, pinecone_index, embeddings = init_system()

# --- 4. ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "30 Aralık 2025" 
    config = types.GenerateContentConfig(
        tools=[search_tool], temperature=1.0,
        system_instruction=f"Tarih: {current_date}. Sen DATALIG Football OS Baş Stratejistisin. WhoScored, FBref ve Transfermarkt verilerini zorunlu tara. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver."
    )
    forced_query = f"{current_date} itibarıyla güncel veriyle yanıtla: {query}"
    response = client.models.generate_content(model="gemini-2.5-flash", contents=[forced_query], config=config)
    return response.text

# --- 5. ARAYÜZ KATMANI ---
st.markdown("<h1 class='main-title'>THE ORACLE</h1>", unsafe_allow_html=True)

# Üst Metrik Kartları
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">AKTİF TAKIM</div><div class="metric-value">{st.session_state.tactic_context["focus_team"]}</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">DİZİLİŞ</div><div class="metric-value">{st.session_state.tactic_context["formation"]}</div></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">SİSTEM DURUMU</div><div class="metric-value">ANALİTİK</div></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/football.png", width=80)
    st.markdown("### STRATEJİK YÖNETİM")
    if st.button("Hafızayı Temizle"):
        st.session_state.tactic_context = {"focus_team": "Hafıza Bekliyor...", "formation": "4-3-3", "scouting_report": "", "last_update": time.time()}
        st.rerun()
    st.markdown("---")
    st.caption("Veri Kaynakları: Opta, FBref, WhoScored")

# Mesaj Geçmişi
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Hızlı Komutlar
st.markdown("<p style='font-size: 0.8rem; color: #94a3b8; font-weight: bold; margin-bottom: 10px;'>⚡ HIZLI KOMUT PANELİ</p>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
templates = {
    "🔍 GÖZLEM": "Aktif takımı WhoScored verileriyle analiz et. Zayıf halkayı raporla.",
    "🛡️ REÇETE": "Bu takıma karşı xG düşürücü savunma planı öner.",
    "📈 TRANSFER": "Archie Brown'ın güncel FBref istatistiklerini tara.",
    "🏟️ MAÇ ANALİZİ": "Son maçın xG ve taktiksel hatalarını raporla."
}

def trigger_template(prompt_text):
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.rerun()

with c1: 
    if st.button("🔍 GÖZLEM"): trigger_template(templates["🔍 GÖZLEM"])
with c2: 
    if st.button("🛡️ REÇETE"): trigger_template(templates["🛡️ REÇETE"])
with c3: 
    if st.button("📈 TRANSFER"): trigger_template(templates["📈 TRANSFER"])
with c4: 
    if st.button("🏟️ MAÇ ANALİZİ"): trigger_template(templates["🏟️ MAÇ ANALİZİ"])

# Giriş
if prompt := st.chat_input("Taktiksel komut bekliyorum..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Analiz İşleme
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_p = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.status("📊 Veri Katmanları Analiz Ediliyor...", expanded=False):
            vec = embeddings.embed_query(last_p)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            ans = get_manager_analysis(last_p, archive)
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Context Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in last_p: st.session_state.tactic_context['focus_team'] = "Fenerbahçe"
        elif "Galatasaray" in ans: st.session_state.tactic_context['focus_team'] = "Galatasaray"
        for f in ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2", "3-4-3"]:
            if f in ans or f in last_p: st.session_state.tactic_context['formation'] = f
        
        st.session_state.tactic_context['scouting_report'] = ans
        st.rerun()
