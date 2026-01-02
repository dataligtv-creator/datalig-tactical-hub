import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# --- 2. BEYİN (SESSION STATE) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "scouting_report": "Sistem aktif. Taktiksel veri bekleniyor...",
        "last_update": time.time()
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

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
    config = types.GenerateContentConfig(tools=[search_tool], system_instruction="Sen DATALIG Baş Stratejistisin. Teknik direktöre net, veri odaklı taktikler ver. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver.")
    response = client.models.generate_content(model="gemini-2.0-flash", contents=[query], config=config)
    return response.text

# --- 4. 🚀 STITCH ENTEGRE UI MOTORU ---
def render_analyst_dashboard(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    team = context['focus_team']
    form = context['formation']
    
    # Dizilişe Göre Piyon Pozisyonları (Yüzdelik Koordinatlar)
    pos_db = {
        "4-3-3": [
            (93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"),
            (55, 30, "8"), (60, 50, "6"), (55, 70, "10"),
            (30, 20, "7"), (25, 50, "9"), (30, 80, "11")
        ],
        "4-2-3-1": [
            (93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"),
            (65, 40, "6"), (65, 60, "8"), (45, 20, "7"), (42, 50, "10"), (45, 80, "11"), (25, 50, "9")
        ]
    }
    
    active_pos = pos_db.get(form, pos_db["4-3-3"])
    players_html = "".join([f"""
        <div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:20;'>
            <div style='width:24px; height:24px; border-radius:50%; background:white; border:2px solid #13c8ec; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:bold; color:black; box-shadow: 0 0 10px rgba(19,200,236,0.6);'>
                {num}
            </div>
        </div>""" for t, l, num in active_pos])

    # Stitch'ten gelen HTML yapısını Python dostu hale getirdik
    full_html = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
        <style>
            body {{ background: #101f22; color: white; font-family: 'Inter', sans-serif; margin:0; padding:0; overflow:hidden; }}
            .pitch-stripes {{ background-color: #173828; background-image: repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255,255,255,0.03) 50px, rgba(255,255,255,0.03) 100px); }}
            .glass-panel {{ background: rgba(17, 23, 24, 0.9); border: 1px solid #283639; }}
            .pitch-container {{ position:relative; width:400px; height:580px; margin: 0 auto; border:4px solid #283639; border-radius:15px; overflow:hidden; }}
        </style>
    </head>
    <body>
        <div style="display: grid; grid-template-columns: 320px 1fr 320px; height: 100vh;">
            <aside class="glass-panel p-6 flex flex-col gap-4">
                <div style="color:#13c8ec; font-size:12px; font-weight:bold; letter-spacing:2px; margin-bottom:10px;">TACTICAL COMMAND</div>
                <div style="display:flex; flex-direction:column; gap:10px;">
                    <button style="background:#1a2426; border:1px solid #283639; color:white; padding:10px; border-radius:8px; text-align:left; font-size:12px;">🔍 Rakip Gözlemi</button>
                    <button style="background:#1a2426; border:1px solid #283639; color:white; padding:10px; border-radius:8px; text-align:left; font-size:12px;">🛡️ Savunma Reçetesi</button>
                </div>
                <div style="margin-top:20px; flex:1; display:flex; flex-direction:column;">
                    <div style="color:#13c8ec; font-size:10px; font-weight:bold; margin-bottom:5px;">ORACLE INTELLIGENCE</div>
                    <div style="background:#0b1011; border:1px solid #283639; padding:15px; border-radius:8px; font-family:'JetBrains Mono'; font-size:11px; color:#94a3b8; flex:1; overflow-y:auto;">
                        {report}
                    </div>
                </div>
            </aside>

            <section style="display:flex; align-items:center; justify-content:center; background:#0f1516;">
                <div class="pitch-container pitch-stripes">
                    <div style="position:absolute; inset:20px; border:1px solid rgba(255,255,255,0.4);">
                        <div style="position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.4);"></div>
                        <div style="position:absolute; top:50%; left:50%; width:80px; height:80px; border:1px solid rgba(255,255,255,0.4); border-radius:50%; transform:translate(-50%,-50%);"></div>
                        <div style="position:absolute; top:0; left:50%; width:160px; height:60px; border:1px solid rgba(255,255,255,0.4); border-top:0; transform:translateX(-50%);"></div>
                        <div style="position:absolute; bottom:0; left:50%; width:160px; height:60px; border:1px solid rgba(255,255,255,0.4); border-bottom:0; transform:translateX(-50%);"></div>
                    </div>
                    {players_html}
                </div>
            </section>

            <aside class="glass-panel p-6">
                <div style="color:#13c8ec; font-size:12px; font-weight:bold; margin-bottom:20px;">MATCH METRICS</div>
                <div style="margin-bottom:20px;">
                    <div style="font-size:10px; color:#94a3b8;">ACTIVE TEAM</div>
                    <div style="font-size:18px; font-weight:bold; color:white;">{team}</div>
                </div>
                <div style="margin-bottom:20px;">
                    <div style="font-size:10px; color:#94a3b8;">FORMATION</div>
                    <div style="font-size:18px; font-weight:bold; color:#13c8ec;">{form}</div>
                </div>
                <div style="background:#1a2426; border:1px solid #283639; padding:15px; border-radius:8px;">
                    <div style="font-size:10px; color:#94a3b8; margin-bottom:10px;">POSSESSION</div>
                    <div style="height:8px; background:#283639; border-radius:4px; overflow:hidden;">
                        <div style="width:56%; height:100%; background:#13c8ec;"></div>
                    </div>
                </div>
            </aside>
        </div>
    </body>
    </html>
    """
    return components.html(full_html, height=700)

# --- 5. ANA EKRAN ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#13c8ec;'>DATALIG ANALYST</h1>", unsafe_allow_html=True)
    pw = st.text_input("Şifre", type="password")
    if st.button("Sisteme Gir"):
        if pw == "datalig2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# Dashboard'u Render Et
render_analyst_dashboard(st.session_state.tactic_context)

# Sohbet Alanı
st.markdown("---")
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages[-2:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Analiz komutu beklemede..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        ans = get_manager_analysis(prompt)
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Akıllı Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        st.session_state.tactic_context['scouting_report'] = ans
        st.rerun()
