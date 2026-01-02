import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# --- 2. SESSION STATE ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "scouting_report": "Sistem başlatıldı. Stratejik veri girişi bekleniyor...",
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. GİRİŞ KONTROLÜ ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#00E5FF; font-family:monospace;'>DATALIG COCKPIT</h1>", unsafe_allow_html=True)
    pw = st.text_input("Sistem Şifresi", type="password", key="login_pass")
    if st.button("ERİŞİM SAĞLA"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 4. SİSTEM BAŞLATMA ---
@st.cache_resource
def init_system():
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        idx = pc.Index("regista-arsiv")
        embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return client, idx, embeds
    except:
        return None, None, None

client, pinecone_index, embeddings = init_system()

# --- 5. ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[search_tool], 
        system_instruction="Sen bir futbol stratejistisin. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver."
    )
    response = client.models.generate_content(model="gemini-2.0-flash", contents=[query], config=config)
    return response.text

# --- 6. 🚀 CYBER-UI ENGINE (HATASIZ VERSİYON) ---
def render_cyber_ui(context):
    report = context['scouting_report'].replace("\n", " ").replace('"', "'")
    team = context['focus_team']
    form = context['formation']
    
    # Koordinatlar (Dikey Saha: Üst Hücum, Alt Savunma)
    pos_map = {
        "4-3-3": [
            (92, 50, "shield"), # GK
            (78, 15, "person"), (80, 38, "person"), (80, 62, "person"), (78, 85, "person"), # DEF
            (55, 30, "person"), (60, 50, "person"), (55, 70, "person"), # MID
            (25, 20, "person"), (20, 50, "person"), (25, 80, "person")  # FWD
        ],
        "4-2-3-1": [
            (92, 50, "shield"),
            (78, 15, "person"), (80, 35, "person"), (80, 65, "person"), (78, 85, "person"),
            (65, 40, "person"), (65, 60, "person"),
            (45, 20, "person"), (40, 50, "person"), (45, 80, "person"),
            (22, 50, "person")
        ]
    }
    
    active_pos = pos_map.get(form, pos_map["4-3-3"])
    players_html = ""
    for t, l, icon in active_pos:
        players_html += f"""
        <div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:5;'>
            <div style='width:24px; height:24px; border-radius:50%; border:1px solid #00E5FF; background:#0B0E14; display:flex; align-items:center; justify-content:center; box-shadow:0 0 8px #00E5FF;'>
                <span class='material-icons-outlined' style='color:#00E5FF; font-size:14px;'>{icon}</span>
            </div>
        </div>"""

    # HTML - F-string çakışmasını önlemek için stilleri basit tuttum
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
        <style>
            body {{ background:#0B0E14; color:#cbd5e1; font-family:sans-serif; margin:0; padding:10px; }}
            .header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }}
            .panel {{ background:rgba(19,27,38,0.9); border:1px solid rgba(0,229,255,0.2); border-radius:8px; padding:15px; }}
            .pitch {{ position:relative; background:#0B0E14; border:1px solid #1e293b; border-radius:8px; height:500px; overflow:hidden; }}
            .goal-top {{ position:absolute; top:0; left:50%; width:60px; height:4px; background:rgba(0,229,255,0.5); transform:translateX(-50%); }}
            .goal-bottom {{ position:absolute; bottom:0; left:50%; width:60px; height:4px; background:rgba(239,68,68,0.5); transform:translateX(-50%); }}
            .line-center {{ position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.05); }}
        </style>
    </head>
    <body>
        <div class="header">
            <div style="color:white; font-weight:bold; letter-spacing:2px;">DATALIG OS <span style="color:#00E5FF">V7.0</span></div>
            <div style="display:flex; gap:10px;">
                <div class="panel" style="padding:4px 12px; border-bottom:2px solid #ef4444; font-size:11px;">{team}</div>
                <div class="panel" style="padding:4px 12px; border-bottom:2px solid #00E5FF; font-size:11px; color:#00E5FF;">{form}</div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(12, 1fr); gap:15px;">
            <div class="panel" style="grid-column: span 4; height:500px; display:flex; flex-direction:column;">
                <div style="font-size:10px; color:#00E5FF; margin-bottom:10px;">INTELLIGENCE_REPORT</div>
                <div style="flex:1; overflow-y:auto; font-size:11px; line-height:1.6; color:#94a3b8;">{report}</div>
            </div>
            <div class="pitch" style="grid-column: span 8;">
                <div class="goal-top"></div>
                <div class="line-center"></div>
                <div class="goal-bottom"></div>
                {players_html}
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_template, height=600)

# --- 7. ANA EKRAN ---
render_cyber_ui(st.session_state.tactic_context)

st.markdown("---")
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages[-2:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Taktik komutunuzu girin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        ans = get_manager_analysis(prompt, "")
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Otomatik Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        st.session_state.tactic_context['scouting_report'] = ans
        st.rerun()
