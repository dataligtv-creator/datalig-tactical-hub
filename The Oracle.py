import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import time

# --- 1. SİSTEM KİMLİĞİ VE AYARLAR ---
st.set_page_config(page_title="THE ORACLE OS", page_icon="👁️", layout="wide")

# --- 2. GENİŞLETİLMİŞ VERİ HAVUZU ---
TURKISH_TEAMS = ["Fenerbahçe", "Galatasaray", "Beşiktaş", "Trabzonspor", "Başakşehir", "Adana Demirspor"]
EUROPEAN_GIANTS = ["Man City", "Real Madrid", "Bayern Munich", "Liverpool", "Arsenal", "Inter", "Leverkusen"]
UEFA_POOL = ["Man United", "Tottenham", "Porto", "Ajax", "Lyon", "Slavia Prag", "Twente", "AZ Alkmaar", "Rangers"]
ALL_TEAMS = sorted(list(set(TURKISH_TEAMS + EUROPEAN_GIANTS + UEFA_POOL)))

# --- 3. SESSION STATE (SİSTEM HAFIZASI) ---
if 'context' not in st.session_state:
    st.session_state.context = {
        "focus_team": None,
        "opponent": None,
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "reports": {
            "strategy": "",     # Stratejik Çözümleme
            "omniscient": "",   # Veri Sentezi
            "optimization": "", # Antrenman/Performans
            "meta": "",         # Psikoloji/Hava
            "timeline": "",     # Oyuncu Kırılma Noktası
            "scenario": ""      # Kriz/Kaos Yönetimi
        }
    }

# --- 4. GEMINI 2.5 BAĞLANTISI ---
@st.cache_resource
def init_system():
    try:
        # secrets.toml dosyasında GOOGLE_API_KEY tanımlı olmalı
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        return client
    except Exception as e:
        st.error(f"API Bağlantı Hatası: {e}")
        return None

client = init_system()
MODEL_ID = "gemini-2.5-flash"

# --- 5. ORACLE BRAIN: MERKEZİ ZEKA ---
def oracle_brain(mode, query):
    """
    Oracle'ın düşünme motoru. Kişi isimlerinden arındırılmış, 
    saf futbol aklı ve veri bilimini sentezleyen yapı.
    """
    if not client:
        return "⚠️ API Bağlantısı Kurulamadı. Lütfen API Key'i kontrol edin."

    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # ANA SİSTEM TALİMATI (PERSONA)
    base_instruction = """
    Sen THE ORACLE'sın. Hiçbir insanı taklit etmezsin. 
    Sen, futbol tarihinin tüm taktiksel bilgisini, modern veri bilimini (xG, PPDA) 
    ve oyun teorisini birleştiren üstün bir 'Futbol Karar Mekanizması'sın.
    
    Kurallar:
    1. Asla 'Pep şöyle yapardı' deme. 'Veriler ve oyun geometrisi şunu emrediyor' de.
    2. Cevapların net, otoriter ve çözüm odaklı olsun.
    3. İnternetten en güncel verileri (sakatlık, hava durumu, son maç istatistikleri) canlı çek.
    """
    
    # MODA GÖRE ÖZELLEŞMİŞ GÖREVLER
    if mode == "STRATEGY":
        task = "Görevin: Rakibi analiz et, zayıf halkaları bul ve mutlak galibiyet formülünü yaz."
    elif mode == "OMNISCIENT":
        task = "Görevin: xG, PPDA, pas ağları ve küresel analist yorumlarını sentezleyip maçın matematiksel röntgenini çekmek."
    elif mode == "OPTIMIZATION":
        task = "Görevin: Sahadaki taktiksel kurguyu kas hafızasına dönüştürecek bilimsel antrenman setleri hazırlamak."
    elif mode == "META":
        task = "Görevin: Hoca basın toplantılarını, takım stresini ve hava durumunu analiz ederek 'görünmez etkenleri' yönetmek."
    elif mode == "TIMELINE":
        task = "Görevin: Bir fizyolog gibi davranıp, hedef oyuncunun maç içinde fiziksel olarak tükendiği dakikayı tespit etmek."
    elif mode == "SCENARIO":
        task = "Görevin: Bir 'Oyun Yöneticisi' (Game Master) olarak, verilen kaotik senaryoda (kırmızı kart, geriye düşme) en rasyonel B Planını sunmak."
    else:
        task = ""

    full_prompt = f"{base_instruction}\n{task}"
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=full_prompt)
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
        return response.text
    except Exception as e: return f"⚠️ Oracle Analiz Hatası: {str(e)}"

# --- 6. GÖRSELLEŞTİRME (FÜTÜRİSTİK SAHA) ---
def render_pitch(phase):
    # Fazlara göre dinamik SVG çizimleri
    svg = ""
    title = "GENEL GÖRÜNÜM"
    
    if phase == "HÜCUM KURGUSU":
        title = "HÜCUM GEOMETRİSİ"
        svg = """
        <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#00ff9d" /></marker></defs>
        <line x1="20%" y1="50%" x2="50%" y2="20%" stroke="#00ff9d" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="4"/>
        <line x1="20%" y1="50%" x2="50%" y2="80%" stroke="#00ff9d" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="4"/>
        <circle cx="50%" cy="50%" r="60" fill="none" stroke="#00ff9d" stroke-opacity="0.3" stroke-width="2"/>
        """
    elif phase == "SAVUNMA BLOĞU":
        title = "SAVUNMA ORGANİZASYONU"
        svg = """
        <rect x="25%" y="20%" width="50%" height="60%" fill="rgba(255, 50, 50, 0.1)" stroke="#ff3232" stroke-width="1" stroke-dasharray="2"/>
        <line x1="50%" y1="20%" x2="50%" y2="80%" stroke="#ff3232" stroke-width="1"/>
        """
    elif phase == "GEÇİŞ OYUNU":
        title = "GEÇİŞ (TRANSITION)"
        svg = """
        <defs><marker id="bolt" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#facc15" /></marker></defs>
        <line x1="30%" y1="80%" x2="80%" y2="20%" stroke="#facc15" stroke-width="3" marker-end="url(#bolt)"/>
        """

    html = f"""
    <div style="background:#050505; border:1px solid #333; border-radius:12px; height:550px; position:relative; overflow:hidden; display:flex; justify-content:center; align-items:center;">
        <div style="position:absolute; width:90%; height:90%; border:1px solid rgba(255,255,255,0.05);"></div>
        <div style="position:absolute; width:1px; height:100%; background:rgba(255,255,255,0.05);"></div>
        <div style="position:absolute; width:100%; height:1px; background:rgba(255,255,255,0.05);"></div>
        <div style="position:absolute; width:100px; height:100px; border:1px solid rgba(255,255,255,0.05); border-radius:50%;"></div>
        <svg width="100%" height="100%" style="position:absolute; top:0; left:0;">
            {svg}
        </svg>
        <div style="position:absolute; bottom:15px; right:15px; color:#00ff9d; font-family:monospace; font-size:12px; letter-spacing:2px; text-shadow: 0 0 5px #00ff9d;">ORACLE VISION // {title}</div>
    </div>"""
    return components.html(html, height=570)

# --- 7. SIDEBAR: KOMUTA MERKEZİ ---
with st.sidebar:
    st.title("👁️ THE ORACLE")
    st.caption("v.Final | Engine: Gemini 2.5 Flash")
    st.markdown("---")

    # A. HİBRİT TAKIM SEÇİMİ
    st.subheader("⚔️ BİRİM KONFİGÜRASYONU")
    
    # Yönetilen Takım
    f_select = st.selectbox("Yönetilen Birim", TURKISH_TEAMS + ["➕ MANUEL GİRİŞ"])
    if f_select == "➕ MANUEL GİRİŞ":
        f_team = st.text_input("Takım Adı Gir:", key="ft_input")
    else:
        f_team = f_select
    st.session_state.context['focus_team'] = f_team

    # Rakip Takım
    op_select = st.selectbox("Hedef Birim (Rakip)", ALL_TEAMS + ["➕ MANUEL GİRİŞ"])
    if op_select == "➕ MANUEL GİRİŞ":
        op_team = st.text_input("Rakip Adı Gir:", key="op_input")
    else:
        op_team = op_select
    st.session_state.context['opponent'] = op_team
    
    # Durum Kontrolü
    is_ready = (f_team not in [None, ""]) and (op_team not in [None, ""])
    if is_ready:
        st.success(f"ANALİZ: {f_team} vs {op_team}")
    
    st.markdown("---")

    # B. OYUN FAZI
    phase = st.radio("ANALİZ BOYUTU", ["HÜCUM KURGUSU", "SAVUNMA BLOĞU", "GEÇİŞ OYUNU"])
    st.session_state.context['game_phase'] = phase
    st.markdown("---")

    # C. TEMEL ANALİZ BUTONLARI
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧬 STRATEJİ", disabled=not is_ready, use_container_width=True):
            with st.spinner("Oracle strateji geliştiriyor..."):
                st.session_state.context['reports']['strategy'] = oracle_brain("STRATEGY", f"{op_team} takımına karşı {f_team} için mutlak galibiyet stratejisi.")
    with col2:
        if st.button("📊 VERİ HUB", disabled=not is_ready, use_container_width=True):
            with st.spinner("Veri ağları taranıyor..."):
                st.session_state.context['reports']['omniscient'] = oracle_brain("OMNISCIENT", f"{f_team} vs {op_team} maçı için xG, PPDA ve yorumcu analizleri.")
    
    if st.button("🚀 PERFORMANS OPTİMİZASYONU", disabled=not f_team, use_container_width=True):
         with st.spinner("Antrenman algoritmaları çalışıyor..."):
             st.session_state.context['reports']['optimization'] = oracle_brain("OPTIMIZATION", f"{f_team} için {phase} kurgusunu geliştirecek antrenman setleri.")

    if st.button("🧠 META-ANALİZ (Psikoloji/Hava)", disabled=not is_ready, use_container_width=True):
        with st.spinner("Çevresel faktörler hesaplanıyor..."):
            st.session_state.context['reports']['meta'] = oracle_brain("META", f"{f_team} ve {op_team} son durum psikolojik analizi ve maç günü hava durumu.")

    st.markdown("---")
    
    # D. OYUNCU TIMELINE (DEDEKTİF)
    st.subheader("🕵️ ZAMAN ÇİZELGESİ")
    target_player = st.text_input("Hedef Oyuncu", placeholder="Örn: Marco Asensio")
    if st.button("⏱️ Kırılma Anını Bul", disabled=not target_player):
        with st.spinner(f"{target_player} analiz ediliyor..."):
            st.session_state.context['reports']['timeline'] = oracle_brain("TIMELINE", f"{target_player} ({op_team}) maçın hangi dakikalarında fiziksel düşüş yaşıyor?")

    st.markdown("---")

    # E. KRİZ YÖNETİMİ (YENİ MODÜL)
    st.subheader("⚡ KRİZ / SENARYO SİMÜLASYONU")
    scenario_list = ["10 Kişi Kaldık (Kırmızı Kart)", "Skor 1-0 Öndeyiz (Kapanma)", "Skor 0-1 Gerideyiz (Risk)", "Rakip 'Otobüs' Çekti"]
    sc_select = st.selectbox("Senaryo", scenario_list + ["Manuel Senaryo"])
    
    final_sc = sc_select
    if sc_select == "Manuel Senaryo":
        final_sc = st.text_input("Senaryoyu Yaz:", placeholder="Örn: 80. dakikada kalecimiz sakatlandı")
        
    if st.button("B PLANINI ÇALIŞTIR", disabled=not is_ready):
        with st.spinner("Oracle kriz çözümü üretiyor..."):
             st.session_state.context['reports']['scenario'] = oracle_brain("SCENARIO", f"{f_team} vs {op_team} maçında durum: {final_sc}. Bize kurtuluş planını ver.")


# --- 8. ANA EKRAN DÜZENİ ---
main_col1, main_col2 = st.columns([5, 5])

with main_col1:
    st.subheader("📋 ORACLE RAPORLARI")
    # Tüm modüller için sekmeler
    t1, t2, t3, t4, t5, t6 = st.tabs(["🧬 STRATEJİ", "📊 VERİ", "🚀 İDMAN", "🧠 META", "🕵️ OYUNCU", "⚡ KRİZ"])
    
    with t1: st.write(st.session_state.context['reports']['strategy'])
    with t2: st.info(st.session_state.context['reports']['omniscient'])
    with t3: st.success(st.session_state.context['reports']['optimization'])
    with t4: st.warning(st.session_state.context['reports']['meta'])
    with t5: 
        if st.session_state.context['reports']['timeline']:
            st.markdown(f"### 📉 {target_player} PERFORMANS EĞRİSİ")
            st.write(st.session_state.context['reports']['timeline'])
        else: st.write("Oyuncu analizi bekleniyor...")
    with t6:
        if st.session_state.context['reports']['scenario']:
            st.error("🚨 SİMÜLASYON SONUCU")
            st.write(st.session_state.context['reports']['scenario'])
        else: st.write("Senaryo bekleniyor...")

with main_col2:
    st.subheader(f"SAHA SİMÜLASYONU // {st.session_state.context['game_phase']}")
    render_pitch(st.session_state.context['game_phase'])
