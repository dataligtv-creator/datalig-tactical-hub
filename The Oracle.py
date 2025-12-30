import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
import time

# --- 1. SAYFA VE GLOBAL BELLEK AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

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

# --- 4. 🧠 YÖNETİCİ ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "30 Aralık 2025" 
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=1.0,
        system_instruction=f"""
        BUGÜNÜN TARİHİ: {current_date}
        Sen 'DATALIG Football OS' Baş Stratejistisin. 
        
        KESİN TALİMATLAR:
        1. GEÇMİŞ VERİ YASAĞI: Mourinho veya eski dönemleri sadece kıyas için kullan. 2025 sonu güncel kadroları baz al.
        2. ZORUNLU ARAMA: WhoScored, FBref ve Transfermarkt verilerini internetten tara.
        3. VERİ ÇIKTISI: Yanıtının sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver.
        """
    )

    try:
        forced_query = f"{current_date} itibarıyla güncel veriyle yanıtla: {query}"
        response = client.models.generate_content(model=MODEL_ID, contents=[forced_query], config=config)
        return response.text
    except Exception as e:
        if "429" in str(e): return "KOTA_LIMITI"
        return f"Sistem Hatası: {str(e)}"

# --- 5. 🖥️ ANA ARAYÜZ ---
st.markdown(f"### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V5.3 (Command Center)</span>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 AKTİF ODAK")
    st.info(f"**Takım:** {st.session_state.tactic_context['focus_team']}\n\n**Diziliş:** {st.session_state.tactic_context['formation']}")
    if st.button("🗑️ Analiz Odağını Sıfırla"):
        st.session_state.tactic_context = {"focus_team": "Genel", "formation": "4-3-3", "scouting_report": "Sıfırlandı.", "last_update": time.time()}
        st.rerun()

# Mesaj Geçmişini Göster
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ⚡ HIZLI KOMUT ŞABLONLARI ---
st.markdown("---")
st.markdown("<p style='font-size: 12px; color: #94a3b8; font-weight: bold;'>⚡ TAKTİKSEL ŞABLONLAR</p>", unsafe_allow_html=True)
col_t1, col_t2, col_t3, col_t4 = st.columns(4)

templates = {
    "🔍 Rakip Gözlemi": "Aktif takımı (veya en son konuşulan takımı) analiz et. Son 3 maçına bakarak en zayıf savunma halkasını ve kilit hücum oyuncusunu WhoScored verileriyle raporla.",
    "🛡️ Savunma Reçetesi": "Bu takıma karşı xG üretimini düşürmek için Premier Lig standartlarında bir savunma bloğu ve pres tetikleyicisi (press triggers) öner.",
    "📈 Transfer Uyumu": "Gündemdeki oyuncunun (Örn: Archie Brown) mevcut taktiksel sistemimize (4-3-3) uyumunu FBref istatistikleriyle kıyasla.",
    "🏟️ Maç Sonu xG": "Son oynanan maçın xG (Gol Beklentisi) verilerini tara. Üretilen fırsatların kalitesini ve taktiksel yerleşim hatalarını analiz et."
}

def handle_template(prompt_text):
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.rerun()

with col_t1:
    if st.button("🔍 Rakip Gözlemi", use_container_width=True): handle_template(templates["🔍 Rakip Gözlemi"])
with col_t2:
    if st.button("🛡️ Savunma Reçetesi", use_container_width=True): handle_template(templates["🛡️ Savunma Reçetesi"])
with col_t3:
    if st.button("📈 Transfer Uyumu", use_container_width=True): handle_template(templates["📈 Transfer Uyumu"])
with col_t4:
    if st.button("🏟️ Maç Sonu xG", use_container_width=True): handle_template(templates["🏟️ Maç Sonu xG"])

# --- KULLANICI GİRİŞİ ---
if prompt := st.chat_input("Taktiksel sorgunuzu girin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Yanıt Üretme Mantığı
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_prompt = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.status("🔍 Veriler İşleniyor...", expanded=False):
            vec = embeddings.embed_query(last_prompt)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            analysis = get_manager_analysis(last_prompt, archive)

        if analysis == "KOTA_LIMITI":
            st.warning("⚠️ Kota doldu. 60sn bekleyin.")
        else:
            st.markdown(analysis)
            st.session_state.messages.append({"role": "assistant", "content": analysis})
            
            # Bağlam Güncelleme
            if "Fenerbahçe" in analysis or "Fenerbahçe" in last_prompt: st.session_state.tactic_context['focus_team'] = "Fenerbahçe"
            for f in ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"]:
                if f in analysis or f in last_prompt: st.session_state.tactic_context['formation'] = f
            
            st.session_state.tactic_context['scouting_report'] = analysis
            st.toast(f"Odak: {st.session_state.tactic_context['focus_team']}")
            st.rerun()
