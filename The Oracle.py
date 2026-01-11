import streamlit as st
import json
import os
from datetime import datetime

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE v4", page_icon="👁️", layout="wide")

# CSS: Karanlık Mode ve Modern Minimalizm (Sidebar Gizleme Dahil)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #050505; color: #e0e0e0; }
    .assistant-panel {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(0, 255, 157, 0.15);
        text-align: center;
        transition: 0.3s;
        margin-bottom: 20px;
    }
    .assistant-panel:hover { border: 1px solid #00ff9d; background: rgba(0, 255, 157, 0.05); cursor: pointer; }
    .stChatInputContainer { padding-bottom: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME (SCOUT BOT ENTEGRASYONU) ---
def load_scout_data():
    if os.path.exists("hub_data.json"):
        with open("hub_data.json", "r") as f:
            return json.load(f)
    return {
        "last_update": "Veri Bekleniyor...",
        "next_match": "Samsunspor - Fenerbahçe",
        "match_date": "11 Ocak 2026 | 21:45",
        "weather": "12°C Yağmurlu",
        "expert_notes": "Scout botu henüz raporu hazırlamadı."
    }

# --- 3. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- 4. ORACLE MOTORU ---
try:
    from google import genai
    from google.genai import types
except:
    st.error("Kütüphane Hatası!")

def oracle_engine(prompt):
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    config = types.GenerateContentConfig(
        system_instruction="Sen THE ORACLE'sın. Tedesco'nun Fenerbahçesi'nin baş taktik danışmanısın. Kısa ve stratejik konuş.",
        temperature=0.2,
        thinking_config={"include_thoughts": True, "thinking_level": "minimal"}
    )
    res = client.models.generate_content(model="gemini-3-flash-preview", contents=[prompt], config=config)
    return res.text

# --- 5. UI: ÜST ASİSTAN PANELİ ---
def render_assistant_panel(data):
    st.markdown(f"""
    <div class="assistant-panel">
        <span style="color: #888; font-size: 14px; letter-spacing: 2px;">GELECEK MAÇ</span><br>
        <b style="font-size: 24px; color: #00ff9d;">{data['next_match']}</b><br>
        <span style="font-size: 16px; color: #bbb;">{data['match_date']} • {data['weather']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Görünmez buton ile tıklama hissi
    if st.button("🏟️ SAVAŞ ODASINA (WAR ROOM) GİRİŞ YAP", use_container_width=True):
        st.session_state.page = "war_room"
        st.rerun()

# --- 6. SAYFA: HOME (CHAT MODU) ---
def show_home():
    data = load_scout_data()
    render_assistant_panel(data)
    
    st.markdown("<br><h1 style='text-align: center; color: #333;'>👁️</h1>", unsafe_allow_html=True)
    
    # Chat Geçmişi
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, bugün hangi bölgeye sızalım?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle derin analize geçiyor..."):
                ans = oracle_engine(prompt)
                st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 7. SAYFA: WAR ROOM (DERİN ANALİZ) ---
def show_war_room():
    data = load_scout_data()
    
    col_back, col_title = st.columns([1, 9])
    with col_back:
        if st.button("← Geri"):
            st.session_state.page = "home"
            st.rerun()
    with col_title:
        st.title(f"🏟️ WAR ROOM: {data['next_match']}")

    st.markdown("---")
    
    # War Room Grid Sistemi
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Tahmini xG", value="2.10", delta="+0.45")
        st.info(f"**Uzman Notu:** {data['expert_notes']}")
    with c2:
        st.metric(label="Saha Baskısı", value="%68", delta="Yüksek")
        st.warning("**Kritik Risk:** Rakip 75+ dakikada fiziksel düşüş yaşıyor.")
    with c3:
        st.metric(label="Hava Etkisi", value="Sert", delta="Yağmurlu")
        st.success("**Taktik Öneri:** Uzaktan şut denemelerini artır.")

    st.markdown("---")
    st.subheader("💬 Savaş Planı Sentezi")
    # Savaş odasına özel mikro chat veya taktik tahtası buraya gelecek
    st.caption("Burada sadece bu maça özel savaş planını konuşabilirsin...")

# --- 8. YÖNLENDİRME ---
if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "war_room":
    show_war_room()
