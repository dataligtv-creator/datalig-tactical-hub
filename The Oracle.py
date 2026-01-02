import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "scouting_report": "Analiz için veri bekleniyor...",
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 2. GİRİŞ KONTROLÜ ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#22c55e;'>DATALIG ANALYST LOGIN</h1>", unsafe_allow_html=True)
    pw = st.text_input("Sistem Şifresi", type="password", key="login_pass")
    if st.button("SİSTEME GİRİŞ"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 3. SİSTEM BAŞLATMA ---
@st.cache_resource
def init_system():
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        idx = pc.Index("regista-arsiv")
        embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return client, idx, embeds
    except: return None, None, None

client, pinecone_index, embeddings = init_system()

def get_manager_analysis(query):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction="Sen bir futbol stratejistisin. Yanıtın sonunda [TEAM: ..., FORMATION: ...] ekle.")
    response = client.models.generate_content(model="gemini-2.0-flash", contents=[query], config=config)
    return response.text

# --- 4. 🏟️ KLASİK YEŞİL SAHA MOTORU (V7.5) ---
def render_analyst_ui(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    team = context['focus_team']
    form = context['formation']
    
    # Dikey Diziliş Koordinatları (Yeşil Saha Üzerine)
    pos_map = {
        "4-3-3": [
            (93, 50, "GK"), (78, 15, "LB"), (82, 38, "CB"), (82, 62, "CB"), (78, 85, "RB"),
            (60, 30, "CM"), (65, 50, "DM"), (60, 70, "CM"),
            (35, 20, "LW"), (28, 50, "ST"), (35, 80, "RW")
        ],
        "4-2-3-1": [
            (93, 50, "GK"), (78, 15, "LB"), (82, 35, "CB"), (82, 65, "CB"), (78, 85, "RB"),
            (68, 40, "DM"), (68, 60, "DM"), (45, 25, "LM"), (42, 50, "AM"), (45, 75, "RM"), (25, 50, "ST")
        ]
    }
    
    active_pos = pos_map.get(form, pos_map["4-3-3"])
    players_html = ""
    for t, l, label in active_pos:
        players_html += f"""
        <div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:10; text-align:center;'>
            <div style='width:22px; height:22px; border-radius:50%; background:#fff; border:2px solid #1e3a8a; box-shadow:0 2px 4px rgba(0,0,0,0.3);'></div>
            <div style='font-size:9px; color:white; font-weight:bold; background:rgba(0,0,0,0.6); padding:1px 3px; border-radius:3px; margin-top:2px;'>{label}</div>
        </div>"""

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background:#111827; color:#e5e7eb; font-family:sans-serif; margin:0; padding:15px; }}
            .analyst-container {{ display:grid; grid-template-columns: 350px 1fr; gap:20px; height:600px; }}
            .report-panel {{ background:#1f2937; border:1px solid #374151; border-radius:12px; padding:20px; overflow-y:auto; }}
            
            /* Yeşil Saha Tasarımı */
            .pitch {{ 
                position:relative; background:#2d5a27; border:3px solid #fff; border-radius:4px; 
                height:100%; width:420px; margin:0 auto;
                background-image: repeating-linear-gradient(0deg, #2d5a27, #2d5a27 10%, #356330 10%, #356330 20%);
            }}
            .pitch-line {{ position:absolute; border:1px solid rgba(255,255,255,0.8); }}
            .center-circle {{ position:absolute; top:50%; left:50%; width:80px; height:80px; border:1px solid white; border-radius:50%; transform:translate(-50%,-50%); }}
            .center-line {{ position:absolute; top:50%; left:0; right:0; height:1px; background:white; }}
            
            /* Kaleler (Kısa Kenarlar) */
            .penalty-area-top {{ position:absolute; top:0; left:50%; width:180px; height:70px; border:1px solid white; border-top:0; transform:translateX(-50%); }}
            .penalty-area-bottom {{ position:absolute; bottom:0; left:50%; width:180px; height:70px; border:1px solid white; border-bottom:0; transform:translateX(-50%); }}
            .goal-box {{ position:absolute; width:40px; height:4px; background:#fff; left:50%; transform:translateX(-50%); }}
        </style>
    </head>
    <body>
        <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
            <b style="color:#22c55e;">DATALIG ANALYST CENTER</b>
            <div style="display:flex; gap:10px;">
                <span style="background:#374151; padding:2px 10px; border-radius:4px; font-size:12px;">TAKIM: {team}</span>
                <span style="background:#1e40af; padding:2px 10px; border-radius:4px; font-size:12px;">DİZİLİŞ: {form}</span>
            </div>
        </div>
        <div class="analyst-container">
            <div class="report-panel">
                <div style="font-size:12px; color:#10b981; margin-bottom:10px; font-weight:bold;">TACTICAL INTELLIGENCE</div>
                <div style="font-size:13px; line-height:1.6;">{report}</div>
            </div>
            <div style="background:#1f2937; border-radius:12px; display:flex; align-items:center; border:1px solid #374151;">
                <div class="pitch">
                    <div class="goal-box" style="top:-2px;"></div>
                    <div class="penalty-area-top"></div>
                    <div class="center-line"></div>
                    <div class="center-circle"></div>
                    <div class="penalty-area-bottom"></div>
                    <div class="goal-box" style="bottom:-2px;"></div>
                    {players_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_template, height=650)

# --- 5. ANA EKRAN ---
render_analyst_ui(st.session_state.tactic_context)

st.markdown("---")
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages[-2:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Analiz komutu girin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        ans = get_manager_analysis(prompt)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Bağlam Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        st.session_state.tactic_context['scouting_report'] = ans
        st.rerun()
