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
    
    # MODELİ ÖNBELLEĞE AL (HATA 429 ÇÖZÜMÜ)
    @st.cache_resource
    def get_model():
        return genai.GenerativeModel('gemini-1.5-flash-latest')
    
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

# --- SIDEBAR (HATALI KISIM DÜZELTİLDİ) ---
with st.sidebar:
    # f-string içindeki HTML'i düzgünce hizaladık
    sidebar_html = f"""
    <div style="padding: 10px; background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.1); border-radius: 8px; margin-bottom: 20px;">
        <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #94a3b8;">SYSTEM STATUS</div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
            <div style="width: 8px; height: 8px; background-color: {db_color}; border-radius: 50%; box-shadow: 0 0 10px {db_color};"></div>
            <div style="font-weight: bold; color: white;">{db_status}</div>
        </div>
    </div>
    """
    st.markdown(sidebar_html, unsafe_allow_html=True)
    
    st.markdown("### 🛠️ KONTROL PANELİ")
    st.info("Model: **Gemini 1.5 Flash**")
    st.info("Motor: **HuggingFace**")
    
    if st.button("🔒 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem hazır teknik direktörüm. Analiz verileri emrine amade."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def arsivden_bul(soru):
    if not pinecone_index: return None, []
    try:
        soru_vektor = embeddings.embed_query(soru)
        sonuc = pinecone_index.query(vector=soru_vektor, top_k=4, include_metadata=True)
        metinler = ""
        kaynaklar = []
        for match in sonuc['matches']:
            if 'text' in match['metadata']:
                metinler += match['metadata']['text'] + "\n\n"
                kaynaklar.append(match['metadata'].get('source', 'Unknown'))
        return metinler, list(set(kaynaklar))
    except: return None, []

if prompt := st.chat_input("Taktiksel analiz sorgusu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.status("⚡ VERİ İŞLENİYOR...", expanded=True) as status:
            st.write("Vektör veritabanı taranıyor...")
            context, kaynaklar = arsivden_bul(prompt)
            st.write("Taktiksel desenler eşleştiriliyor...")
            time.sleep(0.3)
            status.update(label="ANALİZ TAMAMLANDI", state="complete", expanded=False)
        
        prompt_taslagi = """
        Sen 'DATALIG AI' adında profesyonel bir futbol analistisin.
        Aşağıdaki arşiv verilerini kullanarak teknik direktör seviyesinde cevap ver.
        
        SORU: {soru}
        ARŞİV: {bilgi}
        """
        final_prompt = prompt_taslagi.format(soru=prompt, bilgi=context if context else "(Veri yok)")
        
        try:
            response = model.generate_content(final_prompt)
            ai_response = response.text
            
            if kaynaklar:
                ai_response += "\n\n<div style='background: rgba(0, 229, 255, 0.05); padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 229, 255, 0.1); margin-top: 15px;'>"
                ai_response += "<div style='font-family: JetBrains Mono; font-size: 12px; color: #00e5ff; margin-bottom: 5px;'>📚 REFERANS DOSYALAR</div>"
                for k in kaynaklar:
                    ai_response += f"<div style='font-size: 12px; color: #94a3b8;'>📄 {k}</div>"
                ai_response += "</div>"
            
            message_placeholder.markdown(ai_response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
