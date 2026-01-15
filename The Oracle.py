import streamlit as st
import json
import os
from datetime import datetime

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE OS v4", page_icon="👁️", layout="wide")

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
        margin-bottom: 20px;
    }
    .stChatInputContainer { padding-bottom: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ZEKİ VERİ YÜKLEME (SMART CACHE) ---
def load_scout_data():
    default_data = {
        "next_match": "Veri Çekiliyor...",
        "match_date": "N/A",
        "match_date_iso": "2000-01-01T00:00:00",
        "weather": "N/A",
        "expert_notes": "Scout botu taze veri arıyor...",
        "xg_data": {"Ev": 0.0, "Dep": 0.0}
    }
    
    if os.path.exists("hub_data.json"):
        with open("hub_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Maç tarihi kontrolü
            match_iso = data.get("match_date_iso", "2000-01-01T00:00:00")
            try:
                if datetime.now() > datetime.fromisoformat(match_iso):
                    data["status_alert"] = "⚠️ Maç Günü Geçti - Yeni Veri Bekleniyor"
            except:
                pass
            return data
    return default_data

# --- 3. ORACLE MOTORU (GOOGLE SEARCH ENTEGRASYONLU) ---
from google import genai
from google.genai import types

def oracle_engine(prompt):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Hata: Secrets içinde API anahtarı bulunamadı."
    
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Soru maç/hava durumu ile ilgiliyse Google Search'ü tetikle
    use_search = any(word in prompt.lower() for word in ["ne zaman", "hava", "maçı", "kadro", "sakat"])
    
    config = types.GenerateContentConfig(
        system_instruction="Sen THE ORACLE'sın. Tedesco'nun Fenerbahçesi'nin baş stratejistisin. Kısa ve net konuş.",
        tools=[types.Tool(google_search=types.GoogleSearch())] if use_search else [],
        temperature=0.2
    )
    
    try:
        res = client.models.generate_content(model="gemini-3-flash-preview", contents=[prompt], config=config)
        return res.text
    except Exception as e:
        return f"Oracle Hatası: {str(e)}"

# --- 4. NAVİGASYON ---
def render_navigation():
    with st.expander("🛠️ STRATEJİK ARAÇLAR (MODÜLLER)"):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("🧬 Scout DNA", use_container_width=True): st.switch_page("pages/1_🧬_Scout_DNA.py")
            if st.button("📊 Match Center", use_container_width=True): st.switch_page("pages/2_📊_Match_Center.py")
        with col_m2:
            if st.button("📋 Taktik Tahta", use_container_width=True): st.switch_page("pages/3_📋_Tactical_Board.py")
            if st.button("🔥 Pressure Lab", use_container_width=True): st.switch_page("pages/4_🔥_Pressure_Lab.py")
        with col_m3:
            if st.button("🎥 Video Analiz", use_container_width=True): st.switch_page("pages/5_🎥_Video_Analiz.py")

# --- 5. SAYFA: HOME ---
def show_home():
    render_navigation()
    data = load_scout_data()
    
    st.markdown(f"""
    <div class="assistant-panel">
        <span style="color: #888; font-size: 14px; letter-spacing: 2px;">GELECEK MAÇ</span><br>
        <b style="font-size: 28px; color: #00ff9d;">{data['next_match']}</b><br>
        <span style="font-size: 16px; color: #bbb;">{data['match_date']} • {data['weather']}</span>
        {f'<p style="color: orange; font-size: 12px;">{data.get("status_alert", "")}</p>' if "status_alert" in data else ""}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏟️ SAVAŞ ODASINA (WAR ROOM) GİRİŞ YAP", use_container_width=True):
        st.session_state.page = "war_room"
        st.rerun()

    # Chat
    if 'messages' not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, strateji nedir?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            ans = oracle_engine(prompt)
            st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 6. SAYFA: WAR ROOM ---
def show_war_room():
    data = load_scout_data()
    if st.button("← Geri"):
        st.session_state.page = "home"
        st.rerun()
    
    st.title(f"🏟️ WAR ROOM: {data['next_match']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tahmini xG", f"{data.get('xg_data', {}).get('Dep', 0.0)}", delta="Hücum Hattı")
        st.info(f"**Uzman Notu:** {data['expert_notes']}")
    
    with col2:
        st.markdown("### ⏱️ Kırılma Noktaları")
        st.error("**Rakip Düşüşü: 70' - 85'**")
        st.caption("Samsunspor son çeyrekte fiziksel olarak çözülüyor.")
    
    with col3:
        st.success("**Taktik Pencere: 60'**")
        st.caption("Tedesco'nun dikey geçişleri için en uygun hamle dakikası.")

# --- 7. ROUTING ---
if 'page' not in st.session_state: st.session_state.page = "home"
if st.session_state.page == "home": show_home()
else: show_war_room()
