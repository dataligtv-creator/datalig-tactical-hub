import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

# --- 2. BEYİN (SESSION STATE) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "HAZIR",
        "formation": "4-3-3",
        "scouting_report": "Sistem aktif. Taktiksel veri bekleniyor...",
        "last_update": time.time()
    }

# --- 3. SİSTEM BAŞLATMA (PAID TIER GEMINI 2.5) ---
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
    MODEL_ID = "gemini-2.0-flash" # Gemini 2.5 Paid Tier gücü
    search_tool = types.Tool(google_search=types.GoogleSearch())
    current_date = "2 Ocak 2026"
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction=f"Tarih: {current_date}. Sen DATALIG Baş Stratejistisin. İnternetten WhoScored, FBref ve haberleri tara. Yanıtın sonunda mutlaka [TEAM: ..., FORMATION: ...] ekle."
    )
    response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
    return response.text

# --- 4. 🎮 TAKTİKSEL ŞABLON TETİKLEYİCİSİ ---
def run_command(cmd_name):
    team = st.session_state.tactic_context['focus_team']
    prompts = {
        "RAKIP": f"{team} takımının sıradaki resmi rakibini internetten bul ve zayıf noktalarını analiz et.",
        "SAVUNMA": f"{team} için bu haftaki rakibe özel bir savunma yerleşimi ve pres planı hazırla.",
        "HUCUM": f"{team} için hızlı hücum geçişleri ve kilit pas kanalları analizi yap.",
        "TRANSFER": f"{team} için Ocak 2026 transfer döneminde adı geçen oyuncuların taktiksel uyumunu incele."
    }
    
    with st.spinner("Oracle veri katmanlarını işliyor..."):
        ans = get_manager_analysis(prompts[cmd_name])
        st.session_state.tactic_context['scouting_report'] = ans
        
        # Analizden takım ve diziliş bilgisini çekme
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        elif "3-5-2" in ans: st.session_state.tactic_context['formation'] = "3-5-2"
        st.rerun()

# --- 5. 🏟️ STITCH UI MOTORU ---
def render_dashboard(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    team = context['focus_team']
    form = context['formation']
    
    # Diziliş Piyonları
    pos_db = {
        "4-3-3": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (55, 30, "8"), (60, 50, "6"), (55, 70, "10"), (30, 20, "7"), (25, 50, "9"), (30, 80, "11")],
        "4-2-3-1": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (65, 40, "6"), (65, 60, "8"), (45, 20, "7"), (42, 50, "10"), (45, 80, "11"), (25, 50, "9")]
    }
    players_html = "".join([f"<div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:20;'><div style='width:22px; height:22px; border-radius:50%; background:white; border:2px solid #13c8ec; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:bold; color:black; box-shadow: 0 0 10px rgba(19,200,236,0.6);'>{num}</div></div>" for t, l, num in pos_db.get(form, pos_db["4-3-3"])])

    # Dashoard HTML
    full_html = f"""
    <!DOCTYPE html>
    <html class="dark">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap" rel="stylesheet">
        <style>
            body {{ background: #111718; color: white; font-family: sans-serif; margin:0; overflow:hidden; }}
            .pitch-stripes {{ background-color: #173828; background-image: repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255, 255, 255, 0.03) 50px, rgba(255, 255, 255, 0.03) 100px); }}
            .panel {{ background: #111718; border: 1px solid #283639; border-radius: 8px; }}
            .oracle-box {{ background: #0b1011; border: 1px solid #283639; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94a3b8; padding: 15px; height: 350px; overflow-y: auto; }}
        </style>
    </head>
    <body class="p-4">
        <div class="grid grid-cols-12 gap-4 h-screen">
            <div class="col-span-3 flex flex-col gap-4">
                <div class="panel p-4">
                    <h3 class="text-xs font-bold text-primary mb-3 uppercase tracking-widest text-[#13c8ec]">Tactical Command</h3>
                    <p class="text-[10px] text-gray-500 mb-4">Aşağıdaki kontrolleri Streamlit Sidebar'dan yönetin.</p>
                </div>
                <div class="panel p-4 flex-1">
                    <h3 class="text-xs font-bold text-[#13c8ec] mb-3 uppercase tracking-widest">Oracle Intelligence</h3>
                    <div class="oracle-box">{report}</div>
                </div>
            </div>

            <div class="col-span-6 flex items-center justify-center bg-[#0f1516] rounded-xl border border-[#283639] relative">
                <div class="relative w-[400px] h-[580px] pitch-stripes rounded-lg border-2 border-white/20 overflow-hidden">
                    <div style="position:absolute; inset:20px; border:1px solid rgba(255,255,255,0.3);">
                        <div style="position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.3);"></div>
                        <div style="position:absolute; top:0; left:50%; width:160px; height:60px; border:1px solid rgba(255,255,255,0.3); border-top:0; transform:translateX(-50%);"></div>
                        <div style="position:absolute; bottom:0; left:50%; width:160px; height:60px; border:1px solid rgba(255,255,255,0.3); border-bottom:0; transform:translateX(-50%);"></div>
                    </div>
                    {players_html}
                </div>
            </div>

            <div class="col-span-3 flex flex-col gap-4">
                <div class="panel p-6">
                    <h3 class="text-xs font-bold text-[#13c8ec] mb-4 uppercase tracking-widest">Match Metrics</h3>
                    <div class="mb-4">
                        <span class="text-[10px] text-gray-500 block uppercase">Active Team</span>
                        <span class="text-lg font-bold">{team}</span>
                    </div>
                    <div class="mb-4">
                        <span class="text-[10px] text-gray-500 block uppercase">Formation</span>
                        <span class="text-lg font-bold text-[#13c8ec]">{form}</span>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return components.html(full_html, height=720)

# --- 6. 🎮 SIDEBAR KONTROL MERKEZİ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/53/53283.png", width=50) # Opsiyonel logo
    st.title("DATALIG OS")
    st.markdown("---")
    
    st.subheader("🕹️ Taktiksel Tetikleyiciler")
    if st.button("🔍 RAKİP GÖZLEMİ", use_container_width=True): run_command("RAKIP")
    if st.button("🛡️ SAVUNMA REÇETESİ", use_container_width=True): run_command("SAVUNMA")
    if st.button("⚡ KARŞI ATAK PLANI", use_container_width=True): run_command("HUCUM")
    if st.button("📉 TRANSFER UYUMU", use_container_width=True): run_command("TRANSFER")
    
    st.markdown("---")
    st.info("Hızlı komutlar, aktif odağınızdaki takımı baz alarak Oracle'ı internette araştırmaya sevk eder.")

# --- 7. DASHBOARD RENDER ---
render_dashboard(st.session_state.tactic_context)

# Sohbet Girişi
st.markdown("---")
if prompt := st.chat_input("Daha spesifik bir soru sorun..."):
    with st.chat_message("assistant"):
        ans = get_manager_analysis(prompt)
        st.markdown(ans)
        st.session_state.tactic_context['scouting_report'] = ans
        if "Fenerbahçe" in ans or "Fenerbahçe" in prompt: st.session_state.tactic_context['focus_team'] = "FENERBAHÇE"
        st.rerun()
