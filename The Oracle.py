import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime

# --- 0. BAĞLANTI VE SİSTEM AYARLARI ---
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Kütüphane hatası: pip install google-genai streamlit")
    st.stop()

st.set_page_config(page_title="THE ORACLE OS", page_icon="👁️", layout="wide")

# --- 1. VERİ HAVUZU ---
TURKISH_TEAMS = ["Fenerbahçe", "Galatasaray", "Beşiktaş", "Trabzonspor", "Başakşehir", "Samsunspor", "Eyüpspor"]
ALL_TEAMS = sorted(list(set(TURKISH_TEAMS + ["Real Madrid", "Man City", "Liverpool", "Arsenal", "Bayern Munich", "Barcelona", "Inter"])))

# --- 2. SİSTEM HAFIZASI (SESSION STATE) ---
if 'context' not in st.session_state:
    st.session_state.context = {
        "focus_team": "Fenerbahçe",
        "opponent": None,
        "reports": {
            "strategy": "Oracle hedef bekliyor...",
            "data_hub": "Sayısal analiz yapılmadı.",
            "scenarios": "Kriz varyasyonları hesaplanmadı.",
            "meta": "Psikolojik analiz yok.",
            "training": "İdman seti hazırlanmadı.",
            "timeline": ""
        }
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. API CLIENT ---
@st.cache_resource
def init_client():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("secrets.toml içinde API KEY eksik!")
        return None
    return genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

client = init_client()
MODEL_ID = "gemini-2.5-flash"

# --- 4. ORACLE MODÜLER MOTORU (ANTİ-HALİSÜNASYON & RETRY) ---
def oracle_engine(mode, f_team, op_team, retries=3):
    if not client: return "Bağlantı yok."
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    current_date = datetime.now().strftime("%d %B %Y")
    
    # MODÜLER TALİMATLAR (Her sekme için ayrı uzmanlık ve kesin güncellik)
    instructions = {
        "STRAT": f"Görevin: {f_team} vs {op_team} için ÇOK KISA strateji ver. 1. {f_team} oyun kimliği, 2. {op_team} oyun kimliği, 3. Galibiyet için kilit çözüm. Max 3 kısa paragraf.",
        "DATA": f"Görevin: {f_team} ve {op_team} için {current_date} tarihli GÜNCEL verileri getir. xG, PPDA, sakatlıklar ve son maç sonuçlarını tablo/liste yap. Halüsinasyon görme.",
        "KRİZ": f"Görevin: {op_team} maçında yaşanabilecek 3 somut kriz senaryosu (Örn: Torreira baskısı, Osimhen koşuları) ve her birine B planı üret.",
        "META": f"Görevin: Maç atmosferi, taraftar etkisi ve hava durumunun taktiksel etkisini özetle.",
        "TIMELINE": f"Görevin: {op_team} takımındaki kilit oyuncuların fiziksel/mental düşüş dakikalarını (fatigue point) analiz et.",
        "CHAT": "Sen THE ORACLE'sın. Sorulara kısa, net ve stratejik cevaplar ver."
    }

    base = f"TARİH: {current_date}. Sen THE ORACLE'sın. Futbolun kolektif zekasısın. Kesinlikle güncel kal. İsim taklidi yapma. Yaratıcılığı kısıp (temp=0.1) gerçekliğe odaklan."
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=f"{base}\n{instructions.get(mode, '')}")
    
    for i in range(retries):
        try:
            query = f"{current_date} itibariyle {f_team} ve {op_team} arasındaki derin taktiksel/verisel karşılaştırmayı yap."
            response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
            return response.text
        except Exception as e:
            if "503" in str(e) and i < retries - 1:
                time.sleep(2)
                continue
            return f"⚠️ Veri Senkronizasyon Hatası: {str(e)}"

# --- 5. SAHA GÖRSELLEŞTİRME ---
def render_pitch(phase):
    svg = ""
    if phase == "HÜCUM":
        svg = """<line x1="20%" y1="50%" x2="50%" y2="20%" stroke="#00ff9d" stroke-width="2" marker-end="url(#arrow)" stroke-dasharray="4"/>"""
    elif phase == "SAVUNMA":
        svg = """<rect x="25%" y="25%" width="50%" height="50%" fill="rgba(255, 50, 50, 0.1)" stroke="#ff3232" stroke-width="1"/>"""
    
    html = f"""
    <div style="background:#050505; border:1px solid #333; border-radius:15px; height:480px; position:relative; overflow:hidden; display:flex; justify-content:center; align-items:center;">
        <div style="position:absolute; width:90%; height:90%; border:1px solid rgba(255,255,255,0.05);"></div>
        <svg width="100%" height="100%" style="position:absolute; top:0; left:0;">
            <defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#00ff9d" /></marker></defs>
            {svg}
        </svg>
        <div style="position:absolute; bottom:15px; right:15px; color:#00ff9d; font-family:monospace; font-size:12px;">ORACLE FIELD // {phase}</div>
    </div>"""
    return components.html(html, height=500)

# --- 6. SIDEBAR VE OTOMASYON ---
with st.sidebar:
    st.title("👁️ THE ORACLE")
    st.caption(f"Modular Ultimate | {datetime.now().strftime('%Y')}")
    st.markdown("---")
    
    # Fenerbahçe Default Seçimi
    f_team = st.selectbox("Yönetilen Birim", TURKISH_TEAMS, index=TURKISH_TEAMS.index("Fenerbahçe"))
    st.session_state.context['focus_team'] = f_team

    op_team = st.selectbox("Hedef Rakip", [None] + ALL_TEAMS, index=0)

    # RAKİP SEÇİLDİĞİ AN OTOMATİK MODÜLER DAĞITIM
    if op_team and op_team != st.session_state.context['opponent']:
        st.session_state.context['opponent'] = op_team
        with st.spinner(f"Oracle {op_team} verilerini senkronize ediyor..."):
            st.session_state.context['reports']['strategy'] = oracle_engine("STRAT", f_team, op_team)
            st.session_state.context['reports']['data_hub'] = oracle_engine("DATA", f_team, op_team)
            st.session_state.context['reports']['scenarios'] = oracle_engine("KRİZ", f_team, op_team)
            st.session_state.context['reports']['meta'] = oracle_engine("META", f_team, op_team)
        st.rerun()

    st.markdown("---")
    phase = st.radio("Saha Fazı", ["HÜCUM", "SAVUNMA", "GEÇİŞ"])
    
    st.markdown("---")
    st.subheader("🕵️ OYUNCU ANALİZİ")
    target_p = st.text_input("Hedef Oyuncu", placeholder="Örn: Asensio")
    if st.button("⏱️ Kırılma Noktasını Bul"):
        with st.spinner("Analiz ediliyor..."):
            st.session_state.context['reports']['timeline'] = oracle_engine("TIMELINE", f_team, target_p)

# --- 7. ANA EKRAN (MODÜLER PANELLER) ---
c1, c2 = st.columns([5, 5])

with c1:
    st.subheader("📋 MASTERMIND ANALİZ")
    t1, t2, t3, t4, t5 = st.tabs(["🧬 STRATEJİ", "📊 VERİ MERKEZİ", "⚡ KRİZLER", "🧠 META", "🚀 İDMAN"])
    
    with t1:
        st.markdown("### 🎯 Savaş Planı")
        st.write(st.session_state.context['reports']['strategy'])
    
    with t2:
        st.markdown("### 📈 Sayısal Veriler (GÜNCEL)")
        st.markdown(st.session_state.context['reports']['data_hub'])
        
    with t3:
        st.markdown("### 🚨 Kritik Varyasyonlar")
        # Arka plan rengi olmadan sadece KIRMIZI metin
        st.markdown(f'<p style="color:#ff4b4b; font-size:16px;">{st.session_state.context["reports"]["scenarios"]}</p>', unsafe_allow_html=True)
        
    with t4:
        st.markdown("### 🧠 Çevresel Analiz")
        # Arka plan rengi olmadan sadece YEŞİL metin
        st.markdown(f'<p style="color:#00ff9d; font-size:16px;">{st.session_state.context["reports"]["meta"]}</p>', unsafe_allow_html=True)
        
    with t5:
        if st.session_state.context['reports']['timeline']:
            st.success("🕵️ Oyuncu Zaman Çizelgesi Aktif")
            st.write(st.session_state.context['reports']['timeline'])
        else:
            st.success("Taktiksel antrenman programları hazırlandı.")

with c2:
    render_pitch(phase)

# --- 8. CHAT ---
st.markdown("---")
st.subheader("💬 ORACLE İLE SENTEZ")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Oracle'a spesifik bir detay danış..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Oracle araştırıyor..."):
            ans = oracle_engine("CHAT", f_team, f"BAĞLAM: {f_team} vs {st.session_state.context['opponent']}. SORU: {prompt}")
            st.markdown(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})
