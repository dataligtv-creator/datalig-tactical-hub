import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Mastermind OS", page_icon="🧬", layout="wide")

# --- 2. DİNAMİK TAKIM LİSTESİ (Örnek Havuz - Genişletilebilir) ---
# Gerçek uygulamada burası bir API'den veya JSON'dan beslenebilir.
ALL_TEAMS = [
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", 
    "Real Madrid", "Manchester City", "Arsenal", "Liverpool", 
    "Bayern Munich", "PSG", "Inter Milan", "Barcelona", "Napoli",
    "Aston Villa", "Bayer Leverkusen", "Girona", "Benfica"
]

# --- 3. SESSION STATE GÜNCELLEME ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Seçilmedi",
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "opponent_dna": "Lütfen önce analiz edilecek takımı seçin.",
        "scouting_report": "Stratejik merkez hazır. Odak takım bekleniyor.",
    }

# --- 4. GEMINI 2.5 FLASH ANALİZ MOTORU ---
def get_mastermind_analysis(query, mode="TACTIC"):
    MODEL_ID = "gemini-2.5-flash"
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    if mode == "OPPONENT_DNA":
        instruction = "Sen Domenico Tedesco ve Luis Enrique'sin. Rakibin en güncel maç verilerini internetten (WhoScored, Opta, Transfermarkt) bul ve zayıf halkalarını deşifre et."
    else:
        instruction = "Sen Pep Guardiola, Jose Mourinho ve Jurgen Klopp'un hibrit zekasısın."

    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=f"Tarih: 2 Ocak 2026. {instruction}"
    )
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
        return response.text
    except Exception as e:
        return f"Analiz Hatası: {str(e)}"

# --- 5. SIDEBAR: MASTERMIND KOMUTA MERKEZİ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/802/802276.png", width=60) # Taktik İkonu
    st.title("MASTERMIND OS")
    st.markdown("---")
    
    # --- TAKIM SEÇİCİ (AUTO-COMPLETE) ---
    st.subheader("📍 ODAK TAKIM")
    selected_team = st.selectbox(
        "Analiz edilecek takımı yazın veya seçin:",
        options=ALL_TEAMS,
        index=None,
        placeholder="Takım adı giriniz (Örn: Galatasaray)...",
    )
    
    if selected_team:
        st.session_state.tactic_context['focus_team'] = selected_team
        st.success(f"Odak: {selected_team}")

    st.markdown("---")
    
    # --- DEŞİFRE BUTONU ---
    if st.button("🔬 RAKİBİ DEŞİFRE ET", use_container_width=True, disabled=(selected_team is None)):
        with st.spinner(f"{selected_team} deşifre ediliyor..."):
            dna = get_mastermind_analysis(f"{selected_team} takımının taktiksel zayıflıkları ve rakip olarak karşılaşıldığında dikkat edilmesi gereken DNA verileri.", mode="OPPONENT_DNA")
            st.session_state.tactic_context['opponent_dna'] = dna
            st.rerun()

    st.markdown("---")
    st.subheader("⚙️ OYUN PARAMETRELERİ")
    phase = st.radio("OYUN EVRESİ", ["SET HÜCUMU", "SAVUNMA", "GEÇİŞ"])
    st.session_state.tactic_context['game_phase'] = phase

# --- 6. UI RENDER (Mastermind Arayüzü) ---
def render_ui(context):
    report = context['scouting_report'].replace("\n", "<br>")
    dna = context['opponent_dna'].replace("\n", "<br>")
    team = context['focus_team']
    
    # Stitch tasarımına sadık kalarak HTML render
    html_content = f"""
    <div style="background:#0b1011; color:white; padding:20px; font-family:sans-serif;">
        <div style="display:grid; grid-template-columns: 1fr 2fr; gap:20px;">
            <div style="background:#111718; border:1px solid #283639; padding:15px; border-radius:10px;">
                <h3 style="color:#facc15; font-size:12px; border-bottom:1px solid #283639; padding-bottom:5px;">🧬 {team.upper()} DNA DEŞİFRESİ</h3>
                <div style="font-size:11px; color:#94a3b8; margin-top:10px; line-height:1.6;">{dna}</div>
            </div>
            <div style="background:#0f1516; border:2px solid #283639; height:500px; border-radius:15px; position:relative; overflow:hidden;">
                <div style="text-align:center; margin-top:200px; color:#13c8ec; opacity:0.3; font-weight:bold;">TACTICAL FIELD ACTIVE</div>
            </div>
        </div>
    </div>
    """
    return components.html(html_content, height=600)

render_ui(st.session_state.tactic_context)
