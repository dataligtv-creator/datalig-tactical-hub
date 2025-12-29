import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid

# --- 🧠 SPORTİF YAZILIM MİMARİSİ AYARLARI ---
st.set_page_config(page_title="DATALIG Oracle Pro", page_icon="⚽", layout="wide")

# --- 🚀 YENİ NESİL GOOGLE GEN AI SDK (ARALIK 2025) ---
if "GOOGLE_API_KEY" in st.secrets:
    # Yeni SDK ile Client tabanlı yapı
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Model Tanımlama: Gemini 3 Flash (Hız ve PhD seviyesi mantık)
    MODEL_ID = "gemini-3-flash-preview" 

    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        pinecone_index = pc.Index("regista-arsiv")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        st.error(f"Veri tabanı bağlantı hatası: {e}")
else:
    st.error("🚨 API KEY EKSİK!")
    st.stop()

# --- 🛠️ TAKTİKSEL ANALİZ MOTORU ---
def generate_tactical_response(user_query, context_data):
    # Google Search Grounding Yapılandırması
    # Halüsinasyonu önlemek için modelin internetten doğrulama yapmasını sağlar.
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # Taktiksel 'Thinking' Seviyesi (Aralık 2025 özelliği)
    config = types.GenerateContentConfig(
        tools=[search_tool],
        # Modelin yanıt vermeden önce bir 'antrenör' gibi düşünmesini sağlar
        thinking_config=types.ThinkingConfig(include_thoughts=True), 
        temperature=1.0 # Google'ın grounding için önerdiği değer
    )

    # 15 yıllık futbol uzmanı persona'sı ve hibrit veri talimatı
    system_instruction = f"""
    Sen 15 yıllık deneyime sahip bir 'Futbol Stratejisti ve Performans Analisti'sin.
    
    VERİ KULLANIM KURALLARIN:
    1. ÖĞRENME SETİ (ARŞİV): Aşağıdaki Bundesliga verilerini sadece TAKTİKSEL ANLAYIŞI kavramak için kullan. 
       Arşiv Verisi: {context_data}
    
    2. GÜNCEL BİLGİ (SEARCH): Eğer soru güncel bir takım (örn: Fenerbahçe) veya oyuncu hakkındaysa, 
       ASLA arşivdeki Bundesliga verileriyle kısıtlı kalma. Google Search kullanarak EN GÜNCEL ve DOĞRU bilgiyi bul.
    
    3. HARMANLAMA: Bulduğun güncel bilgiyi, arşivdeki taktiksel derinlikle (örn: Rakitic'in 3. bölge hareketliliği prensibi) harmanlayarak profesyonel bir TD raporu sun.
    
    4. GÜVENLİK: Bilmediğin veya internette doğrulanmayan transfer dedikodularına girme. Sadece teknik ve taktik analize odaklan.
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=user_query,
        config=config
    )
    return response

# --- 🖥️ STREAMLIT ARAYÜZÜ (CHAT) ---
st.title("⚽ DATALIG ORACLE PRO")
st.caption("Gemini 3 Flash & Google Search Grounding Entegrasyonu")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Taktiksel bir soru sorun (Örn: Fenerbahçe'nin sol kanat defans zafiyeti nedir?)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Pinecone'dan taktiksel 'öğretici' metinleri çek
        query_vector = embeddings.embed_query(prompt)
        results = pinecone_index.query(vector=query_vector, top_k=3, include_metadata=True)
        taktik_context = "\n".join([res['metadata']['text'] for res in results['matches']])

        # 2. Analizi Üret
        with st.spinner("Analist verileri harmanlıyor..."):
            res = generate_tactical_response(prompt, taktik_context)
            full_response = res.text
            
            # Kaynakça (Citations) eklemesi
            if res.candidates[0].grounding_metadata.search_entry_point:
                full_response += "\n\n**🔍 Doğrulanmış Kaynaklar:** Google Search üzerinden güncel verilerle desteklenmiştir."
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
