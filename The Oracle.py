import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
import time

# --- 1. SAYFA VE GLOBAL BELLEK AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# Diğer sayfaların (Tactical Board, Scout DNA) okuyacağı merkezi veri deposu
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Genel",
        "formation": "4-3-3",
        "scouting_report": "Henüz bir analiz yapılmadı.",
        "last_update": time.time()
    }

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
        st.markdown("<h2 style='text-align:center;'>DATALIG COCKPIT</h2>", unsafe_allow_html=True)
        st.text_input("Şifre", type="password", key="password_input")
        st.button("Giriş Yap", on_click=check_login)
    st.stop()

# --- 3. 🚀 SİSTEM BAŞLATMA ---
@st.cache_resource
def init_system():
    # Gemini 2.5 Flash: 2025'in en stabil ve internet tarama yeteneği yüksek modeli
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

# --- 4. 🧠 YÖNETİCİ ANALİZ MOTORU (ZAMAN ODAKLI) ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "29 Aralık 2025" # Zaman sapmasını önlemek için tarih mühürleme
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=1.0,
        system_instruction=f"""
        BUGÜNÜN TARİHİ: {current_date}
        Sen 'DATALIG Football OS' Baş Stratejistisin. 
        
        KESİN TALİMATLAR:
        1. MOURINHO ÖNCESİ VERİLER: Geçmiş verileri sadece karşılaştırma için kullan. 2025 sonu kadrosunu (Örn: Archie Brown, Kostić, güncel sakatlıklar) baz al.
        2. ZORUNLU ARAMA: Eğer sorgu güncel bir takım/oyuncu hakkındaysa, WhoScored, FBref ve Transfermarkt verilerini internetten tara.
        3. ANALİZ DERİNLİĞİ: Arşivindeki ({archive_context}) Premier Lig ve La Liga taktiksel standartlarını bir IQ katmanı olarak kullanarak analiz yap.
        4. VERİ ÇIKTISI: Yanıtının sonunda mutlaka [TEAM: ..., FORMATION: ...] şeklinde bir teknik özet bırak.
        """
    )

    try:
        # Arama sorgusuna tarihi ekleyerek güncelliği zorluyoruz
        forced_query = f"{current_date} itibarıyla güncel veriyle yanıtla: {query}"
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[forced_query],
            config=config
        )
        return response.text
    except Exception as e:
        if "429" in str(e): return "KOTA_LIMITI"
        return f"Sistem Hatası: {str(e)}"

# --- 5. 🖥️ ANA ARAYÜZ ---
st.markdown(f"### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V5.2 (Merkezi Beyin)</span>", unsafe_allow_html=True)

# SIDEBAR: MEVCUT DURUM TAKİBİ
with st.sidebar:
    st.markdown("### 🎯 AKTİF TAKTİKSEL ODAK")
    st.info(f"**Takım:** {st.session_state.tactic_context['focus_team']}\n\n"
            f"**Diziliş:** {st.session_state.tactic_context['formation']}")
    
    if st.button("🗑️ Analiz Odağını Sıfırla"):
        st.session_state.tactic_context = {"focus_team": "Genel", "formation": "4-3-3", "scouting_report": "Sıfırlandı.", "last_update": time.time()}
        st.rerun()

# CHAT GEÇMİŞİ
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# KULLANICI GİRİŞİ
if prompt := st.chat_input("Taktiksel sorgunuzu girin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 İnternet ve Arşiv Verileri Harmanlanıyor...", expanded=False):
            # 1. Pinecone Arşiv Sorgusu (Taktiksel IQ için)
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            
            # 2. AI Analizi (Zaman Odaklı)
            analysis = get_manager_analysis(prompt, archive)

        if analysis == "KOTA_LIMITI":
            st.warning("⚠️ Google API Kotası doldu. Lütfen 60 saniye bekleyin.")
        else:
            st.markdown(analysis)
            st.session_state.messages.append({"role": "assistant", "content": analysis})
            
            # --- 🤖 AKILLI BAĞLAM GÜNCELLEME (DİĞER SAYFALAR İÇİN) ---
            # Modelin cevabından veya sorudan kritik kelimeleri ayıklıyoruz
            if "Fenerbahçe" in analysis or "Fenerbahçe" in prompt:
                st.session_state.tactic_context['focus_team'] = "Fenerbahçe"
            elif "Galatasaray" in analysis:
                st.session_state.tactic_context['focus_team'] = "Galatasaray"
            
            # Formasyon Tespiti
            for f in ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2", "3-4-3"]:
                if f in analysis or f in prompt:
                    st.session_state.tactic_context['formation'] = f
            
            # Raporu sakla (Tactical Board okuyacak)
            st.session_state.tactic_context['scouting_report'] = analysis
            st.session_state.tactic_context['last_update'] = time.time()
            
            st.toast(f"Bağlam Güncellendi: {st.session_state.tactic_context['focus_team']}")

if st.sidebar.button("🔒 Güvenli Çıkış"):
    st.session_state.authenticated = False
    st.rerun()
