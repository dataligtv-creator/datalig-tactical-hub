import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
# DİKKAT: Artık GoogleEmbeddings değil, HuggingFace kullanıyoruz
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Regista Tactical Hub", page_icon="⚽", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    h1 {color: #ff4b4b;}
    .stChatMessage {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("⚽ Regista Tactical Hub")
st.caption("AI Destekli Taktik Analiz & Arşiv Uzmanı")

# --- API KURULUMLARI ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    # 1. Gemini (Sohbet için)
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # 2. Pinecone ve Embedding (Arşiv için)
    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index_name = "regista-arsiv"
        pinecone_index = pc.Index(index_name)
        
        # KRİTİK NOKTA: Colab'deki motorun AYNISI olmak zorunda!
        # model_name="sentence-transformers/all-MiniLM-L6-v2"
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        db_status = "🟢 Arşiv Bağlı (HuggingFace Motoru)"
    except Exception as e:
        pinecone_index = None
        db_status = f"🔴 Arşiv Hatası: {e}"
else:
    st.error("🚨 API Anahtarları Eksik!")
    st.stop()

# --- YAN MENÜ ---
with st.sidebar:
    st.header("Saha Kenarı")
    st.info(f"Durum: {db_status}")
    st.markdown("---")
    st.markdown("**Nasıl Kullanılır?**")
    st.markdown("1. Sorunu yaz (Örn: 'Gegenpressing nedir?')")
    st.markdown("2. Sistem arşivden tarayıp cevaplar.")

# --- SOHBET ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Taktik tahtası hazır hocam. Hangi analize bakalım?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ARŞİV ARAMA FONKSİYONU ---
def arsivden_bul(soru):
    if not pinecone_index:
        return None, []
    
    try:
        # Soruyu vektöre çevir (HuggingFace ile)
        soru_vektor = embeddings.embed_query(soru)
        
        # Pinecone'da ara
        sonuc = pinecone_index.query(
            vector=soru_vektor,
            top_k=3,
            include_metadata=True
        )
        
        metinler = ""
        kaynaklar = []
        for match in sonuc['matches']:
            if 'text' in match['metadata']:
                metinler += match['metadata']['text'] + "\n\n"
                src = match['metadata'].get('source', 'Bilinmeyen')
                kaynaklar.append(src)
        
        return metinler, list(set(kaynaklar))
    except Exception as e:
        return None, []

# --- SOHBET MANTIĞI ---
if prompt := st.chat_input("Sorunu yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 *Arşiv taranıyor...*")
        
        context, kaynaklar = arsivden_bul(prompt)
        
        prompt_taslagi = """
        Sen uzman bir futbol analistisin. Aşağıdaki arşiv bilgilerini kullanarak soruyu yanıtla.
        
        KULLANICI SORUSU: {soru}
        
        ARŞİV BİLGİLERİ:
        {bilgi}
        
        Eğer arşivde bilgi yoksa, genel futbol bilgini kullan ama bunu belirt.
        """
        
        if context:
            final_prompt = prompt_taslagi.format(soru=prompt, bilgi=context)
        else:
            final_prompt = prompt_taslagi.format(soru=prompt, bilgi="(Arşivde bilgi bulunamadı)")

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(final_prompt)
            ai_response = response.text
            
            if kaynaklar:
                ai_response += "\n\n--- \n📚 **Kaynaklar:**\n" + "\n".join([f"- {k}" for k in kaynaklar])
            
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error(f"Hata: {e}")
