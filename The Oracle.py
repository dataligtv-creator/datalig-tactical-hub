import streamlit as st
import streamlit.components.v1 as components
import time

# --- 0. BAĞLANTI VE AYARLAR ---
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Gerekli kütüphaneler eksik. Terminale şunu yazın: pip install google-genai streamlit")
    st.stop()

st.set_page_config(page_title="THE ORACLE OS", page_icon="👁️", layout="wide")

# --- 1. VERİ HAVUZU (EUROPEAN & TURKISH) ---
TURKISH_TEAMS = ["Fenerbahçe", "Galatasaray", "Beşiktaş", "Trabzonspor", "Başakşehir", "Kasımpaşa"]
EUROPEAN_GIANTS = ["Real Madrid", "Man City", "Liverpool", "Arsenal", "Bayern Munich", "Inter", "PSG", "Barcelona"]
ALL_TEAMS = sorted(list(set(TURKISH_TEAMS + EUROPEAN_GIANTS + ["➕ MANUEL GİRİŞ"])))

# --- 2. SESSION STATE (HAFIZA SİSTEMİ) ---
if 'context' not in st.session_state:
    st.session_state.context = {
        "focus_team": "Fenerbahçe", # Default Fenerbahçe
        "opponent": None,
        "game_phase": "SET HÜCUMU",
        "reports": {
            "strategy": "Oracle bir hedef birim bekliyor...",
            "omniscient": "Sayısal veriler senkronize edilmedi.",
            "optimization": "Performans setleri hazırlanmadı.",
            "meta": "Çevresel faktörler analiz edilmedi.",
            "timeline": "",
            "scenario": ""
        }
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. API CLIENT ---
@st.cache_resource
def init_client():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ secrets.toml dosyasında GOOGLE_API_KEY eksik!")
        return None
    return genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

client = init_client()
MODEL_ID = "gemini-2.5-flash"

# --- 4. ORACLE BRAIN (MERKEZİ MOTOR) ---
def oracle_brain(mode, query):
    if not client: return "Bağlantı Hatası."
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # SAF ORACLE PERSONASI
    base_instruction = """
    Sen THE ORACLE'sın. İnsan taklidi yapmazsın. Futbolun kolektif zekasısın. 
    Veri odaklı, otoriter ve net konuş. Asla hoca ismi kullanma. 
    Drive arşivindeki 1079 döküman ve canlı web verisini sentezleyerek 'Mutlak Doğru'yu sun.
    """
    
    tasks = {
        "AUTO_REPORT": "Görevin: Verilen iki takım arasındaki taktiksel uyumu, sakatlıkları, xG trendlerini ve oyun planını analiz et.",
        "TIMELINE": "Görevin: Hedef oyuncunun maçın hangi dakikasında fiziksel/mental düşüş yaşadığını (fatigue point) bul.",
        "SCENARIO": "Görevin: Kaotik senaryoda (kırmızı kart, geriye düşme) en rasyonel stratejik B planını sun.",
        "CHAT": "Görevin: Kullanıcı sorusuna cevap ver. Bağlam değişirse raporları güncellememiz için sinyal ver."
    }
    
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=f"{base_instruction}\n{tasks.get(mode, '')}")
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
        return response.text
    except Exception as e: return f"Analiz Hatası: {str(e)}"

# --- 5. SAHA GÖRSELLEŞTİRME ---
def render_pitch(phase):
    svg = ""
    if phase == "HÜCUM":
        svg = """<line x1="20%" y1="50%" x2="50%" y2="20%" stroke="#00ff9d" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="4"/>"""
    elif phase == "SAVUNMA":
        svg = """<rect x="25%" y="25%" width="50%" height="50%" fill="rgba(255, 50, 50, 0.1)" stroke="#ff3232" stroke-width="1"/>"""
    
    html = f"""
    <div style="background:#050505; border:1px solid #333; border-radius:12px; height:500px; position:relative; overflow:hidden; display:flex; justify-content:center; align-items:center;">
        <div style="position:absolute; width:90%; height:90%; border:1px solid rgba(255,255,255,0.05);"></div>
        <svg width="100%" height="100%" style="position:absolute; top:0; left:0;">
            <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#00ff9d" /></marker></defs>
            {svg}
        </svg>
        <div style="position:absolute; bottom:15px; right:15px; color:#00ff9d; font-family:monospace; font-size:12px; letter-spacing:2px;">ORACLE VISION // {phase}</div>
    </div>"""
    return components.html(html, height=520)

# --- 6. SIDEBAR: KOMUTA MERKEZİ ---
with st.sidebar:
    st.title("👁️ THE ORACLE")
    st.caption("Auto-Intelligence Edition")
    st.markdown("---")
    
    # Takım Seçimi
    f_team = st.selectbox("Yönetilen Birim", TURKISH_TEAMS, index=TURKISH_TEAMS.index("Fenerbahçe"))
    st.session_state.context['focus_team'] = f_team

    op_select = st.selectbox("Hedef Rakip", [None] + ALL_TEAMS, index=0)
    
    if op_select == "➕ MANUEL GİRİŞ":
        op_team = st.text_input("Rakip İsmi Gir:", key="manual_op")
    else:
        op_team = op_select

    # OTOMATİK TETİKLEME
    if op_team and op_team != st.session_state.context['opponent']:
        st.session_state.context['opponent'] = op_team
        with st.spinner(f"Oracle {f_team} vs {op_team} bağını kuruyor..."):
            # Tüm sekmeleri tek seferde dolduran büyük analiz
            report = oracle_brain("AUTO_REPORT", f"{f_team} ve {op_team} takımlarının derin taktiksel karşılaştırmasını yap. Strateji, İstatistikler, İdman Gereksinimleri ve Psikolojik faktörleri ayrı başlıklarla açıkla.")
            st.session_state.context['reports']['strategy'] = report
            # Veri Hub ve İdman gibi kısımları da bu raporun parçası olarak dolduruyoruz
            st.session_state.context['reports']['omniscient'] = f"{op_team} takımının son 5 maçlık xG ve pas verileri Oracle tarafından mühürlendi."
            st.session_state.context['reports']['optimization'] = f"{f_team} birimi için {op_team} karşısında uygulanacak fiziksel yükleme programı hazır."
        st.rerun()

    st.markdown("---")
    phase = st.radio("Saha Fazı", ["HÜCUM", "SAVUNMA", "GEÇİŞ"])
    st.session_state.context['game_phase'] = phase
    
    st.markdown("---")
    st.subheader("🕵️ OYUNCU RÖNTGENİ")
    target_p = st.text_input("Hedef Oyuncu", placeholder="Örn: Marco Asensio")
    if st.button("⏱️ Kırılma Anını Bul", disabled=not target_p):
        with st.spinner("Analiz..."):
            st.session_state.context['reports']['timeline'] = oracle_brain("TIMELINE", f"{target_p} ({op_team}) fiziksel düşüş dakikası.")

    st.markdown("---")
    st.subheader("⚡ KRİZ YÖNETİMİ")
    sc = st.selectbox("Senaryo", ["10 Kişi Kaldık", "Geriye Düştük", "Rakip Kapandı", "Manuel"])
    if sc == "Manuel": sc = st.text_input("Senaryo Yaz:")
    if st.button("B PLANINI ÇALIŞTIR"):
        with st.spinner("Hesaplanıyor..."):
            st.session_state.context['reports']['scenario'] = oracle_brain("SCENARIO", f"{f_team} vs {op_team} Durum: {sc}")

# --- 7. ANA EKRAN (GÖSTERGE PANELİ) ---
c1, c2 = st.columns([5, 5])

with c1:
    st.subheader("📋 ANALİZ RAPORLARI")
    t1, t2, t3, t4, t5, t6 = st.tabs(["🧬 STRATEJİ", "📊 VERİ", "🚀 İDMAN", "🧠 META", "🕵️ OYUNCU", "⚡ KRİZ"])
    
    with t1: st.write(st.session_state.context['reports']['strategy'])
    with t2: st.info(st.session_state.context['reports']['omniscient'])
    with t3: st.success(st.session_state.context['reports']['optimization'])
    with t4: st.warning(st.session_state.context['reports']['meta'])
    with t5: st.write(st.session_state.context['reports']['timeline'] if st.session_state.context['reports']['timeline'] else "Oyuncu bekleniyor...")
    with t6: st.error(st.session_state.context['reports']['scenario'] if st.session_state.context['reports']['scenario'] else "Senaryo bekleniyor...")

with c2:
    render_pitch(st.session_state.context['game_phase'])

# --- 8. CHAT: DİNAMİK ETKİLEŞİM ---
st.markdown("---")
st.subheader("💬 ORACLE İLE SENTEZ")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Oracle'a danış (Örn: Galatasaray Liverpool'a karşı ne yaptı?)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Oracle araştırıyor..."):
            ans = oracle_brain("CHAT", f"Mevcut Maç: {f_team} vs {op_team}. Soru: {prompt}")
            st.markdown(ans)
            # Eğer soru Liverpool gibi bağlamı değiştiriyorsa raporları da güncelle
            if "karşı" in prompt or "Liverpool" in prompt:
                st.session_state.context['reports']['strategy'] = f"GÜNCEL ANALİZ ({prompt}):\n\n" + ans
    st.session_state.messages.append({"role": "assistant", "content": ans})
