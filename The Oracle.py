import streamlit as st
from google import genai
from google.genai import types
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
import uuid
from PIL import Image

# --- 1. SİSTEM BAŞLATMA VE ORTAK BELLEK ---
st.set_page_config(page_title="DATALIG Football OS", page_icon="⚽", layout="wide")

if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Genel",
        "formation": "Bilinmiyor",
        "players": [],
        "tactical_notes": ""
    }

@st.cache_resource
def init_system():
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    idx = pc.Index("regista-arsiv")
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return client, idx, embeds

client, pinecone_index, embeddings = init_system()

# --- 2. 🧠 YÖNETİCİ ANALİZ MOTORU ---
def get_manager_analysis(query, archive_context):
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    config = types.GenerateContentConfig(
        tools=[search_tool],
        temperature=0.7,
        system_instruction=f"""
        Sen 'DATALIG Football OS' sisteminin ana yöneticisisin. 
        GÖREVİN: 
        1. Kullanıcının sorusundan Takım, Formasyon ve Oyuncu bilgilerini ayıkla.
        2. Arşiv verisiyle ({archive_context}) harmanla.
        3. Yanıtında mutlaka WhoScored ve FBref verilerine dayanan 'Isı Haritası Özeti' ver.
        4. VERİ AKTARIMI: Yanıtının sonunda şu formatta bir özet bırak: 
           [CONTEXT: TAKIM=X, FORMASYON=Y, OYUNCULAR=A,B,C]
        """
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[query],
        config=config
    )
    return response.text

# --- 3. 🖥️ ARAYÜZ VE BAĞLAMSAL FİLTRELEME ---
st.markdown(f"### ⚽ DATALIG <span style='color:#94a3b8;'>ORACLE V5.0</span>", unsafe_allow_html=True)

# Mevcut Taktiksel Odak Göstergesi
with st.sidebar:
    st.markdown("### 🎯 MEVCUT ODAK")
    st.info(f"**Takım:** {st.session_state.tactic_context['focus_team']}\n\n"
            f"**Diziliş:** {st.session_state.tactic_context['formation']}")
    
    if st.button("🗑️ Odağı Temizle"):
        st.session_state.tactic_context = {"focus_team": "Genel", "formation": "Bilinmiyor", "players": [], "tactical_notes": ""}
        st.rerun()

# ANA CHAT
if prompt := st.chat_input("Taktiksel bir senaryo girin (Örn: Fenerbahçe 4-3-3 hücum analizi)..."):
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # Pinecone + AI Analizi
        vec = embeddings.embed_query(prompt)
        res = pinecone_index.query(vector=vec, top_k=3, include_metadata=True)
        archive = "\n".join([m['metadata']['text'] for m in res['matches']])
        
        analysis = get_manager_analysis(prompt, archive)
        st.markdown(analysis)
        
        # --- 🤖 AKILLI BAĞLAM GÜNCELLEME ---
        # AI yanıtından takım ve formasyon bilgilerini çekip session_state'e atıyoruz.
        if "Fenerbahçe" in analysis or "Fenerbahçe" in prompt:
            st.session_state.tactic_context['focus_team'] = "Fenerbahçe"
        if "4-3-3" in analysis or "4-3-3" in prompt:
            st.session_state.tactic_context['formation'] = "4-3-3"
        
        st.session_state.tactic_context['tactical_notes'] = analysis
        st.success("✅ Bağlam güncellendi. Scout DNA ve Tactical Board sayfaları bu verilere göre hazırlandı.")
