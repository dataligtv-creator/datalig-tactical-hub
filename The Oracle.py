import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# --- 2. SESSION STATE (BELLEK) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "BEKLEMEDE",
        "formation": "4-3-3",
        "scouting_report": "Sistem aktif. Komut bekleniyor...",
        "last_update": time.time()
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. GİRİŞ KONTROLÜ ---
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#00E5FF; font-family:monospace;'>DATALIG COCKPIT</h1>", unsafe_allow_html=True)
    pw = st.text_input("Sistem Şifresi", type="password", key="login_key")
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
    except Exception as e:
        st.error(f"Başlatma Hatası: {e}")
        return None, None, None

client, pinecone_index, embeddings = init_system()

# --- 5. ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "30 Aralık 2025" 
    config = types.GenerateContentConfig(
        tools=[search_tool], temperature=1.0,
        system_instruction=f"Tarih: {current_date}. Sen DATALIG Football OS Baş Stratejistisin. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] bilgisini ver."
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=[f"{current_date} verisiyle: {query}"], config=config)
    return response.text

# --- 6. 🚀 STITCH UI: CYBER-PITCH ENGINE (V6.2) ---
def render_cyber_ui(context):
    clean_report = context['scouting_report'].replace("\n", "<br>").replace("**", "")
    formation = context['formation']
    
    # Dikey Saha Piyon Pozisyonları
    pos_db = {
        "4-3-3": [
            {"t": "92%", "l": "50%", "i": "shield"},
            {"t": "80%", "l": "20%"}, {"t": "82%", "l": "40%"}, {"t": "82%", "l": "60%"}, {"t": "80%", "l": "80%"},
            {"t": "60%", "l": "30%"}, {"t": "65%", "l": "50%"}, {"t": "60%", "l": "70%"},
            {"t": "35%", "l": "20%"}, {"t": "28%", "l": "50%"}, {"t": "35%", "l": "80%"}
        ],
        "4-2-3-1": [
            {"t": "92%", "l": "50%", "i": "shield"},
            {"t": "80%", "l": "15%"}, {"t": "82%", "l": "38%"}, {"t": "82%", "l": "62%"}, {"t": "80%", "l": "85%"},
            {"t": "68%", "l": "40%"}, {"t": "68%", "l": "60%"},
            {"t": "48%", "l": "20%"}, {"t": "45%", "l": "50%"}, {"t": "48%", "l": "80%"},
            {"t": "25%", "l": "50%"}
        ],
        "3-5-2": [
             {"t": "92%", "l": "50%", "i": "shield"},
             {"t": "82%", "l": "25%"}, {"t": "84%", "l": "50%"}, {"t": "82%", "l": "75%"},
             {"t": "60%", "l": "10%"}, {"t": "58%", "l": "35%"}, {"t": "58%", "l": "50%"}, {"t": "58%", "l": "65%"}, {"t": "60%", "l": "90%"},
             {"t": "30%", "l": "40%"}, {"t": "30%", "l": "60%"}
        ]
    }
    
    players = pos_db.get(formation, pos_db["4-3-3"])
    player_html = "".join([f"""
        <div style="position: absolute; top: {p['t']}; left: {p['l']}; transform: translate(-50%, -50%); z-index: 10;">
            <div style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #00E5FF; background: #0B0E14; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(0,229,255,0.5);">
                <span class="material-icons-outlined" style="color: #00E5FF; font-size: 16px;">{p.get('i', 'person')}</span>
            </div>
        </div>
    """ for p in players])

    # HTML Şablonu (F-string çakışmasını önlemek için {{ }} kullanıldı)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
        <style>
            body {{ background-color: #0B0E14; color: #cbd5e1; font-family: 'Rajdhani', sans-serif; margin: 0; padding: 10px; overflow: hidden; }}
            .glass-panel {{ background: rgba(19, 27, 38, 0.85); backdrop-filter: blur(10px); border: 1px solid rgba(0, 229, 255, 0.15); border-radius: 8px; }}
            .cyber-pitch {{ background: #0B0E14; position: relative; border: 1px solid #1e293b; border-radius: 8px; height: 100%; overflow: hidden; }}
            .pitch-lines {{ position: absolute; inset: 20px; border: 1px solid rgba(255,255,255,0.05); }}
        </style>
    </head>
    <body>
        <header style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="material-icons-outlined" style="color: #00E5FF;">radar</span>
                <span style="font-weight: bold; letter-spacing: 2px; color: white;">DATALIG OS</span>
            </div>
            <div style="display: flex; gap: 10px;">
                <div class="glass-panel" style="padding: 2px 15px; border-bottom: 2px solid #ef4444; font-size: 10px;">{context['focus_team']}</div>
                <div class="glass-panel" style="padding: 2px 15px; border-bottom: 2px solid #00E5FF; font-size: 10px; color: #00E5FF;">{formation}</div>
            </div>
        </header>

        <div style="display: grid; grid-template-columns: repeat(12, 1fr); gap: 15px; height: 480px;">
            <div class="glass-panel" style="grid-column: span 3; padding: 15px; display: flex; flex-direction: column;">
                <div style="font-size: 10px; color: #00E5FF; border-bottom: 1px solid #1e293b; padding-bottom: 5px; margin-bottom: 10px; letter-spacing: 1px;">INTELLIGENCE FEED</div>
                <div style="flex: 1; overflow-y: auto; font-family: monospace; font-size: 10px; color: #94a3b8; line-height: 1.5;">{clean_report}</div>
            </div>
            
            <div class="cyber-pitch" style="grid-column: span 9;">
                <div class="pitch-lines">
                    <div style="position: absolute; top: 50%; left: 0; right: 0; h: 1px; background: rgba(255,255,255,0.1);"></div>
                    <div style="position: absolute; top: 50%; left: 50%; width: 100px; height: 100px; border: 1px solid rgba(255,255,255,0.1); border-radius: 50%; transform: translate(-50%, -50%);"></div>
                    <div style="position: absolute; top: 0; left: 50%; width: 140px; height: 60px; border: 1px solid rgba(255,255,255,0.1); border-top: 0; transform: translateX(-50%);"></div>
                    <div style="position: absolute; bottom: 0; left: 50%; width: 140px; height: 60px; border: 1px solid rgba(255,255,255,0.1); border-bottom: 0; transform: translateX(-50%);"></div>
                    <div style="position: absolute; top: 0; left: 50%; width: 60px; height: 4px; background: rgba(0,229,255,0.3); transform: translateX(-50%); border-radius: 0 0 4px 4px;"></div>
                    <div style="position: absolute; bottom: 0; left: 50%; width: 60px; height: 4px; background: rgba(239,68,68,0.3); transform: translateX(-50%); border-radius: 4px 4px 0 0;"></div>
                </div>
                {player_html}
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(html_code, height=580)

# --- 7. ANA ARAYÜZ ---
render_cyber_ui(st.session_state.tactic_context)

st.markdown("---")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları göster
for msg in st.session_state.messages[-3:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Giriş
if prompt := st.chat_input("Taktiksel komut bekliyorum..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.status("🔍 Analiz Ediliyor...", expanded=False):
            vec = embeddings.embed_query(prompt)
            res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
            archive = "\n".join([m['metadata']['text'] for m in res['matches']])
            ans = get_manager_analysis(prompt, archive)
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        
        # Bağlam Güncelleme
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        elif "Galatasaray" in ans: st.session_state.tactic_context['focus_team'] = "GALATASARAY"
        
        for f in ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"]:
            if f in ans or f in prompt: st.session_state.tactic_context['formation'] = f
            
        st.session_state.tactic_context['scouting_report'] = ans
        st.session_state.tactic_context['last_update'] = time.time()
        st.rerun()
