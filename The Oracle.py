import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time
import uuid

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Pro Suite", page_icon="⚽", layout="wide")

# --- 🔐 GİRİŞ KONTROLÜ ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if st.session_state.password == "datalig2025":
        st.session_state.authenticated = True
    else:
        st.session_state.login_error = "Hatalı şifre teknik direktörüm!"

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center;'>DATALIG COCKPIT</h2>", unsafe_allow_html=True)
    st.text_input("Şifre", type="password", key="password", on_change=check_login)
    st.button("Giriş Yap", on_click=check_login)
    st.stop()

# --- 🚀 API & MODEL YAPILANDIRMASI (STABLE) ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    @st.cache_resource
    def get_model():
        # Şu anki en kararlı ve uyumlu model
        return genai.GenerativeModel('gemini-2.5-flash')
    
    model = get_model()

    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        pinecone_index = pc.Index("regista-arsiv")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db_status = "SYSTEM ONLINE"
    except Exception:
        db_status = "DB OFFLINE"
else:
    st.error("🚨 API KEY EKSİK!")
    st.stop()

# --- ANA EKRAN ---
st.sidebar.markdown(f"**DURUM:** {db_status}")
st.markdown("### ⚽ DATALIG ORACLE V2.6")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem hazır. Taktik analizine başlayabiliriz."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- SORU-CEVAP MEKANİZMASI ---
if prompt := st.chat_input("Taktiksel analiz sorgusu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        
        # 1. Pinecone Arama
        soru_vektor = embeddings.embed_query(prompt)
        search_results = pinecone_index.query(vector=soru_vektor, top_k=5, include_metadata=True)
        context = "\n".join([res['metadata']['text'] for res in search_results['matches']])
        
        # 2. Prompt
        full_prompt = f"Futbol analisti olarak cevapla.\n\nARŞİV: {context}\n\nSORU: {prompt}"

        try:
            response = model.generate_content(full_prompt)
            msg_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hata: {e}")
