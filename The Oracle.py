import streamlit as st
import streamlit.components.v1 as components

# --- 0. BAĞLANTI ---
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Kütüphane hatası: pip install google-genai streamlit")
    st.stop()

st.set_page_config(page_title="THE ORACLE OS", page_icon="👁️", layout="wide")

# --- 1. VERİ HAVUZU ---
TURKISH_TEAMS = ["Fenerbahçe", "Galatasaray", "Beşiktaş", "Trabzonspor", "Başakşehir"]
ALL_TEAMS = sorted(list(set(TURKISH_TEAMS + ["Real Madrid", "Man City", "Liverpool", "Arsenal", "Bayern Munich"])))

# --- 2. SİSTEM HAFIZASI ---
if 'context' not in st.session_state:
    st.session_state.context = {
        "focus_team": "Fenerbahçe",
        "opponent": None,
        "reports": {
            "strategy": "Oracle hedef bekliyor...",
            "data_hub": "Sayısal veriler taranıyor...",
            "scenarios": "Kriz varyasyonları hesaplanıyor...",
            "meta": "Psikolojik analiz bekleniyor...",
            "timeline": ""
        }
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. API CLIENT ---
@st.cache_resource
def init_client():
    if "GOOGLE_API_KEY" not in st.secrets: return None
    return genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

client = init_client()
MODEL_ID = "gemini-2.5-flash"

# --- 4. ORACLE MODÜLER MOTORU (VERİ ODAKLI GÜNCELLEME) ---
def oracle_engine(mode, f_team, op_team):
    if not client: return "Bağlantı yok."
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # VERİ MERKEZİ İÇİN AGRESİF TALİMAT
    instructions = {
        "STRAT": f"Görevin: {f_team} ve {op_team} oyun kimliklerini özetle. {f_team} için galibiyet formülünü 3 kısa maddede ver.",
        "DATA": f"""Görevin: {f_team} ve {op_team} için İNTERNETİ TARA ve şu verileri MUTLAKA getir: 
                   1. Son derbi sonucu ve istatistikleri (Şut, xG, Korner). 
                   2. İki takımın ligdeki güncel xG ortalamaları. 
                   3. GÜNCEL Sakat ve Cezalı listesi. 
                   4. En formda 3 oyuncu ve reytingleri. 
                   'Veri yok' deme, web araması yaparak en güncel rakamları tablo veya liste yap.""",
        "KRİZ": f"Görevin: {op_team} maçında {f_team} için yaşanabilecek 3 spesifik taktiksel tehlikeyi (Örn: Geçiş savunması zafiyeti) ve çözümünü yaz.",
        "META": f"Görevin: Derbi atmosferi, taraftar etkisi ve maç saati hava durumunun oyuna etkisini analiz et.",
        "CHAT": "Sen THE ORACLE'sın. Sorulara kısa, net ve stratejik cevaplar ver."
    }

    base = "Sen THE ORACLE'sın. Bilgi eksikliği kabul edilemez. Web kaynaklarını kullanarak en güncel rakamları sentezle. Halüsinasyon görme."
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=f"{base}\n{instructions.get(mode, '')}")
    
    try:
        query = f"Canlı futbol verilerini kullanarak {f_team} vs {op_team} analizi yap."
        response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
        return response.text
    except Exception as e: return f"Veri Senkronizasyon Hatası: {str(e)}"

# --- 5. SIDEBAR VE OTOMASYON ---
with st.sidebar:
    st.title("👁️ THE ORACLE")
    f_team = st.selectbox("Yönetilen Birim", TURKISH_TEAMS, index=TURKISH_TEAMS.index("Fenerbahçe"))
    st.session_state.context['focus_team'] = f_team

    op_team = st.selectbox("Hedef Rakip", [None] + ALL_TEAMS, index=0)

    if op_team and op_team != st.session_state.context['opponent']:
        st.session_state.context['opponent'] = op_team
        with st.spinner(f"Oracle küresel veri ağlarına sızıyor: {f_team} vs {op_team}..."):
            # Paralel rapor üretimi (Ayrı ayrı çağrı yapılarak sekmeler doldurulur)
            st.session_state.context['reports']['strategy'] = oracle_engine("STRAT", f_team, op_team)
            st.session_state.context['reports']['data_hub'] = oracle_engine("DATA", f_team, op_team)
            st.session_state.context['reports']['scenarios'] = oracle_engine("KRİZ", f_team, op_team)
            st.session_state.context['reports']['meta'] = oracle_engine("META", f_team, op_team)
        st.rerun()

# --- 6. ANA EKRAN ---
col1, col2 = st.columns([5, 5])

with col1:
    st.subheader("📋 MODÜLER ANALİZ PANELİ")
    t1, t2, t3, t4 = st.tabs(["🧬 STRATEJİ", "📊 VERİ MERKEZİ", "⚡ KRİZLER", "🧠 META"])
    
    with t1:
        st.write(st.session_state.context['reports']['strategy'])
    
    with t2:
        st.markdown("### 📈 Canlı Veri Akışı")
        st.markdown(st.session_state.context['reports']['data_hub'])
        
    with t3:
        st.error(st.session_state.context['reports']['scenarios'])
        
    with t4:
        st.warning(st.session_state.context['reports']['meta'])

with col2:
    # Dinamik Saha (Basit SVG)
    components.html(f"""<div style='background:#050505; border:1px solid #333; height:450px; border-radius:15px; display:flex; align-items:center; justify-content:center; color:#00ff9d; font-family:monospace;'>[ SAHA SİMÜLASYONU: {f_team} vs {op_team if op_team else '...'} ]</div>""", height=470)

# --- 7. CHAT ---
st.markdown("---")
if prompt := st.chat_input("Bir detay sor..."):
    with st.chat_message("assistant"):
        ans = oracle_engine("CHAT", f_team, f"Bağlam: {f_team} vs {op_team}. Soru: {prompt}")
        st.write(ans)
