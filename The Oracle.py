import streamlit as st
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE OS v5", page_icon="👁️", layout="wide")

# CSS: Oracle "Karanlık Tema" ve Profesyonel Panel
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #050505; color: #e0e0e0; }
    .assistant-panel {
        background: linear-gradient(145deg, rgba(10,10,10,1) 0%, rgba(30,30,30,1) 100%);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(0, 255, 157, 0.3);
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 255, 157, 0.1);
    }
    .stChatInputContainer { padding-bottom: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HİBRİT VERİ YÜKLEME (JSON & VALIDATION) ---
def load_oracle_memory():
    if os.path.exists("hub_data.json"):
        try:
            with open("hub_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Modelin "Gerçeklik Çapası" (Context Injection)
                memory_context = f"""
                [GÜNCEL DURUM RAPORU - {data.get('last_sync', 'N/A')}]
                Fikstür: {data.get('next_battle', {}).get('match', 'Bilinmiyor')}
                Tarih/Hava: {data.get('next_battle', {}).get('kick_off', 'N/A')} | {data.get('next_battle', {}).get('weather', 'N/A')}
                
                KADRO DURUMU:
                - Gidenler/Yoklar: {', '.join(data.get('active_squad', {}).get('out_of_squad', []))}
                - Yeni Eklenenler: {', '.join(data.get('active_squad', {}).get('key_additions', []))}
                - Kritik Eksikler: {data.get('active_squad', {}).get('squad_depth_report', 'N/A')}
                
                FORM GRAFİĞİ:
                {data.get('recent_form', [])}
                """
                return data, memory_context
        except Exception as e:
            st.error(f"Bellek okuma hatası: {e}")
    
    return {}, "Canlı veri bulunamadı. Genel futbol bilgini kullan."

# --- 3. ORACLE 3.1 PRO MOTORU ---
def oracle_engine(prompt, memory_context):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Hata: API anahtarı eksik."
    
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Bugünün tam tarihi
    current_date = datetime.now().strftime('%d %B %Y')
    
    # SISTEM TALİMATI: 3.1 Pro için Oracle Kişiliği
    system_instr = f"""
    Sen THE ORACLE v5.0 (3.1 Pro) elit futbol stratejistisin. 
    Bugün {current_date}. 28 Şubat 2026 gerçekliğinde yaşıyorsun.

    GÖREVİN:
    1. Aşağıdaki [GERÇEKLİK VERİSİ]'ni hafızandaki her şeyin üstünde tut.
    2. Eğer bir oyuncu 'out_of_squad' listesindeyse, o artık yoktur. Asla 'Fenerbahçe'de oynuyor' deme.
    3. Taktiksel analizlerinde Tedesco'nun modern asimetrik futbol felsefesini benimse.
    4. Cevapların kısa, vurucu ve stratejik olsun.

    [GERÇEKLİK VERİSİ]:
    {memory_context}
    """
    
    # Kota dostu çapraz sorgu ihtiyacı tespiti
    needs_web = any(word in prompt.lower() for word in ["sakat", "transfer", "son dakika", "kim geldi"])
    
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        tools=[types.Tool(google_search=types.GoogleSearch())] if needs_web else [],
        temperature=0.3, # Taktiksel yaratıcılık ve tutarlılık dengesi
        model="gemini-3.1-pro" # Ana işlemci 3.1 Pro
    )
    
    try:
        res = client.models.generate_content(model="gemini-3.1-pro", contents=[prompt], config=config)
        return res.text
    except Exception as e:
        return f"Oracle Zihin Hatası: {str(e)}"

# --- 4. UI: HOME ---
def show_home():
    # Veri Yükleme
    hub_data, memory_context = load_oracle_memory()
    
    # DashBoard (Görsel Paneli)
    match = hub_data.get('next_battle', {}).get('match', 'Veri Bekleniyor')
    kick_off = hub_data.get('next_battle', {}).get('kick_off', 'N/A')
    
    st.markdown(f"""
    <div class="assistant-panel">
        <span style="color: #00ff9d; font-size: 12px; letter-spacing: 3px;">ORACLE TACTICAL HUB v5</span><br>
        <b style="font-size: 32px;">{match}</b><br>
        <span style="color: #888;">{kick_off} | {hub_data.get('next_battle', {}).get('weather', '')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Chat Sistemi
    if 'messages' not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, taktiksel raporu hazırla..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle 3.1 Pro verileri sentezliyor..."):
                ans = oracle_engine(prompt, memory_context)
                st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 5. ROUTING ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    show_home()
