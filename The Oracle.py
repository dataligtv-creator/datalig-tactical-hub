import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="DATALIG Pro Suite",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🔐 GİRİŞ KONTROL MEKANİZMASI ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if st.session_state.password == "datalig2025":
        st.session_state.authenticated = True
    else:
        st.session_state.login_error = "Hatalı şifre teknik direktörüm!"

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.1) 0%, transparent 50%);
        }
        .login-container {
            max-width: 400px; margin: 100px auto; padding: 40px;
            background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px; backdrop-filter: blur(10px); text-align: center;
        }
        .stTextInput input { background-color: #0f172a !important; color: white !important; border: 1px solid rgba(255,255,255,0.1) !important; }
        .stButton button { width: 100%; background-color: #00e5ff !important; color: #0b0f19 !important; border: none; padding: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="font-size: 40px; margin-bottom: 20px;">⚽</div>
            <h2 style="color: white; margin-bottom: 5px;">DATALIG COCKPIT</h2>
            <p style="color: #94a3b8; font-size: 14px;">Advanced Tactical Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Şifre", type="password", key="password", on_change=check_login)
        st.button("Giriş Yap", on_click=check_login)
        if 'login_error' in st.session_state:
            st.error(st.session_state.login_error)
    st.stop()

# --- 🚀 ANA UYGULAMA BAŞLANGICI ---

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid rgba(255,255,255,0.1); }
    .stTextInput input { background-color: #0f172a !important; color: white !important; border-color: rgba(255,255,255,0.1) !important; }
    [data-testid="stChatMessage"] { background-color: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; }
    a { color: #00e5ff !important; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col1, col2 = st.columns([1, 12])
with col1:
    st.markdown("<h1 style='color:#00e5ff; text-align:center;'>D</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("### DATALIG <span style='font-weight:300; color:#94a3b8;'>PRO SUITE</span>", unsafe_allow_html=True)
st.markdown("---")

# --- API AYARLARI ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # MODELİ ÖNBELLEĞE ALIYORUZ (HATA 429 ÇÖZÜMÜ)
    @st.cache_resource
    def get_model():
        # En stabil ve kota dostu model: 1.5 Flash
        return genai.GenerativeModel('gemini-1.5-flash')
    
    model = get_model()

    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index_name = "regista-arsiv"
        pinecone_index = pc.Index(index_name)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db_status = "ONLINE"
        db_color = "#00e5ff" 
    except Exception as e:
        pinecone_index = None
        db_status = "OFFLINE"
        db_color = "#ef4444" 
else:
    st.error("🚨 API KEY EKSİK! Lütfen Secrets ayarlarını kontrol et.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 10px; background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.1); border-radius: 8px; margin-bottom: 20px;">
        <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #94a3b8;">SYSTEM STATUS</div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
            <div style="width: 8px; height: 8px; background-color: {db_color}; border-radius: 50%; box-shadow: 0 0 10px {db_color};"></div>
            <div style="font-weight: bold; color: white;">{db_status}</div>
        </div>
