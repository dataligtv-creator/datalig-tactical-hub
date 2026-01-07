import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SİSTEM AYARLARI VE KİMLİK ---
st.set_page_config(page_title="DATALIG MASTERMIND OS", page_icon="🧠", layout="wide")

# Efsanevi Hocalar Listesi (Sistem Talimatı İçin)
LEGENDS = "Pep Guardiola, Carlo Ancelotti, Sir Alex Ferguson, José Mourinho, Jürgen Klopp, Zinedine Zidane, Diego Simeone, Vicente del Bosque, Luis Enrique, Antonio Conte, Domenico Tedesco"

# YouTube ve Medya Kaynakları
ANALYST_CHANNELS = ["VOLE", "SportsDigitale", "Serbest Sekiz", "Erdal Vahid", "Socrates", "The Coaches Voice", "Tifo Football"]

# --- 2. SESSION STATE (SİSTEM HAFIZASI) ---
if 'context' not in st.session_state:
    st.session_state.context = {
        "focus_team": None,
        "opponent": None,
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "reports": {
            "dna": "Henüz analiz yapılmadı.",
            "drills": "Antrenman programı bekleniyor.",
            "omniscient": "Veri merkezi beklemede.",
            "psyche": "Mental analiz yapılmadı."
        }
    }

# --- 3. GEMINI 2.5 FLASH VE PINECONE BAŞLATMA ---
@st.cache_resource
def init_system():
    try:
        # API Keyleri st.secrets'tan çeker
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        idx = pc.Index("regista-arsiv") # Vektör veritabanı
        embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return client, idx, embeds
    except: return None, None, None

client, pinecone_index, embeddings = init_system()
MODEL_ID = "gemini-2.5-flash" # Mühürlendi

# --- 4. ZEKİ ANALİZ FONKSİYONLARI ---

def master_agent(task, query):
    """
    Tüm modüllerin kullandığı ana beyin fonksiyonu.
    Task'e göre persona değiştirir (Scout, Hoca, Psikolog).
    """
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    if task == "DNA":
        sys_inst = f"Sen Domenico Tedesco ve Luis Enrique'sin. {st.session_state.context['focus_team']} için internetteki (WhoScored, FBref) verileri tara ve rakip zayıf halkalarını sayısal olarak deşifre et."
    elif task == "DRILLS":
        sys_inst = f"Sen Antonio Conte ve Sir Alex Ferguson'sun. Analiz edilen taktiği sahaya yansıtacak 3 somut antrenman drilli (Isınma, Ana Bölüm, Taktik) hazırla."
    elif task == "OMNISCIENT":
        sys_inst = f"Sen {LEGENDS} hibrit zekasına sahip bir Veri Bilimci'sin. xG, PPDA ve sakatlık verilerini bul ve bunları taktiksel bir dille yorumla."
    elif task == "PSYCHE":
        sys_inst = "Sen bir Spor Psikoloğu ve Meteoroloji Uzmanısın. Hoca basın toplantılarını, takımın stres seviyesini ve maç saati hava durumunu analiz et."
    else:
        sys_inst = f"Sen {LEGENDS} birleşimisin."

    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=sys_inst)
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
        return response.text
    except Exception as e: return f"Bağlantı Hatası: {str(e)}"

# --- 5. GÖRSELLEŞTİRME VE UI (SAHA & PANELLER) ---

def render_pitch(phase, formation):
    # Dinamik oklar ve alanlar
    svg_overlay = ""
    if phase == "SET HÜCUMU":
        svg_overlay = """
        <line x1="10%" y1="50%" x2="40%" y2="20%" stroke="#13c8ec" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>
        <line x1="10%" y1="50%" x2="40%" y2="80%" stroke="#13c8ec" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="5,5"/>
        <circle cx="50%" cy="50%" r="60" fill="none" stroke="#13c8ec" stroke-opacity="0.2" stroke-width="2"/>
        """
    elif phase == "SAVUNMA":
        svg_overlay = """
        <rect x="30%" y="20%" width="40%" height="60%" fill="rgba(239,68,68,0.15)" stroke="none"/>
        <line x1="30%" y1="20%" x2="30%" y2="80%" stroke="#ef4444" stroke-width="2"/>
        """
    
    # Basit Piyon Yerleşimi (4-3-3 Örneği)
    players_html = "" # (Buraya daha önceki detaylı piyon kodları gelir)

    html = f"""
    <div style="background:#0f1516; border:2px solid #283639; border-radius:12px; height:600px; position:relative; overflow:hidden;">
        <svg width="100%" height="100%" style="position:absolute; top:0; left:0;">
            <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#13c8ec" /></marker></defs>
            {svg_overlay}
        </svg>
        <div style="position:absolute; bottom:10px; right:10px; color:rgba(255,255,255,0.3); font-size:10px;">MASTERMIND FIELD V2.0</div>
    </div>
    """
    return components.html(html, height=620)

# --- 6. SIDEBAR: KOMUTA MERKEZİ ---
with st.sidebar:
    st.title("🧠 DATALIG OS")
    st.caption(f"Engine: {MODEL_ID}")
    st.markdown("---")

    # A. ODAK VE RAKİP
    st.subheader("📍 HEDEF SEÇİMİ")
    team_list = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Real Madrid", "Man City", "Arsenal"]
    f_team = st.selectbox("Takımımız", options=team_list, index=None, placeholder="Takım Seç...")
    op_team = st.text_input("Rakip Takım", placeholder="Örn: Tottenham")
    
    if f_team: st.session_state.context['focus_team'] = f_team
    if op_team: st.session_state.context['opponent'] = op_team

    st.markdown("---")
    
    # B. OYUN PARAMETRELERİ
    st.subheader("⚙️ PARAMETRELER")
    phase = st.radio("Oyun Fazı", ["SET HÜCUMU", "SAVUNMA", "GEÇİŞ"])
    st.session_state.context['game_phase'] = phase
    
    st.markdown("---")
    
    # C. AKSİYON BUTONLARI (MODÜLLER)
    st.subheader("🚀 ANALİZ MODÜLLERİ")
    
    if st.button("🧬 RAKİP DNA (Tedesco)", disabled=not op_team):
        with st.spinner("Zayıf halkalar taranıyor..."):
            res = master_agent("DNA", f"{op_team} taktiksel zayıflıkları ve son maç istatistikleri.")
            st.session_state.context['reports']['dna'] = res
            
    if st.button("📊 OMNISCIENT DATA (Veri+Yorum)", disabled=not op_team):
        with st.spinner("xG, Sakatlık ve Yorumcu görüşleri harmanlanıyor..."):
            res = master_agent("OMNISCIENT", f"{f_team} vs {op_team} maçı için xG, PPDA, sakatlıklar ve uzman taktik yorumları.")
            st.session_state.context['reports']['omniscient'] = res

    if st.button("🏋️ ANTRENMAN (Conte/SAF)", disabled=not f_team):
        with st.spinner("Driller hazırlanıyor..."):
            res = master_agent("DRILLS", f"{f_team} için {phase} fazına uygun antrenman planı.")
            st.session_state.context['reports']['drills'] = res

    if st.button("⛈️ PSİKOLOJİ & ATMOSFER", disabled=not op_team):
        with st.spinner("Hoca ruh hali ve hava durumu analizi..."):
            res = master_agent("PSYCHE", f"{f_team} ve {op_team} son basın toplantıları analizi ve maç günü hava durumu etkisi.")
            st.session_state.context['reports']['psyche'] = res

# --- 7. ANA EKRAN DÜZENİ ---
col1, col2 = st.columns([4, 6])

with col1:
    st.subheader("📋 MASTERMIND RAPORLARI")
    tab1, tab2, tab3, tab4 = st.tabs(["🧬 DNA", "📊 VERİ", "🏋️ ANTRENMAN", "🧠 MENTAL"])
    
    with tab1: st.info(st.session_state.context['reports']['dna'])
    with tab2: st.success(st.session_state.context['reports']['omniscient'])
    with tab3: st.warning(st.session_state.context['reports']['drills'])
    with tab4: st.error(st.session_state.context['reports']['psyche'])

with col2:
    st.subheader(f"🏟️ TAKTİK SAHA ({st.session_state.context['game_phase']})")
    render_pitch(st.session_state.context['game_phase'], st.session_state.context['formation'])

# Chat Input
if prompt := st.chat_input("Mastermind'a özel bir soru sor..."):
    with st.chat_message("user"): st.write(prompt)
    with st.chat_message("assistant"):
        ans = master_agent("GENERAL", prompt)
        st.write(ans)
