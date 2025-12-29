import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="DATALIG Oracle V3.7", page_icon="⚽", layout="wide")

# --- 2. 🔐 GİRİŞ KONTROLÜ ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center;'>DATALIG COCKPIT</h2>", unsafe_allow_html=True)
    pw = st.text_input("Şifre", type="password", key="login_pw")
    if st.button("Sisteme Giriş"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Erişim Reddedildi!")
    st.stop()

# --- 3. 🚀 SİSTEM BAŞLATMA (GEMINI 2.5 & PINECONE) ---
@st.cache_resource
def init_system():
    # 2025 Unified SDK Kullanımı
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

try:
    client, pinecone_index, embeddings = init_system()
    # 2.5 Flash: 2025'in en stabil ücretsiz kotasına sahip modeli
    MODEL_ID = "gemini-2.5-flash" 
except Exception as e:
    st.error(f"Sistem başlatılamadı: {e}")
    st.stop()

# --- 4. 🧠 TAKTİKSEL ANALİZ MOTORU ---
def get_tactical_analysis(query, archive_data):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=0.8,
        system_instruction=f"""
        Sen Pro-Lisanslı bir futbol analistisin. 
        SÜREÇ: 
        1. Google Search ile takımın/oyuncunun SON 3 MAÇ performansını ve SAKATLIK durumunu bul.
        2. Bu güncel durumu şu taktiksel arşiv verileriyle kıyasla: {archive_data}
        3. Sakat veya cezalı oyuncuları analiz dışı bırak.
        4. Analizi bir antrenör raporu titizliğinde sun.
        """
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=query,
            config=config
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "KOTA_LIMITI"
        return f"Analiz Hatası: {str(e)}"

# --- 5. 🖥️ CHAT ARAYÜZÜ ---
st.markdown("### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V3.7</span>", unsafe_allow_html=True)
st.sidebar.info(f"Aktif Model: {MODEL_ID}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Taktiksel sorgunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 Veri Katmanları İnceleniyor...", expanded=False):
            # Pinecone Vektör Arama
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=4, include_metadata=True)
            context = "\n".join([m['metadata']['text'] for m in res['matches']])
            
            # AI Analizi
            analysis = get_tactical_analysis(prompt, context)

        if analysis == "KOTA_LIMITI":
            st.warning("⚠️ Ücretsiz kota doldu. Lütfen 60 saniye bekleyip tekrar deneyin.")
            st.session_state.messages.pop() # Hatalı girişi temizle
        else:
            st.markdown(analysis)
            st.session_state.messages.append({"role": "assistant", "content": analysis})

if st.sidebar.button("🔒 Çıkış"):
    st.session_state.authenticated = False
    st.rerun()
