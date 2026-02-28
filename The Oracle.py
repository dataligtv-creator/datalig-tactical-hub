import streamlit as st
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# --- 1. SİSTEM & UI AYARLARI ---
st.set_page_config(page_title="THE ORACLE OS v5.1", page_icon="👁️", layout="wide")

# CSS: Karanlık Mod ve Sidebar'ı Tekrar Açan Düzenleme
st.markdown("""
    <style>
    /* Sidebar'ı görünür yapıyoruz */
    section[data-testid="stSidebar"] { display: block !important; background-color: #0a0a0a; }
    .main { background-color: #050505; color: #e0e0e0; }
    .assistant-panel {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 255, 157, 0.2);
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HİBRİT VERİ YÜKLEME (GÜNCEL SCOUT ŞEMASIYLA UYUMLU) ---
def load_oracle_memory():
    if os.path.exists("hub_data.json"):
        try:
            with open("hub_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Scout DNA'dan gelen yeni şemayı parse ediyoruz
                next_battle = data.get("next_battle", {})
                squad = data.get("active_squad", {})
                
                memory_context = f"""
                [GERÇEKLİK VERİSİ - {data.get('last_sync', 'N/A')}]
                Maç: {next_battle.get('match', 'Bilinmiyor')}
                Tarih/Hava: {next_battle.get('kick_off', 'N/A')} | {next_battle.get('weather', 'N/A')}
                
                KADRO ANALİZİ:
                - Eksikler/Ayrılanlar: {', '.join(squad.get('out_of_squad', []))}
                - Yeni Katılanlar: {', '.join(squad.get('key_additions', []))}
                - Rapor: {squad.get('squad_depth_report', 'N/A')}
                """
                return data, memory_context
        except Exception as e:
            st.error(f"Veri okuma hatası: {e}")
    
    return {}, "Veri bulunamadı. Lütfen scout.py'yi çalıştır."

# --- 3. ORACLE 3.1 PRO MOTORU ---
def oracle_engine(prompt, memory_context):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "⚠️ Hata: API anahtarı bulunamadı."
    
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    
    system_instr = f"""
    Sen THE ORACLE v5.1 (3.1 Pro) stratejistisin. Bugün {datetime.now().strftime('%d %B %Y')}.
    Hafızandaki eski verileri unut. Sadece sana sunulan JSON verisine sadık kal.
    Taktiksel, ciddi ve 'Thought Partner' tonunda konuş.
    
    VERİ: {memory_context}
    """
    
    # Not: Studio'da 3.1 Pro erişimin yoksa "gemini-2.0-flash" kullanabilirsin.
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        temperature=0.2,
        model="gemini-3.1-pro" 
    )
    
    try:
        res = client.models.generate_content(model="gemini-3.1-pro", contents=[prompt], config=config)
        return res.text
    except Exception as e:
        return f"Oracle Zihin Hatası: {str(e)}"

# --- 4. ANA SAYFA DASHBOARD ---
def show_home():
    hub_data, memory_context = load_oracle_memory()
    
    # Üst Panel: Gelecek Maç Bilgisi
    next_battle = hub_data.get('next_battle', {})
    st.markdown(f"""
    <div class="assistant-panel">
        <span style="color: #888; font-size: 12px; letter-spacing: 2px;">GELECEK MAÇ ANALİZİ</span><br>
        <b style="font-size: 28px; color: #00ff9d;">{next_battle.get('match', 'Veri Çekiliyor...')}</b><br>
        <span style="font-size: 16px; color: #bbb;">{next_battle.get('kick_off', 'N/A')} • {next_battle.get('weather', 'N/A')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Orta Panel: Modül Kısayolları (Görünürlük için Button Grubu)
    st.write("### 🛠️ Stratejik Modüller")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧬 Scout DNA", use_container_width=True): st.info("Yan menüden 'Scout DNA' sayfasına geçiniz.")
    with c2:
        if st.button("📊 Match Center", use_container_width=True): st.info("Yan menüden 'Match Center' sayfasına geçiniz.")
    with c3:
        if st.button("📋 Taktik Tahta", use_container_width=True): st.info("Yan menüden 'Taktik Tahta' sayfasına geçiniz.")

    st.markdown("---")

    # Chat Sistemi
    if 'messages' not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Hocam, taktiksel bir soru sor..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle 3.1 Pro analiz ediyor..."):
                ans = oracle_engine(prompt, memory_context)
                st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# --- 5. ÇALIŞTIR ---
show_home()
