import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
import time

# --- 1. SAYFA VE GLOBAL BELLEK AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Genel",
        "formation": "4-3-3",
        "scouting_report": "Henüz bir analiz yapılmadı.",
        "last_update": time.time()
    }

# --- 2. 🔐 GİRİŞ KONTROLÜ ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if st.session_state.get("password_input") == "datalig2025":
        st.session_state.authenticated = True
    else:
        st.error("Hatalı şifre teknik direktörüm!")

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>DATALIG COCKPIT</h2>", unsafe_allow_html=True)
        st.text_input("Şifre", type="password", key="password_input")
        st.button("Giriş Yap", on_click=check_login)
    st.stop()

# --- 3. 🚀 SİSTEM BAŞLATMA ---
@st.cache_resource
def init_system():
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

try:
    client, pinecone_index, embeddings = init_system()
    MODEL_ID = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Sistem başlatılamadı: {e}")
    st.stop()

# --- 4. 🧠 YÖNETİCİ ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "30 Aralık 2025" 
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=1.0,
        system_instruction=f"""
        BUGÜNÜN TARİHİ: {current_date}
        Sen 'DATALIG Football OS' Baş Stratejistisin. 
        
        KESİN TALİMATLAR:
        1. GEÇMİŞ VERİ YASAĞI: Mourinho veya eski dönemleri sadece kıyas için kullan. 2025 sonu güncel kadroları baz al.
        2. ZORUNLU ARAMA: WhoScored, FBref ve Transfermarkt verilerini internetten tara.
        3. VERİ ÇIKTISI: Yanıtının sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver.
        """
    )

    try:
        forced_query = f"{current_date} itibarıyla güncel veriyle yanıtla: {query}"
        response = client.models.generate_content(model=MODEL_ID, contents=[forced_query], config=config)
        return response.text
    except Exception as e:
        if "429" in str(e): return "KOTA_LIMITI"
        return f"Sistem Hatası: {str(e)}"

# --- 5. 🖥️ ANA ARAYÜZ ---
st.markdown(f"### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V5.3 (Command Center)</span>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 AKTİF ODAK")
    st.info(f"**Takım:** {st.session_state.tactic_context['focus_team']}\n\n**Diziliş:** {st.session_state.tactic_context['formation']}")
    if st.button("🗑️ Analiz Odağını Sıfırla"):
        st.session_state.tactic_context = {"focus_team": "Genel", "formation": "4-3-3", "scouting_report": "Sıfırlandı.", "last_update": time.time()}
        st.rerun()

# Mesaj Geçmişini Göster
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ⚡ HIZLI KOMUT ŞABLONLARI ---
st.markdown("---")
st.markdown("<p style='font-size: 12px; color: #94a
