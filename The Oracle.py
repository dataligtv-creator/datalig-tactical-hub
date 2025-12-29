import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Oracle V4.0", page_icon="⚽", layout="wide")

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

# --- 4. 🌐 GLOBAL TAKTİK TARAYICI (SCOUT-AGENT) ---
def scout_league_trends(league):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    search_query = f"December 2025 {league} tactical analysis, latest team formations and coaching trends"
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=f"Sen bir Global Taktik Analistisin. {league} ligindeki en güncel taktiksel değişimleri, antrenör tercihlerini ve dizilişleri profesyonel bir dille raporla."
    )
    
    response = client.models.generate_content(model=MODEL_ID, contents=search_query, config=config)
    return response.text

# --- 5. 🧠 ANA ANALİZ MOTORU ---
def get_tactical_analysis(query, archive_data):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=0.8,
        system_instruction=f"""
        Sen Pro-Lisanslı bir futbol analistisin. 
        SÜREÇ: 
        1. Google Search ile son 3-4 maçın kadrosunu ve sakatlıkları doğrula.
        2. Bilgiyi şu taktiksel veri tabanıyla harmanla: {archive_data}
        3. Güncel lig trendlerini ve sakatlıkları baz alarak profesyonel bir TD raporu sun.
        """
    )
    response = client.models.generate_content(model=MODEL_ID, contents=query, config=config)
    return response.text

# --- 6. 🖥️ ARAYÜZ ---
st.markdown("### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V4.0</span>", unsafe_allow_html=True)

# --- SIDEBAR: LİG ÖĞRETME MODÜLÜ ---
with st.sidebar:
    st.markdown("### 🌐 GLOBAL ÖĞRENME")
    target_league = st.selectbox("Lig Seç", ["Premier League", "La Liga", "Serie A", "Bundesliga"])
    if st.button(f"⚡ {target_league} Trendlerini Sisteme Öğret"):
        with st.status(f"{target_league} Verileri İşleniyor...", expanded=True):
            trend_report = scout_league_trends(target_league)
            
            # Pinecone'a Kaydet (Sistemin hafızasına ekle)
            vec = embeddings.embed_query(trend_report)
            vector_id = f"trend-{uuid.uuid4()}"
            pinecone_index.upsert(vectors=[{"id": vector_id, "values": vec, "metadata": {"text": trend_report, "source": target_league}}])
            
            st.write(trend_report)
            st.success("Taktiksel DNA başarıyla güncellendi!")

# --- ANA CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Taktiksel sorunuz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 Hibrit Analiz Yapılıyor...", expanded=False):
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=5, include_metadata=True)
            context = "\n".join([m['metadata']['text'] for m in res['matches']])
            analysis = get_tactical_analysis(prompt, context)

        st.markdown(analysis)
        st.session_state.messages.append({"role": "assistant", "content": analysis})
