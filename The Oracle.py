import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
from PIL import Image
import io

# --- 1. SİSTEM BAŞLATMA ---
st.set_page_config(page_title="DATALIG Oracle V4.5", page_icon="⚽", layout="wide")

@st.cache_resource
def init_system():
    # Gemini 2.5 Flash - Ücretsiz Kotaya Uygun ve Multimodal (Görsel okuyabilir)
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

try:
    client, pinecone_index, embeddings = init_system()
    MODEL_ID = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- 2. 🧠 ANALİZ MOTORU (HİBRİT MANTIK) ---
def get_combined_analysis(query, context, image=None):
    """
    Hem metin, hem arşiv, hem de (varsa) görseli birleştirip analiz eder.
    """
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # Görsel varsa listeye ekle, yoksa sadece metin gönder
    contents = [query]
    if image:
        contents.append(image)

    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=0.8,
        system_instruction=f"""
        Sen Pro-Lisanslı bir 'Futbol Stratejisti'sin. 
        ELİNDEKİ KAYNAKLAR:
        1. ARŞİV VERİSİ: {context} (Taktiksel temel)
        2. GÖRSEL VERİ: (Varsa) Isı haritası, xG tablosu veya diziliş görseli.
        3. GÜNCEL VERİ: Google Search üzerinden son 3-4 maçın sakatlık/kadro bilgisi.

        GÖREV: Görseldeki verileri (xG, ısı haritası, pas yüzdesi vb.) arşivdeki taktiksel 
        prensiplerle harmanla. Eğer görsel bir ısı haritasıysa, oyuncunun saha içi 
        geometrisini yorumla. Sakatlık durumlarını internetten teyit et.
        """
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=config
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "KOTA_LIMITI"
        return f"Hata: {str(e)}"

# --- 3. 🌐 GLOBAL LİG TARAYICI ---
def scout_league_trends(league):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=f"Sen bir Global Taktik Analistisin. {league} ligindeki en güncel 2025/26 taktiksel trendleri raporla."
    )
    response = client.models.generate_content(model=MODEL_ID, contents=f"{league} tactical review", config=config)
    return response.text

# --- 4. 🖥️ ARAYÜZ ---
st.markdown("### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V4.5</span>", unsafe_allow_html=True)

# SIDEBAR: VERİ GİRİŞLERİ
with st.sidebar:
    st.markdown("### 📊 GÖRSEL VERİ ANALİZİ")
    uploaded_file = st.file_uploader("Isı Haritası / xG Görseli Yükle", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    st.markdown("### 🌐 GLOBAL ÖĞRENME")
    target_league = st.selectbox("Lig Seç", ["Premier League", "La Liga", "Serie A", "Bundesliga"])
    if st.button(f"⚡ {target_league} Trendlerini Öğret"):
        with st.status(f"{target_league} Analiz Ediliyor..."):
            report = scout_league_trends(target_league)
            vec = embeddings.embed_query(report)
            pinecone_index.upsert(vectors=[{"id": str(uuid.uuid4()), "values": vec, "metadata": {"text": report, "source": target_league}}])
            st.success("DNA Güncellendi!")

# ANA CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Sorgunuzu yazın veya görsel yükleyin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 Analiz Ediliyor...", expanded=False):
            # 1. Arşivden veri çek
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=5, include_metadata=True)
            context = "\n".join([m['metadata']['text'] for m in res['matches']])
            
            # 2. Görseli hazırla
            image_data = None
            if uploaded_file:
                image_data = Image.open(uploaded_file)
            
            # 3. Hibrit Analiz
            analysis = get_combined_analysis(prompt, context, image_data)

        if analysis == "KOTA_LIMITI":
            st.warning("⚠️ Kota doldu. 60 sn sonra tekrar deneyin.")
        else:
            st.markdown(analysis)
            st.session_state.messages.append({"role": "assistant", "content": analysis})
