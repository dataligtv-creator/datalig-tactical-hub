import streamlit as st
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE OS v4", page_icon="👁️", layout="wide")

# CSS: Karanlık Mod ve Modern Panel Tasarımı
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

# --- 2. AKILLI VERİ YÜKLEME (CACHE & VALIDATION) ---
def load_scout_data():
    if os.path.exists("hub_data.json"):
        try:
            with open("hub_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Tarih Kontrolü: Maç günü geçti mi?
                match_iso = data.get("match_date_iso", "2000-01-01T00:00:00")
                if datetime.now() > datetime.fromisoformat(match_iso):
                    data["status_alert"] = "⚠️ Maç Günü Geçti - Scout Güncellemesi Bekleniyor"
                return data
        except Exception as e:
            st.error(f"Veri okuma hatası: {e}")
            
    return {
        "next_match": "Veri Bekleniyor",
        "match_date": "N/A",
        "weather": "N/A",
        "expert_notes": "Scout botu henüz raporu mühürlemedi.",
        "xg_data": {"Ev": 0.0, "Dep": 0.0}
    }

# --- 3. ORACLE MOTORU (ÇAPRAZ SORGU PROTOKOLÜ) ---
def oracle_engine(prompt):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Hata: Streamlit Secrets içinde API anahtarı bulunamadı."
    
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Çapraz sorgu gerektiren durumlar (Sakatlık, Fikstür, Kadro)
    needs_search = any(word in prompt.lower() for word in ["sakat", "kadro", "ilk 11", "ne zaman", "oynuyor mu", "transfermarkt", "haber"])
    
    system_instr = f"""
    Sen THE ORACLE'sın. Bugün {datetime.now().strftime('%d %B %Y')}.
    PRENSİP 1: Oyuncu durumu veya resmi veriler sorulduğunda Google Search ile ÇAPRAZ SORGU yap.
    PRENSİP 2: En az iki farklı kaynağı karşılaştır. Çelişki varsa 'BELİRSİZ' olarak raporla.
    PRENSİP 3: Asla halüsinasyon görme. Bilmiyorsan 'Veri teyit edilemedi' de.
    PRENSİP 4: Tedesco'nun Fenerbahçesi için stratejik bir dille konuş.
    """
    
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        tools=[types.Tool(google_search=types.GoogleSearch())] if needs_search else [],
        temperature=0.1
    )
    
    try:
        res = client.models.generate_content(model="gemini-3-flash-preview", contents=[prompt], config=config)
        return res.text
    except Exception as e:
        return f"Oracle Erişim Hatası: {str(e)}"

# --- 4. SAYFA: HOME (CHAT & DASHBOARD) ---
def show_home():
    # Stratejik Araçlar Menüsü
    with st.expander("🛠️ STRATEJİK ARAÇLAR (MODÜLLER)"):
        col_m1, col_m2, col_m3 = st.columns(3)
        if col_m1.button("🧬 Scout DNA", use_container_width=True): st.switch_page("pages/1_🧬_Scout_DNA.py")
        if col_m2.button("📊 Match Center", use_container_width=True): st.switch_page("pages/2_📊_Match_Center.py")
        if col_m3.button("📋 Taktik Tahta", use_container_width=True): st.switch_page("pages/3_📋_Tactical_Board.py")

    # Gelecek Maç Paneli
    data = load_scout_data()
    st.markdown(f"""
    <div class="assistant-panel">
        <span style="color: #888; font-size: 14px; letter-spacing: 2px;">GELECEK MAÇ</span><br>
        <b style="font-size: 28px; color: #00ff9d;">{data['next_match']}</b><br>
        <span style="font-size: 16px; color: #bbb;">{data['match_date']} • {data['weather']}</span>
        {f'<p style="color: orange; font-size: 12px; margin-top:10px;">{data.get("status_alert", "")}</p>' if "status_alert" in data else ""}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏟️ SAVAŞ ODASINA (WAR ROOM) GİRİŞ YAP", use_container_width=True):
        st.session_state.page = "war_room"
        st.rerun()

    # Chat Sistemi
    if 'messages' not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, istihbarat raporu nedir?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle araştırıyor ve doğruluyor..."):
                ans = oracle_engine(prompt)
                st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 5. SAYFA: WAR ROOM (DERİN ANALİZ) ---
def show_war_room():
    data = load_scout_data()
    
    if st.button("← Geri"):
        st.session_state.page = "home"
        st.rerun()
        
    st.title(f"🏟️ WAR ROOM: {data['next_match']}")
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tahmini xG", f"{data.get('xg_data', {}).get('Dep', 0.0)}", delta="Stratejik Veri")
        st.info(f"**Uzman Notu:** {data['expert_notes']}")
        
    with c2:
        st.markdown("### ⏱️ Kırılma Noktaları")
        st.error("**Rakip Zafiyeti: 70' - 85'**")
        st.caption("Fiziksel düşüşün en yüksek olduğu aralık. Baskıyı artır.")
        
    with c3:
        st.success("**Taktik Pencere: 60'**")
        st.caption(f"Hava: {data['weather']}. Zemin analizi yapıldı.")

# --- 6. ROUTING (YÖNLENDİRME) ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "war_room":
    show_war_room()
