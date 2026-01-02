import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import time

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="🧠", layout="wide")

# --- 2. SESSION STATE (BELLEK) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Seçilmedi",
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "scouting_report": "Sistem aktif. Mastermind hazır.",
        "opponent_dna": "Analiz için takım seçin.",
        "messages": [] # Sohbet geçmişi
    }

# --- 3. ANALİZ MOTORU (GEMINI 2.5 FLASH) ---
def get_mastermind_analysis(query, mode="TACTIC"):
    MODEL_ID = "gemini-2.5-flash"
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # Mastermind Kişiliği
    sys_instruction = (
        "Sen Pep Guardiola, Mourinho, Klopp, Ferguson ve Ancelotti'nin hibrit zekasısın. "
        "2026 Ocak verilerini kullanarak internetten tarama yap. "
        "Analizlerinde taktik tahtası dizilişini mutlaka [FORMATION: X-X-X] formatında belirt."
    )
    
    if mode == "DNA":
        sys_instruction += " Şu an Domenico Tedesco ve Luis Enrique gibi rakibi sayısal deşifre ediyorsun."

    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=sys_instruction)
    response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
    return response.text

# --- 4. 🏟️ STITCH UI & TAKTİK TAHTASI MOTORU ---
def render_dashboard(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    dna = context['opponent_dna'].replace("\n", "<br>").replace('"', "'")
    form = context['formation']
    team = context['focus_team']

    # Diziliş Piyonları (Dikey Saha)
    pos_db = {
        "4-3-3": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (55, 30, "8"), (60, 50, "6"), (55, 70, "10"), (30, 20, "7"), (25, 50, "9"), (30, 80, "11")],
        "4-2-3-1": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (65, 40, "6"), (65, 60, "8"), (45, 20, "7"), (42, 50, "10"), (45, 80, "11"), (25, 50, "9")]
    }
    players_html = "".join([f"<div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:20;'><div style='width:22px; height:22px; border-radius:50%; background:white; border:2px solid #13c8ec; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:bold; color:black; shadow:0 0 10px #13c8ec;'>{num}</div></div>" for t, l, num in pos_db.get(form, pos_db["4-3-3"])])

    html_code = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: #0b1011; color: white; font-family: sans-serif; margin:0; overflow:hidden; }}
            .pitch-stripes {{ background-color: #173828; background-image: repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255, 255, 255, 0.03) 50px, rgba(255, 255, 255, 0.03) 100px); }}
            .panel {{ background: #111718; border: 1px solid #283639; border-radius: 8px; padding: 12px; }}
            .scroll-box {{ height: 250px; overflow-y: auto; font-size: 11px; color: #94a3b8; line-height: 1.5; }}
        </style>
    </head>
    <body class="p-4">
        <div class="grid grid-cols-12 gap-4">
            <div class="col-span-3 flex flex-col gap-4">
                <div class="panel border-l-4 border-yellow-500">
                    <h3 class="text-yellow-500 text-[10px] font-bold uppercase tracking-widest mb-2">🧬 OPPONENT DNA (DEŞİFRE)</h3>
                    <div class="scroll-box">{dna}</div>
                </div>
                <div class="panel border-l-4 border-cyan-500">
                    <h3 class="text-cyan-500 text-[10px] font-bold uppercase tracking-widest mb-2">🧠 STRATEJİK ANALİZ</h3>
                    <div class="scroll-box">{report}</div>
                </div>
            </div>

            <div class="col-span-6 flex items-center justify-center bg-[#0f1516] rounded-xl border border-[#283639]">
                <div class="relative w-[380px] h-[550px] pitch-stripes rounded-lg border-2 border-white/20 overflow-hidden">
                    <div style="position:absolute; inset:15px; border:1px solid rgba(255,255,255,0.3);">
                        <div style="position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.3);"></div>
                        <div style="position:absolute; top:0; left:50%; width:150px; height:55px; border:1px solid rgba(255,255,255,0.3); border-top:0; transform:translateX(-50%);"></div>
                        <div style="position:absolute; bottom:0; left:50%; width:150px; height:55px; border:1px solid rgba(255,255,255,0.3); border-bottom:0; transform:translateX(-50%);"></div>
                    </div>
                    {players_html}
                </div>
            </div>

            <div class="col-span-3">
                <div class="panel h-full">
                    <h3 class="text-xs font-bold text-gray-400 mb-4 tracking-widest uppercase">Match Metrics</h3>
                    <div class="mb-6"><span class="text-[10px] text-gray-500 uppercase block">Odak Takım</span><span class="text-lg font-bold text-white">{team}</span></div>
                    <div class="mb-6"><span class="text-[10px] text-gray-500 uppercase block">Formasyon</span><span class="text-lg font-bold text-cyan-400">{form}</span></div>
                    <div class="h-1 bg-cyan-500/20 rounded w-full mt-4"><div class="h-full bg-cyan-500 w-3/4"></div></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_code, height=600)

# --- 5. SIDEBAR: KOMUTA MERKEZİ ---
ALL_TEAMS = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Real Madrid", "Man City", "Arsenal", "Barcelona", "Liverpool"]

with st.sidebar:
    st.title("🧠 MASTERMIND OS")
    selected_team = st.selectbox("🎯 TAKIM ODAĞI", options=ALL_TEAMS, index=None, placeholder="Takım Seçiniz...")
    
    if selected_team:
        st.session_state.tactic_context['focus_team'] = selected_team
        if st.button("🔬 RAKİBİ DEŞİFRE ET", use_container_width=True):
            dna = get_mastermind_analysis(f"{selected_team} takımını Tedesco ve Enrique gözüyle deşifre et.", mode="DNA")
            st.session_state.tactic_context['opponent_dna'] = dna
            st.rerun()
    
    st.markdown("---")
    phase = st.radio("OYUN EVRESİ", ["SET HÜCUMU", "SAVUNMA", "GEÇİŞ"])
    st.session_state.tactic_context['game_phase'] = phase

# --- 6. ANA EKRAN RENDER ---
render_dashboard(st.session_state.tactic_context)

# --- 7. ORACLE CHAT (CHAT EKRANI GERİ GELDİ) ---
st.markdown("---")
st.subheader("💬 Oracle Taktik Sohbeti")

for msg in st.session_state.tactic_context['messages'][-3:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Mastermind'a direktif ver..."):
    st.session_state.tactic_context['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.status("🧠 Analiz yapılıyor...", expanded=False):
            ans = get_mastermind_analysis(prompt)
        st.markdown(ans)
        st.session_state.tactic_context['scouting_report'] = ans
        st.session_state.tactic_context['messages'].append({"role": "assistant", "content": ans})
        
        # Dinamik Diziliş Güncelleme
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        elif "4-3-3" in ans: st.session_state.tactic_context['formation'] = "4-3-3"
        
        st.rerun()
