import streamlit as st
import json
import os
import time
from datetime import datetime

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE OS v4", page_icon="👁️", layout="wide")

# CSS: Sidebar'ı gizle ve modern karanlık tema uygula
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
        "expert_notes": "Scout botu raporu hazırlıyor, birazdan burada olacak."
    }

# --- 3. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- 4. ORACLE MOTORU (GEMINI 3 FLASH) ---
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Gerekli kütüphaneler eksik: pip install google-genai")

def oracle_engine(prompt):
    # Secrets'tan API Key kontrolü
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Hata: secrets.toml veya GitHub Secrets içinde API anahtarı bulunamadı."
    
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    config = types.GenerateContentConfig(
        system_instruction="Sen THE ORACLE'sın. Tedesco'nun Fenerbahçesi'nin baş taktik danışmanısın. Kısa, öz ve stratejik konuş.",
        temperature=0.2,
        thinking_config={"include_thoughts": True, "thinking_level": "minimal"}
    )
    try:
        res = client.models.generate_content(model="gemini-3-flash-preview", contents=[prompt], config=config)
        return res.text
    except Exception as e:
        return f"Oracle erişim hatası: {str(e)}"

# --- 5. UI BİLEŞENİ: NAVİGASYON (ARAÇ ÇANTASI) ---
def render_navigation():
    with st.expander("🛠️ STRATEJİK ARAÇLAR (MODÜLLER)"):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("🧬 Scout DNA", use_container_width=True):
                st.switch_page("pages/1_🧬_Scout_DNA.py")
            if st.button("📊 Match Center", use_container_width=True):
                st.switch_page("pages/2_📊_Match_Center.py")
        with col_m2:
            if st.button("📋 Taktik Tahta", use_container_width=True):
                st.switch_page("pages/3_📋_Tactical_Board.py")
            if st.button("🔥 Pressure Lab", use_container_width=True):
                st.switch_page("pages/4_🔥_Pressure_Lab.py")
        with col_m3:
            if st.button("🎥 Video Analiz", use_container_width=True):
                st.switch_page("pages/5_🎥_Video_Analiz.py")
            if st.button("🔗 Pass Network", use_container_width=True):
                # Ana dizindeki dosyaya yönlendirme
                st.info("Pass Network için ana dizindeki dosyayı çalıştırın.")

# --- 6. SAYFA: HOME (CHAT & DASHBOARD) ---
def show_home():
    # Navigasyon en üstte (İsteğe bağlı alta da alınabilir)
    render_navigation()
    
    # Asistan Paneli
    data = load_scout_data()
    st.markdown(f"""
    <div class="assistant-panel">
        <span style="color: #888; font-size: 14px; letter-spacing: 2px;">GELECEK MAÇ</span><br>
        <b style="font-size: 28px; color: #00ff9d;">{data['next_match']}</b><br>
        <span style="font-size: 16px; color: #bbb;">{data['match_date']} • {data['weather']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏟️ SAVAŞ ODASINA (WAR ROOM) GİRİŞ YAP", use_container_width=True):
        st.session_state.page = "war_room"
        st.rerun()

    st.markdown("<h2 style='text-align: center; color: #222;'>THE ORACLE</h2>", unsafe_allow_html=True)
    
    # Chat Ekranı
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, bugün hangi bölgeye sızalım?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle araştırıyor..."):
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
    
    # War Room Özet Metrikler
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="Tahmini xG", value="2.10", delta="+0.45")
        st.info(f"**Uzman Notu:** {data['expert_notes']}")
    with c2:
        st.metric(label="Saha Baskısı", value="%68", delta="Yüksek")
        st.warning("**Kritik Risk:** Rakip 75+ dakikada fiziksel düşüş yaşıyor.")
    with c3:
        st.metric(label="Hava Etkisi", value="Sert", delta="Yağmurlu")
        st.success("**Taktik Öneri:** Islak zeminde uzaktan şut varyasyonlarını dene.")

    st.markdown("---")
    st.subheader("💬 Savaş Planı Sentezi")
    st.caption("Bu maç için özel taktikleri aşağıdan konuşabilirsin.")
    
    # War Room Özel Chat (Opsiyonel: Genel chat ile aynı geçmişi paylaşır)
    war_prompt = st.chat_input("Bu maç için özel bir direktif ver...")
    if war_prompt:
        st.session_state.messages.append({"role": "user", "content": f"[WAR ROOM] {war_prompt}"})
        st.session_state.page = "home" # Yanıt için ana ekrana döner
        st.rerun()

# --- 8. YÖNLENDİRME ---
if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "war_room":
    show_war_room()
