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
    # ŞİFRE KONTROLÜ
    if st.session_state.password == "datalig2025":
        st.session_state.authenticated = True
        # BURADAKİ st.rerun() SİLİNDİ, ARTIK UYARI VERMEYECEK.
    else:
        st.session_state.login_error = "Hatalı şifre teknik direktörüm!"

# --- EĞER GİRİŞ YAPILMADIYSA -> LOGIN EKRANI GÖSTER ---
if not st.session_state.authenticated:
    # Login CSS Tasarımı
    st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.1) 0%, transparent 50%);
        }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
            text-align: center;
        }
        .login-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: white;
            font-size: 24px;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }
        .login-subtitle {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 30px;
        }
        .stTextInput input {
            background-color: #0f172a !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 8px;
            padding: 10px;
        }
        .stTextInput input:focus {
            border-color: #00e5ff !important;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important;
        }
        .stButton button {
            width: 100%;
            background-color: #00e5ff !important;
            color: #0b0f19 !important;
            font-weight: bold;
            border: none;
            padding: 12px;
            transition: all 0.3s;
        }
        .stButton button:hover {
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.5);
            transform: scale(1.02);
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="font-size: 40px; margin-bottom: 20px;">⚽</div>
            <div class="login-title">DATALIG COCKPIT</div>
            <div class="login-subtitle">Advanced Tactical Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Callback kullanımı (Enter'a basınca veya butona tıklayınca check_login çalışır)
        st.text_input("Şifre", type="password", key="password", placeholder="Access Key...", on_change=check_login)
        st.button("Sisteme Giriş Yap", on_click=check_login)
        
        if 'login_error' in st.session_state:
            st.error(st.session_state.login_error)
            
    st.stop() 

# --- 🚀 ANA UYGULAMA ---

# --- 🎨 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    :root { --primary-color: #00e5ff; --bg-color: #0b0f19; --surface-color: rgba(15, 23, 42, 0.6); --border-color: rgba(255, 255, 255, 0.1); }
    .stApp { background-color: var(--bg-color); background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 40px 40px; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: white !important; letter-spacing: -0.02em; }
    code, .stCodeBlock, .stMetricValue { font-family: 'JetBrains Mono', monospace !important; }
    [data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid var(--border-color); }
    .stTextInput input { background-color: #0f172a !important; border: 1px solid var(--border-color) !important; color: white !important; border-radius: 8px; font-family: 'Inter', sans-serif; }
    .stTextInput input:focus { border-color: var(--primary-color) !important; box-shadow: 0 0 15px rgba(0, 229, 255, 0.15) !important; }
    .stButton button { background-color: rgba(0, 229, 255, 0.05); color: var(--primary-color); border: 1px solid rgba(0, 229, 255, 0.2); font-family: 'JetBrains Mono', monospace; font-size: 14px; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.05em; }
    .stButton button:hover { background-color: var(--primary-color); color: #0b0f19; box-shadow: 0 0 20px rgba(0, 229, 255, 0.4); border-color: var(--primary-color); }
    [data-testid="stChatMessage"] { background-color: rgba(15, 23, 42, 0.4); border: 1px solid var(--border-color); border-radius: 12px; backdrop-filter: blur(10px); }
    [data-testid="chatAvatarIcon-assistant"] { background-color: #1e293b !important; color: var(--primary-color) !important; border: 1px solid rgba(0, 229, 255, 0.2); }
    [data-testid="chatAvatarIcon-user"] { background-color: var(--primary-color) !important; color: #0b0f19 !important; }
    a { color: var(--primary-color) !important; text-decoration: none; }
    a:hover { text-shadow: 0 0 10px rgba(0, 229, 255, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 12])
with col1:
    st.markdown("""
    <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 0 15px rgba(0,0,0,0.5);">
        <span style="color: #00e5ff; font-weight: bold; font-family: 'JetBrains Mono'; font-size: 24px;">D</span>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="display: flex; flex-direction: column;">
        <h1 style="margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 0.05em;">DATALIG <span style="font-weight: 300; opacity: 0.5;">PRO SUITE</span></h1>
        <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #00e5ff; letter-spacing: 0.2em; opacity: 0.8;">TACTICAL INTELLIGENCE HUB v2.5</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# --- API ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
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
    st.error("🚨 API KEY EKSİK!")
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
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🛠️ KONTROL PANELİ")
    st.info("Model: **Gemini 2.5 Flash**")
    st.info("Motor: **HuggingFace**")
    
    if st.button("🔒 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem hazır hocam. Veri akışı başladı."}]

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
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
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
