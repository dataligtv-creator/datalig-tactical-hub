import streamlit as st
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE OS v5.2", page_icon="👁️", layout="wide")

# CSS: Karanlık Tema ve Sidebar Onarımı
st.markdown("""
    <style>
    /* Sidebar'ı ve Menüleri Görünür Kılıyoruz */
    section[data-testid="stSidebar"] { display: block !important; background-color: #0a0a0a; border-right: 1px solid #1a1a1a; }
    .main { background-color: #050505; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    
    /* Dashboard Paneli Tasarımı */
    .assistant-panel {
        background: linear-gradient(145deg, #0f0f0f 0%, #1a1a1a 100%);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(0, 255, 157, 0.3);
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .status-badge {
        background-color: rgba(0, 255, 157, 0.1);
        color: #00ff9d;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        letter-spacing: 2px;
        font-weight: bold;
        border: 1px solid rgba(0, 255, 157, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME VE SENKRONİZASYON (SCOUT DNA UYUMLU) ---
def load_oracle_memory():
    file_path = "hub_data.json"
    
    # Varsayılan (Boş) Veri Seti
    default_display = {
        "match": "Veri Bekleniyor...",
        "time": "Scout.py Çalıştırılmadı",
        "weather": "N/A",
        "sync": "N/A"
    }
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Scout v3.1 Şemasına Göre Veri Çekme
                next_battle = data.get("next_battle", {})
                squad = data.get("active_squad", {})
                
                # Display için veriyi rafine et
                display_data = {
                    "match": next_battle.get("match", "Fikstür Tanımsız"),
                    "time": next_battle.get("kick_off", "Zaman Belirlenmedi"),
                    "weather": next_battle.get("weather", "Hava Durumu Bilgisi Yok"),
                    "sync": data.get("last_sync", datetime.now().strftime("%H:%M"))
                }
                
                # 3.1 Pro İçin Context Oluştur (Gerçeklik Çapası)
                memory_context = f"""
                [STRATEJİK GERÇEKLİK VERİSİ]
                Son Senkronizasyon: {display_data['sync']}
                Rakip: {display_data['match']}
                Kadro Durumu: {squad.get('squad_depth_report', 'Veri yok')}
                Ayrılanlar/Yoklar: {', '.join(squad.get('out_of_squad', ['Yok']))}
                Yeni Gelenler: {', '.join(squad.get('key_additions', ['Yok']))}
                """
                
                return display_data, memory_context
        except Exception as e:
            st.error(f"⚠️ JSON Okuma Hatası: {e}")
            
    return default_display, "Hafıza şu an boş. Genel bilgilerle devam et."

# --- 3. ORACLE 3.1 PRO MOTORU (HİBRİT ANALİZ) ---
def oracle_engine(prompt, memory_context):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Hata: Streamlit Secrets içinde API anahtarı (GOOGLE_API_KEY) tanımlı değil."
    
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Bugünün tarihi
    current_date = datetime.now().strftime('%d %B %Y')
    
    # Sistem Talimatı (Oracle Kimliği)
    system_instr = f"""
    Sen THE ORACLE v5.2 (3.1 Pro) üst düzey futbol stratejistisin. Bugün {current_date}.
    
    PRENSİP 1: Hafızandaki eski (2024-2025) verileri tamamen unut. 
    PRENSİP 2: Sana sunulan [STRATEJİK GERÇEKLİK VERİSİ]'ne %100 sadık kal.
    PRENSİP 3: Bir oyuncu 'Ayrılanlar' listesindeyse, o artık kadroda değildir.
    PRENSİP 4: Analizlerin teknik, derinlikli ve çözüm odaklı olsun.
    
    {memory_context}
    """
    
    # Akıllı Google Search Tetikleyici
    needs_web = any(word in prompt.lower() for word in ["sakat", "transfer", "son dakika", "haber", "kadro", "ilk 11"])
    
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        tools=[types.Tool(google_search=types.GoogleSearch())] if needs_web else [],
        temperature=0.3,
        model="gemini-3.1-pro" # Eğer Studio'da 3.1 Pro yoksa burayı gemini-2.0-flash yapabilirsin
    )
    
    try:
        res = client.models.generate_content(model="gemini-3.1-pro", contents=[prompt], config=config)
        return res.text
    except Exception as e:
        return f"Oracle Erişim Hatası: {str(e)}"

# --- 4. ANA SAYFA DASHBOARD (GÖRSEL PANEL) ---
def show_home():
    display_data, memory_context = load_oracle_memory()
    
    # GÖSEL PANEL (Onarılmış Bölüm)
    st.markdown(f"""
    <div class="assistant-panel">
        <div style="margin-bottom: 10px;">
            <span class="status-badge">THE ORACLE TACTICAL HUB • LIVE</span>
        </div>
        <div style="margin-top: 20px;">
            <span style="color: #888; font-size: 14px; letter-spacing: 2px;">SIRADAKİ GÖREV</span><br>
            <b style="font-size: 36px; color: #ffffff; text-shadow: 0 0 15px rgba(0,255,157,0.3);">
                {display_data['match']}
            </b><br>
            <span style="font-size: 18px; color: #00ff9d; font-weight: 500;">{display_data['time']}</span><br>
            <span style="font-size: 14px; color: #666; margin-top: 5px; display: block;">
                📍 Son Senkronizasyon: {display_data['sync']} | ☁️ {display_data['weather']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stratejik Modüller (Görsel Butonlar)
    st.write("### 🛠️ Stratejik Modüller")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧬 Scout DNA", use_container_width=True): st.info("Yan menüden 'Scout DNA' sayfasına geçiniz.")
    with c2:
        if st.button("📊 Match Center", use_container_width=True): st.info("Yan menüden 'Match Center' sayfasına geçiniz.")
    with c3:
        if st.button("📋 Taktik Tahta", use_container_width=True): st.info("Yan menüden 'Taktik Tahta' sayfasına geçiniz.")

    st.markdown("---")

    # CHAT SİSTEMİ
    if 'messages' not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, taktiksel bir soru sor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle 3.1 Pro verileri analiz ediyor..."):
                ans = oracle_engine(prompt, memory_context)
                st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 5. ROUTING ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    show_home()
