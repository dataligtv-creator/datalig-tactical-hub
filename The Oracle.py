import streamlit as st
import streamlit.components.v1 as components
import time

# --- 0. KÜTÜPHANE KONTROLÜ VE AYARLAR ---
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Gerekli kütüphaneler eksik. Lütfen terminalde şunu çalıştırın: pip install google-genai streamlit")
    st.stop()

st.set_page_config(page_title="THE ORACLE OS", page_icon="👁️", layout="wide")

# --- 1. VERİ HAVUZU (GENİŞLETİLMİŞ) ---
TURKISH_TEAMS = ["Fenerbahçe", "Galatasaray", "Beşiktaş", "Trabzonspor", "Başakşehir", "Adana Demirspor", "Samsunspor"]
EUROPEAN_GIANTS = ["Man City", "Real Madrid", "Bayern Munich", "Liverpool", "Arsenal", "Inter", "Leverkusen", "Barcelona", "PSG"]
UEFA_POOL = ["Man United", "Tottenham", "Porto", "Ajax", "Lyon", "Slavia Prag", "Twente", "AZ Alkmaar", "Rangers", "Bodo/Glimt"]
# Hepsini tek listede birleştir
ALL_TEAMS = sorted(list(set(TURKISH_TEAMS + EUROPEAN_GIANTS + UEFA_POOL)))

# --- 2. SİSTEM HAFIZASI (SESSION STATE) ---
if 'context' not in st.session_state:
    st.session_state.context = {
        "focus_team": None,
        "opponent": None,
        "game_phase": "SET HÜCUMU",
        "reports": {
            "strategy": "",     # Strateji Raporu
            "omniscient": "",   # Veri Merkezi
            "optimization": "", # Antrenman
            "meta": "",         # Psikoloji/Hava
            "timeline": "",     # Oyuncu Analizi (Asensio Modu)
            "scenario": ""      # Kriz Senaryosu
        }
    }

# Sohbet Geçmişi (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. GOOGLE GEMINI 2.5 BAĞLANTISI ---
@st.cache_resource
def init_client():
    # API Key kontrolü (.streamlit/secrets.toml dosyasından)
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ API KEY BULUNAMADI! Lütfen secrets.toml dosyasını kontrol edin.")
        return None
    try:
        # Client başlatma
        return genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

client = init_client()
MODEL_ID = "gemini-2.5-flash"

# --- 4. ORACLE BEYNİ (TÜM MODÜLLER BURADA) ---
def oracle_brain(mode, query):
    if not client: return "⚠️ API Bağlantısı Yok."
    
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # KİMLİK: İsimsiz, Kolektif Süper Zeka
    base_instruction = """
    Sen THE ORACLE'sın. İnsan taklidi yapmazsın.
    Futbolun kolektif zekasısın. Duygusuz, veri odaklı ve net konuş.
    Asla 'bence' veya 'Pep şöyle derdi' deme. 'Veriler ve oyun geometrisi şunu emrediyor' de.
    """
    
    # GÖREV TANIMLARI
    tasks = {
        "STRATEGY": "Görevin: Rakibi analiz et, zayıf halkaları bul ve mutlak galibiyet formülünü yaz.",
        "OMNISCIENT": "Görevin: xG, PPDA, sakatlıklar ve küresel yorumcu görüşlerini birleştir.",
        "OPTIMIZATION": "Görevin: Sahadaki taktiksel kurguyu kas hafızasına dönüştürecek bilimsel antrenman setleri hazırla.",
        "META": "Görevin: Hoca basın toplantılarını, takım stresini ve hava durumunu analiz et.",
        "TIMELINE": "Görevin: Bir fizyolog gibi, hedef oyuncunun maçın hangi dakikasında fiziksel/mental düşüş yaşadığını bul.",
        "SCENARIO": "Görevin: Kaotik bir senaryoda (kırmızı kart, geriye düşme) en rasyonel B Planını sun.",
        "CHAT": "Görevin: Kullanıcının sorusuna kısa, net ve stratejik bir cevap ver. Sohbeti sürdür."
    }
    
    task_desc = tasks.get(mode, "Kullanıcıya yardımcı ol.")
    full_prompt = f"{base_instruction}\n{task_desc}"
    
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=full_prompt)
    
    try:
        # Gemini çağrısı
        response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
        return response.text
    except Exception as e: return f"⚠️ Analiz Hatası: {str(e)}"

# --- 5. GÖRSELLEŞTİRME (FÜTÜRİSTİK SAHA) ---
def render_pitch(phase):
    svg_content = ""
    title = phase
    
    # Fazlara göre dinamik çizim
    if phase == "HÜCUM KURGUSU":
        svg_content = """<line x1="20%" y1="50%" x2="50%" y2="20%" stroke="#00ff9d" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="4"/><circle cx="50%" cy="50%" r="60" fill="none" stroke="#00ff9d" stroke-opacity="0.3"/>"""
    elif phase == "SAVUNMA BLOĞU":
        svg_content = """<rect x="25%" y="20%" width="50%" height="60%" fill="rgba(255, 50, 50, 0.1)" stroke="#ff3232" stroke-width="1" stroke-dasharray="2"/>"""
    elif phase == "GEÇİŞ":
        svg_content = """<line x1="30%" y1="80%" x2="80%" y2="20%" stroke="#facc15" stroke-width="3"/>"""
    
    html = f"""
    <div style="background:#050505; border:1px solid #333; border-radius:12px; height:520px; position:relative; overflow:hidden; display:flex; justify-content:center; align-items:center;">
        <div style="position:absolute; width:90%; height:90%; border:1px solid rgba(255,255,255,0.05);"></div>
        <div style="position:absolute; width:1px; height:100%; background:rgba(255,255,255,0.05);"></div>
        <div style="position:absolute; width:100%; height:1px; background:rgba(255,255,255,0.05);"></div>
        <svg width="100%" height="100%" style="position:absolute; top:0; left:0;">
            <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#00ff9d" /></marker></defs>
            {svg_content}
        </svg>
        <div style="position:absolute; bottom:15px; right:15px; color:#00ff9d; font-family:monospace; letter-spacing:2px;">ORACLE // {title}</div>
    </div>"""
    return components.html(html, height=540)

# --- 6. SIDEBAR: KOMUTA MERKEZİ ---
with st.sidebar:
    st.title("👁️ THE ORACLE")
    st.caption("Ultimate Edition")
    st.markdown("---")
    
    # A. HİBRİT TAKIM SEÇİMİ
    st.subheader("⚔️ BİRİM SEÇİMİ")
    
    # Takımım
    f_select = st.selectbox("Yönetilen Takım", TURKISH_TEAMS + ["➕ MANUEL GİRİŞ"])
    f_team = st.text_input("Takım Adı Gir:", key="ft") if f_select == "➕ MANUEL GİRİŞ" else f_select
    st.session_state.context['focus_team'] = f_team

    # Rakip
    op_select = st.selectbox("Rakip Takım", ALL_TEAMS + ["➕ MANUEL GİRİŞ"])
    op_team = st.text_input("Rakip Adı Gir:", key="op") if op_select == "➕ MANUEL GİRİŞ" else op_select
    st.session_state.context['opponent'] = op_team
    
    st.markdown("---")
    
    # B. OYUN FAZI
    phase = st.radio("Analiz Fazı", ["HÜCUM KURGUSU", "SAVUNMA BLOĞU", "GEÇİŞ"])
    st.session_state.context['game_phase'] = phase
    
    is_ready = bool(f_team and op_team)
    
    st.markdown("---")
    
    # C. ANALİZ MODÜLLERİ (BUTONLAR)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧬 STRATEJİ", disabled=not is_ready, use_container_width=True):
            with st.spinner("Oracle düşünüyor..."):
                st.session_state.context['reports']['strategy'] = oracle_brain("STRATEGY", f"{op_team} takımına karşı {f_team} için mutlak galibiyet stratejisi.")
    with col2:
        if st.button("📊 VERİ HUB", disabled=not is_ready, use_container_width=True):
            with st.spinner("Veri taranıyor..."):
                st.session_state.context['reports']['omniscient'] = oracle_brain("OMNISCIENT", f"{f_team} vs {op_team} xG, PPDA ve yorumcu analizleri.")

    if st.button("🚀 PERFORMANS & İDMAN", disabled=not f_team, use_container_width=True):
        with st.spinner("Antrenman yükleniyor..."):
            st.session_state.context['reports']['optimization'] = oracle_brain("OPTIMIZATION", f"{f_team} için antrenman setleri.")

    if st.button("🧠 META-ANALİZ (Psikoloji)", disabled=not is_ready, use_container_width=True):
        with st.spinner("Çevresel analiz..."):
             st.session_state.context['reports']['meta'] = oracle_brain("META", f"{f_team} ve {op_team} psikolojik durum ve hava analizi.")

    st.markdown("---")
    
    # D. OYUNCU TIMELINE (DEDEKTİF)
    st.subheader("🕵️ OYUNCU DEDEKTİFİ")
    target_player = st.text_input("Hedef Oyuncu", placeholder="Örn: Asensio")
    if st.button("⏱️ Kırılma Anını Bul", disabled=not target_player):
        with st.spinner("Fizyolojik analiz..."):
            st.session_state.context['reports']['timeline'] = oracle_brain("TIMELINE", f"{target_player} ({op_team}) maçın hangi dakikalarında düşüş yaşıyor?")

    st.markdown("---")
    
    # E. KRİZ YÖNETİMİ
    st.subheader("⚡ KRİZ SİMÜLASYONU")
    sc_val = st.selectbox("Senaryo Seç", ["10 Kişi Kaldık", "Geriye Düştük", "Rakip Kapandı", "Manuel Giriş"])
    sc_text = st.text_input("Senaryo Yaz") if sc_val == "Manuel Giriş" else sc_val
    
    if st.button("B PLANINI ÇALIŞTIR", disabled=not is_ready):
        with st.spinner("Kurtuluş planı hazırlanıyor..."):
             st.session_state.context['reports']['scenario'] = oracle_brain("SCENARIO", f"{f_team} vs {op_team}, Durum: {sc_text}")

# --- 7. ANA EKRAN (RAPORLAR VE SAHA) ---
c1, c2 = st.columns([5, 5])

with c1:
    st.subheader("📋 ANALİZ RAPORLARI")
    # 6 Sekmeli Rapor Paneli
    tabs = st.tabs(["🧬 STRATEJİ", "📊 VERİ", "🚀 İDMAN", "🧠 META", "🕵️ OYUNCU", "⚡ KRİZ"])
    
    with tabs[0]: st.write(st.session_state.context['reports']['strategy'])
    with tabs[1]: st.info(st.session_state.context['reports']['omniscient'])
    with tabs[2]: st.success(st.session_state.context['reports']['optimization'])
    with tabs[3]: st.warning(st.session_state.context['reports']['meta'])
    with tabs[4]: 
        if st.session_state.context['reports']['timeline']:
            st.markdown(f"**Analiz:** {target_player}")
            st.write(st.session_state.context['reports']['timeline'])
        else: st.caption("Oyuncu analizi bekleniyor...")
    with tabs[5]: 
        if st.session_state.context['reports']['scenario']:
            st.error("🚨 SİMÜLASYON RAPORU")
            st.write(st.session_state.context['reports']['scenario'])
        else: st.caption("Kriz senaryosu bekleniyor...")

with c2:
    # Saha Görseli
    render_pitch(st.session_state.context['game_phase'])

# --- 8. SERBEST SOHBET (EN ALTTA) ---
st.markdown("---")
st.subheader("💬 ORACLE İLE SOHBET ET")

# Geçmiş Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Yeni Mesaj Girişi
if prompt := st.chat_input("Oracle'a strateji hakkında soru sor..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Oracle cevabını üret
    with st.chat_message("assistant"):
        with st.spinner("Oracle düşünüyor..."):
            # CHAT modu
            full_prompt = f"Bağlam: Takım {f_team}, Rakip {op_team}. Kullanıcı Sorusu: {prompt}"
            response = oracle_brain("CHAT", full_prompt)
            st.markdown(response)
    
    # Cevabı kaydet
    st.session_state.messages.append({"role": "assistant", "content": response})
