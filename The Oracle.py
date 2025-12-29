import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time
import uuid

# --- 1. SAYFA VE ARAYÜZ AYARLARI ---
st.set_page_config(
    page_title="DATALIG Oracle Pro V3.5",
    page_icon="⚽",
    layout="wide"
)

# Arka plan ve estetik (DataLig Dark Theme)
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    [data-testid="stSidebar"] { background-color: #0b1426; border-right: 1px solid #1e293b; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

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
        st.markdown("<h2 style='text-align:center; color:white;'>DATALIG COCKPIT</h2>", unsafe_allow_html=True)
        st.text_input("Şifre", type="password", key="password_input")
        st.button("Giriş Yap", on_click=check_login)
    st.stop()

# --- 3. 🚀 API VE MODEL BAĞLANTILARI ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    # Yeni Nesil Google SDK Bağlantısı (Aralık 2025)
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    MODEL_ID = "gemini-3-flash-preview"

    try:
        # Pinecone & Embeddings
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        pinecone_index = pc.Index("regista-arsiv")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db_status, db_color = "ONLINE (GEMINI 3)", "#00e5ff"
    except Exception as e:
        db_status, db_color = "DB ERROR", "#ff4b4b"
else:
    st.error("🚨 API KEY EKSİK! Lütfen .streamlit/secrets.toml dosyasını kontrol edin.")
    st.stop()

# --- 4. 🧠 TAKTİKSEL ANALİZ MOTORU ---
def get_ai_response(user_query, tactical_context):
    # Google Search Grounding Yapılandırması
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # Aralık 2025 "Deep Thinking" ve "Search" Konfigürasyonu
    config = types.GenerateContentConfig(
        tools=[search_tool],
        thinking_config=types.ThinkingConfig(include_thoughts=True),
        temperature=1.0,
        system_instruction=f"""
        Sen 15 yıllık tecrübesi olan bir 'Pro-Lisanslı Futbol Stratejisti ve Baş Analist'sin.
        
        ANALİZ PROTOKOLÜ (Sıkı Uygula):
        1. GÜNCEL KADRO TARAMASI: Google Search kullanarak takımın son 3-4 resmi maçındaki (Aralık 2025 itibarıyla) İLK 11'lerini ve giren-çıkan oyuncuları tespit et.
        2. SAKATLIK/CEZA KONTROLÜ: Tespit ettiğin oyuncuların güncel sakatlık ve ceza durumlarını haber kaynaklarından doğrula. Sakat oyuncuyu öneri olarak sunma.
        3. TAKTİKSEL HARMANLAMA: Arşivdeki Bundesliga verilerini (Dortmund, Leverkusen taktikleri vb.) bir 'zeka katmanı' olarak kullan. Güncel oyuncuların bu taktiklere uyumunu analiz et.
        
        ARŞİVDEKİ TAKTİKSEL PRENSİPLER (Öğrenme Seti):
        {tactical_context}
        
        CEVAP FORMATI:
        - Giriş: Kısa bir güncel durum özeti (Son maçlar baz alınarak).
        - Analiz: Taktiksel eşleşme ve nedenleri.
        - Uyarı: Varsa sakatlık/ceza uyarısı.
        - Sonuç: Teknik direktöre net tavsiye.
        """
    )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_query,
        config=config
    )
    return response

# --- 5. 🖥️ ANA EKRAN VE CHAT ---
st.sidebar.markdown(f"""
<div style="padding:10px; border:1px solid {db_color}; border-radius:10px;">
    <p style="margin:0; font-size:12px;">SİSTEM DURUMU</p>
    <h4 style="margin:0; color:{db_color};">{db_status}</h4>
</div>
""", unsafe_allow_html=True)

st.markdown("### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V3.5</span>", unsafe_allow_html=True)
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hazırım hocam. Güncel kadro ve taktiksel arşiv analizi için emrinizdeyim."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Taktiksel analiz sorgusu (Örn: Fenerbahçe'nin güncel hücum hattı analizi)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        
        with st.status("🔍 Veriler Harmanlanıyor (Search + Arşiv)...", expanded=False):
            # 1. Pinecone'dan taktiksel dersleri çek
            query_vector = embeddings.embed_query(prompt)
            results = pinecone_index.query(vector=query_vector, top_k=5, include_metadata=True)
            context = "\n".join([res['metadata']['text'] for res in results['matches']])
            
            # 2. Gemini 3 Flash üretimi
            response = get_ai_response(prompt, context)
            full_response = response.text

        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if st.sidebar.button("🔒 Güvenli Çıkış"):
    st.session_state.authenticated = False
    st.rerun()
