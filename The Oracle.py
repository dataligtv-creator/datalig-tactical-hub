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
        <link href="
