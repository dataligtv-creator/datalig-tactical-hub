import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
from PIL import Image

# --- 1. SAYFA VE BELLEK AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# Tüm sayfalar arası veri paylaşımı için ortak bellek (Shared Session State)
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Genel",
        "formation": "Bilinmiyor",
        "scouting_report": "",
        "last_update": ""
    }

@st.cache_resource
def init_system():
    # Gemini 2.5 Flash: Ücretsiz kota için en kararlı ve internet tarama yeteneği yüksek model
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

try:
    client, pinecone_index, embeddings = init_system()
    MODEL_ID = "gemini-2.5-flash"
except Exception as e:
    st.error(f"Sistem başlatılamadı: {e}")
    st.stop()

# --- 2. 🧠 YÖNETİCİ ANALİZ MOTORU (ZORUNLU ARAŞTIRMA) ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=1.0, # Güncel veriyi yorumlaması için esneklik sağladık
        system_instruction=f"""
        Sen 'DATALIG Football OS' sisteminin Baş Stratejistisin. 
        
        KRİTİK TALİMATLAR:
        1. 'Bilmiyorum' veya 'Arşivimde yok' demek KESİNLİKE YASAKTIR.
        2. Eğer bir bilgi (örn: Fenerbahçe'nin güncel durumu) arşivinde ({archive_context}) yoksa, 
           DERHAL Google Search kullanarak WhoScored, FBref ve haber kaynaklarını tara.
        3. Aralık 2025 itibarıyla güncel kadroyu, sakatlıkları ve son maç dizilişlerini öğren.
        4. Taktiksel yorumunu yaparken arşivdeki Premier Lig/La Liga standartlarını bir IQ katmanı olarak kullan.
        
        YANIT FORMATI:
        - ANALİZ: İnternet verileriyle güncel durum teşhisi.
        - TAKTİKSEL REÇETE: Arşivdeki elit taktiklerle harmanlanmış çözüm.
        - ODAK GÜNCELLEMESİ: Cevabın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver.
        """
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[query],
            config=config
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "KOTA_LIMITI"
        return f"Hata: {str(e)}"

# --- 3. 🖥️ ARAYÜZ ---
st.markdown(f"### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V5.1</span>", unsafe_allow_html=True)

# SIDEBAR: BAĞLAM YÖNETİMİ
with st.sidebar:
    st.markdown("### 🎯 SİSTEM ODAĞI")
    st.info(f"**Takım:** {st.session_state.tactic_context['focus_team']}\n\n"
            f"**Diziliş:** {st.session_state.tactic_context['formation']}")
    
    if st.button("🗑️ Analiz Odağını Sıfırla"):
        st.session_state.tactic_context = {"focus_team": "Genel", "formation": "Bilinmiyor", "scouting_report": "", "last_update": ""}
        st.rerun()

# ANA CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Taktiksel sorunuz (Örn: Fenerbahçe'nin güncel sol bek analizi)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 İnternet ve Arşiv Verileri Harmanlanıyor...", expanded=False):
            # 1. Arşiv Sorgusu
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            
            # 2. AI Analizi (Zorunlu Search)
            analysis = get_manager_analysis(prompt, archive)

        if analysis == "KOTA_LIMITI":
            st.warning("⚠️ Kota doldu. 60 sn sonra tekrar deneyin.")
        else:
            st.markdown(analysis)
            st.session_state.messages.append({"role": "assistant", "content": analysis})
            
            # --- 🤖 AKILLI BAĞLAM GÜNCELLEME ---
            # Basit metin analizi ile takımı ve dizilişi yakalıyoruz
            if "Fenerbahçe" in analysis or "Fenerbahçe" in prompt:
                st.session_state.tactic_context['focus_team'] = "Fenerbahçe"
            if "4-3-3" in analysis or "4-3-3" in prompt:
                st.session_state.tactic_context['formation'] = "4-3-3"
            elif "3-5-2" in analysis:
                st.session_state.tactic_context['formation'] = "3-5-2"
                
            st.session_state.tactic_context['scouting_report'] = analysis
