import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time
import uuid

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="DATALIG Pro Suite | Gemini 3",
    page_icon="⚽",
    layout="wide"
)

# --- 🔐 GİRİŞ KONTROLÜ ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if st.session_state.password == "datalig2025":
        st.session_state.authenticated = True
    else:
        st.session_state.login_error = "Hatalı şifre teknik direktörüm!"

if not st.session_state.authenticated:
    # (Login arayüzü kodun aynı kalabilir, burayı hızlı geçiyorum)
    st.text_input("Şifre", type="password", key="password", on_change=check_login)
    st.button("Giriş Yap", on_click=check_login)
    st.stop()

# --- 🚀 API & MODEL YAPILANDIRMASI (ARALIK 2025) ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    @st.cache_resource
    def get_model():
        # ARALIK 2025 GÜNCEL KODU: gemini-3-flash-preview
        # Bu model üst düzey akıl yürütme ve multimodal yeteneklere sahiptir.
        return genai.GenerativeModel(
            model_name='gemini-3-flash-preview',
            # Canlı internet verisiyle halüsinasyonu engelleyen Grounding aracı
            tools=[{"google_search": {}}] 
        )
    
    model = get_model()

    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        pinecone_index = pc.Index("regista-arsiv")
        # Embedding modelini güncel tutuyoruz
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db_status, db_color = "ONLINE (GEMINI 3 READY)", "#00e5ff"
    except Exception:
        db_status, db_color = "OFFLINE", "#ef4444"
else:
    st.error("🚨 API KEY EKSİK!")
    st.stop()

# --- SIDEBAR & SİSTEMİ EĞİT (Aynen Kalabilir) ---
with st.sidebar:
    st.markdown(f"**SİSTEM DURUMU:** <span style='color:{db_color}'>{db_status}</span>", unsafe_allow_html=True)
    if st.button("🔒 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- ANA EKRAN ---
st.markdown("### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V3.0 (Gemini 3 Flash)</span>", unsafe_allow_html=True)
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem Gemini 3 Flash ile güncellendi hocam. Taktik tahtası emrinizde."}]

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
        
        with st.status("⚡ DERİN AKIL YÜRÜTME AKTİF...", expanded=False):
            # 1. Pinecone'dan Arşiv Verisini Çek
            soru_vektor = embeddings.embed_query(prompt)
            search_results = pinecone_index.query(vector=soru_vektor, top_k=10, include_metadata=True)
            context = "\n".join([res['metadata']['text'] for res in search_results['matches']])
            
            # 2. Gemini 3 İçin Gelişmiş Prompt
            # 'thinking' (düşünme) özelliğini tetikleyen yapı
            full_prompt = f"""
            TALİMAT: Sen profesyonel futbol analisti 'DATALIG AI'sın. 
            ARŞİV BİLGİLERİ (Pinecone): {context if context else "Özel veri yok."}
            
            GÖREV: Yukarıdaki arşiv bilgilerini, kendi futbol bilginle ve Google Search üzerinden gelen 
            güncel dünya verileriyle (sakatlıklar, form durumu) birleştirerek derin bir analiz yap.
            
            SORU: {prompt}
            """

        try:
            # Gemini 3 Flash üretimi
            response = model.generate_content(full_prompt)
            ai_response = response.text
            
            msg_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error(f"Sistem Hatası: {e}. Lütfen model ismini kontrol edin.")
