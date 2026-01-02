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
        "focus_team": "BEKLEMEDE",
        "formation": "4-3-3",
        "scouting_report": "Analitik komut bekleniyor...",
    }

# --- 2. 🧠 ANALİST MOTORU ---
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
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction="Futbol stratejistisin. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver.")
    response = client.models.generate_content(model="gemini-2.0-flash", contents=[query], config=config)
    return response.text

# --- 3. 🏟️ PRO-TACTICAL UI MOTORU (GÖRSELE UYGUN) ---
def render_cyber_pitch(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    team = context['focus_team']
    form = context['formation']
    
    # Görseldeki gibi piyon yerleşimi ve neon halkalar
    pos_map = {
        "4-3-3": [(92, 50, "GK"), (78, 15, "LB"), (80, 38, "CB"), (80, 62, "CB"), (78, 85, "RB"), (58, 30, "CM"), (62, 50, "DM"), (58, 70, "CM"), (30, 20, "LW"), (25, 50, "ST"), (30, 80, "RW")],
        "4-2-3-1": [(92, 50, "GK"), (78, 15, "LB"), (80, 35, "CB"), (80, 65, "CB"), (78, 85, "RB"), (65, 40, "DM"), (65, 60, "DM"), (45, 20, "LM"), (42, 50, "AM"), (45, 80, "RM"), (22, 50, "ST")]
    }
    
    active_pos = pos_map.get(form, pos_map["4-3-3"])
    players_html = "".join([f"""
        <div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:10;'>
            <div style='width:26px; height:26px; border-radius:50%; background:#0B0E14; border:2px solid #00E5FF; box-shadow:0 0 12px #00E5FF; display:flex; align-items:center; justify-content:center;'>
                <span style='color:#00E5FF; font-size:9px; font-weight:bold;'>{label}</span>
            </div>
            <div style='position:absolute; width:40px; height:40px; border:1px solid rgba(0,229,255,0.1); border-radius:50%; top:-7px; left:-7px; animation: pulse 2s infinite;'></div>
        </div>""" for t, l, label in active_pos])

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
        <style>
            body {{ background:#05070A; color:#E0E6ED; font-family:'Share Tech Mono', monospace; margin:0; padding:10px; }}
            .main-grid {{ display:grid; grid-template-columns: 320px 1fr 280px; gap:15px; height:600px; }}
            .panel {{ background:rgba(13, 17, 23, 0.9); border:1px solid #1B2533; border-radius:4px; padding:15px; position:relative; overflow:hidden; }}
            
            /* GÖRSELDEKİ SAHA TASARIMI */
            .pitch-area {{ 
                background:#0B0E14; border:2px solid #1B2533; position:relative; overflow:hidden;
                background-image: 
                    linear-gradient(rgba(31, 41, 55, 0.2) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(31, 41, 55, 0.2) 1px, transparent 1px);
                background-size: 40px 40px; /* Görseldeki kareli zemin */
            }}
            .pitch-lines {{ position:absolute; inset:20px; border:1px solid rgba(255,255,255,0.1); }}
            .center-circle {{ position:absolute; top:50%; left:50%; width:100px; height:100px; border:1px solid rgba(0,229,255,0.3); border-radius:50%; transform:translate(-50%,-50%); }}
            .center-line {{ position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.1); }}
            
            /* HUD Elementleri */
            .status-tag {{ position:absolute; top:10px; right:10px; background:rgba(0,229,255,0.1); color:#00E5FF; padding:2px 8px; font-size:10px; border:1px solid #00E5FF; }}
            @keyframes pulse {{ 0% {{ transform:scale(0.8); opacity:0.5; }} 100% {{ transform:scale(1.2); opacity:0; }} }}
            
            .report-text {{ font-size:11px; line-height:1.6; color:#94A3B8; height:100%; overflow-y:auto; }}
        </style>
    </head>
    <body>
        <div class="main-grid">
            <div class="panel">
                <div style="color:#00E5FF; font-size:12px; margin-bottom:15px; border-bottom:1px solid #1B2533;">TACTICAL COMMAND</div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <div style="border:1px solid #00E5FF; padding:8px; font-size:10px; color:#00E5FF;">🔍 RAKİP GÖZLEMİ</div>
                    <div style="border:1px solid #1B2533; padding:8px; font-size:10px;">🛡️ SAVUNMA REÇETESİ</div>
                    <div style="border:1px solid #1B2533; padding:8px; font-size:10px;">📈 TRANSFER UYUMU</div>
                </div>
                <div style="margin-top:20px; color:#94A3B8; font-size:11px;">
                    <div style="color:#00E5FF; margin-bottom:5px;">ORACLE REPORT</div>
                    <div class="report-text">{report}</div>
                </div>
            </div>

            <div class="pitch-area">
                <div class="status-tag">TACTICAL COMMAND ACTIVE</div>
                <div class="pitch-lines">
                    <div class="center-line"></div>
                    <div class="center-circle"></div>
                    <div style="position:absolute; top:0; left:50%; width:200px; height:80px; border:1px solid rgba(255,255,255,0.1); border-top:0; transform:translateX(-50%);"></div>
                    <div style="position:absolute; bottom:0; left:50%; width:200px; height:80px; border:1px solid rgba(255,255,255,0.1); border-bottom:0; transform:translateX(-50%);"></div>
                </div>
                {players_html}
            </div>

            <div class="panel">
                <div style="font-size:10px; color:#94A3B8; margin-bottom:20px;">
                    <div>ACTIVE TEAM:</div>
                    <div style="color:#FFF; font-size:14px; margin-bottom:15px;">{team}</div>
                    <div>FORMATION:</div>
                    <div style="color:#00E5FF; font-size:14px; margin-bottom:15px;">{form}</div>
                    <div>DATA STATUS:</div>
                    <div style="color:#22C55E; font-size:14px;">REAL-TIME</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_template, height=620)

# --- 4. ANA ARAYÜZ ---
render_cyber_pitch(st.session_state.tactic_context)

st.markdown("---")
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages[-2:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Taktiksel komut girişi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        ans = get_manager_analysis(prompt)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Otomatik State Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        st.session_state.tactic_context['scouting_report'] = ans
        st.rerun()
