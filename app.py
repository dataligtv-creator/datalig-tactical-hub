import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Regista Tactical Hub", page_icon="⚽", layout="wide")

# --- CSS İLE GÖRSELLİK ---
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    h1 {color: #ff4b4b;}
    .stChatMessage {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.title("⚽ Regista Tactical Hub")
st.caption("AI Destekli Taktik Analiz & Arşiv Uzmanı")

# --- API KURULUMLARI ---
# Sadece Google ve Pinecone kontrolü yapıyoruz (Firebase YOK)
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    # 1. Google Gemini Kurulumu
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # 2. Pinecone Bağlantısı (Arşiv için)
    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index_name = "regista-arsiv"
        pinecone_index = pc.Index(index_name)
        
        # Embedding modeli
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=st.secrets["GOOGLE_API_KEY"]
        )
        db_status = "🟢 Arşiv Bağlı"
    except Exception as e:
        pinecone_index = None
        db_status = f"🔴 Arşiv Hatası: {e}"
        # Hata olsa bile devam et, en azından sohbet çalışsın

else:
    st.error("🚨 HATA: API Anahtarları Eksik! Lütfen Streamlit Secrets ayarlarını kontrol et.")
    st.info("Gerekli Anahtarlar: GOOGLE_API_KEY, PINECONE_API_KEY")
    st.stop()

# --- YAN MENÜ ---
with st.sidebar:
    st.header("Saha Kenarı")
    st.info(f"Veritabanı Durumu: {db_status}")
    st.markdown("---")
    st.markdown("**Nasıl Kullanılır?**")
    st.markdown("1. Sorunu yaz (Örn: 'Gegenpressing nedir?')")
    st.markdown("2. AI hem bilgisiyle hem de **Bundesliga arşivinden** tarayarak cevaplar.")

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba Hocam! Sahaya hoş geldin. Arşivdeki maç analizleri emrine amade. Ne analiz edelim?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FONKSİYON: Arşivden Bilgi Çek (RAG) ---
def arsivden_bul(soru):
    if not pinecone_index:
        return None, []
    
    try:
        # 1. Soruyu vektöre çevir
        soru_vektor = embeddings.embed_query(soru)
        
        # 2. Pinecone'da en benzer 3 dökümanı bul
        sonuc = pinecone_index.query(
            vector=soru_vektor,
            top_k=3,
            include_metadata=True
        )
        
        # 3. Metinleri birleştir
        bulunan_bilgiler = ""
        kaynaklar = []
        for match in sonuc['matches']:
            if 'text' in match['metadata']:
                bulunan_bilgiler += match['metadata']['text'] + "\n\n"
                # Kaynak ismini düzeltelim (source yoksa text'ten kırp)
                src = match['metadata'].get('source', 'Bilinmeyen Dosya')
                kaynaklar.append(src)
        
        return bulunan_bilgiler, list(set(kaynaklar))
    except Exception as e:
        print(f"Arama Hatası: {e}")
        return None, []

# --- SOHBET MANTIĞI ---
if prompt := st.chat_input("Taktiksel sorunu sor..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan cevabı hazırlanıyor
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 *Arşiv taranıyor...*")
        
        # 1. Önce Arşivden Bilgi Getir
        context_text, kaynaklar = arsivden_bul(prompt)
        
        # 2. Gemini'ye Prompt Hazırla
        base_prompt = """
        Sen 'Regista AI' adında uzman bir futbol analistisin.
        Sana kullanıcının özel arşivinden bulduğumuz metinler verildi.
        
        Kurallar:
        1. Öncelikle 'BULUNAN ARŞİV BİLGİLERİ'ni kullan.
        2. Arşivde bilgi yoksa, kendi bilgini kullan ama bunu belirt.
        3. Profesyonel, taktiksel konuş.
        """
        
        if context_text:
            final_prompt = f"{base_prompt}\n\nKULLANICI SORUSU: {prompt}\n\nBULUNAN ARŞİV BİLGİLERİ:\n{context_text}"
        else:
            final_prompt = f"{base_prompt}\n\nKULLANICI SORUSU: {prompt}\n\n(Arşivde bilgi bulunamadı, genel bilgi ver.)"

        # 3. Modele Sor
        try:
            # Model ismini değiştirebilirsin (gemini-2.0-flash-exp veya gemini-1.5-flash)
            model = genai.GenerativeModel('gemini-2.5-flash') 
            response = model.generate_content(final_prompt)
            ai_response = response.text
            
            # Kaynakları ekle
            if kaynaklar:
                kaynak_notu = "\n\n--- \n📚 **Kaynaklar:**\n" + "\n".join([f"- {k}" for k in kaynaklar])
                ai_response += kaynak_notu
            
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
