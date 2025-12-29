import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time
import uuid

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
        .stApp { background-color: #0b0f19; background-image: radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.1) 0%, transparent 50%); }
        .login-container { max-width: 400px; margin: 100px auto; padding: 40px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; backdrop-filter: blur(10px); text-align: center; }
        .stTextInput input { background-color: #0f172a !important; color: white !important; border: 1px solid rgba(255,255,255,0.1) !important; }
        .stButton button { width: 100%; background-color: #00e5ff !important; color: #0b0f19 !important; border: none; padding: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="login-container"><div style="font-size: 40px; margin-bottom: 20px;">⚽</div><h2 style="color: white; margin-bottom: 5px;">DATALIG COCKPIT</h2><p style="color: #94a3b8; font-size: 14px;">Advanced Tactical Intelligence</p></div>', unsafe_allow_html=True)
        st.text_input("Şifre", type="password", key="password", on_change=check_login)
        st.button("Giriş Yap", on_click=check_login)
        if 'login_error' in st.session_state:
            st.error(st.session_state.login_error)
    st.stop()

# --- 🚀 ANA UYGULAMA ---

# --- API AYARLARI ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    @st.cache_resource
    def get_model():
        # Senin zaman dilimindeki en stabil model
        return genai.GenerativeModel('gemini-3-flash-preview')
    
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
    st.error("🚨 API KEY EKSİK!")
    st.stop()

# --- 🎨 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stChatMessage"] { background-color: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & SİSTEMİ EĞİT ---
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 10px; background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.1); border-radius: 8px; margin-bottom: 20px;">
        <div style="font-family: 'monospace'; font-size: 12px; color: #94a3b8;">SYSTEM STATUS</div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
            <div style="width: 8px; height: 8px; background-color: {db_color}; border-radius: 50%; box-shadow: 0 0 10px {db_color};"></div>
            <div style="font-weight: bold; color: white;">{db_status}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 🧠 AKTİF ÖĞRENME MODÜLÜ
    st.markdown("### 🧠 SİSTEMİ EĞİT")
    yeni_bilgi = st.text_area("Öğretilecek Bilgi:", placeholder="Örn: Takımımız 70. dakikadan sonra fiziksel olarak düşüyor.")
    kaynak_etiketi = st.text_input("Referans:", value="TD Notu")
    
    if st.button("💾 Hafızaya Kaydet"):
        if yeni_bilgi and pinecone_index:
            with st.spinner("Öğreniliyor..."):
                vektor = embeddings.embed_query(yeni_bilgi)
                vector_id = str(uuid.uuid4())
                pinecone_index.upsert(vectors=[{"id": vector_id, "values": vektor, "metadata": {"text": yeni_bilgi, "source": kaynak_etiketi}}])
                st.success("Sistem bu bilgiyi öğrendi!")
                time.sleep(1)
                st.rerun()

    if st.button("🔒 Çıkış Yap"):
        st.session_state.authenticated = False
        st.rerun()

# --- HEADER ---
st.markdown("### ⚽ DATALIG <span style='font-weight:300; color:#94a3b8;'>ORACLE V2.5</span>", unsafe_allow_html=True)
st.markdown("---")

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem hazır hocam. Hangi oyuncu veya taktik üzerinde çalışıyoruz?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- SORU-CEVAP MEKANİZMASI ---
if prompt := st.chat_input("Taktiksel analiz sorgusu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        
        # 1. HAFIZADAKİ OYUNCUYU ÇEK (Scout DNA'dan gelen)
        secili_oyuncu = st.session_state.get('aktif_oyuncu', "Genel Kadro")
        
        with st.status(f"⚡ {secili_oyuncu} ANALİZ EDİLİYOR...", expanded=False) as status:
            # Pinecone Arama
            soru_vektor = embeddings.embed_query(prompt)
            search_results = pinecone_index.query(vector=soru_vektor, top_k=3, include_metadata=True)
            context = "\n".join([res['metadata']['text'] for res in search_results['matches']])
            kaynaklar = list(set([res['metadata'].get('source', 'Arşiv') for res in search_results['matches']]))
            status.update(label="ANALİZ TAMAMLANDI", state="complete")

        # 2. PROMPT OLUŞTURMA
        prompt_taslagi = f"""
        Sen 'DATALIG AI' adında profesyonel bir futbol analistisin. 
        TEKNİK DİREKTÖRÜN ODAKLANDIĞI OYUNCU: {secili_oyuncu}
        (Kullanıcı 'bu', 'o', 'oyuncu' derse bu ismi kastettiğini bil.)

        ARŞİV BİLGİLERİ:
        {context if context else "Özel bir arşiv notu bulunamadı."}

        SORU: {prompt}
        
        Lütfen analitik ve profesyonel bir dille cevap ver.
        """
        
        try:
            response = model.generate_content(prompt_taslagi)
            ai_response = response.text
            
            # Kaynakları ekle
            if kaynaklar and context:
                ai_response += f"\n\n---\n**📚 Referans:** {', '.join(kaynaklar)}"
            
            msg_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
