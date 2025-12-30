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
st.markdown("<h1 class='main-title'>THE ORACLE</h1>", unsafe_allow
