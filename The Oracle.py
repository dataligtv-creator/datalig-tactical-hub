import streamlit as st
import google.generativeai as genai
from pinecone import Pinecone
# HuggingFace Embeddings (Colab ile uyumlu motor)
from langchain_community.embeddings import HuggingFaceEmbeddings
import time

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="DATALIG Pro Suite",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 DATALIG TASARIM SİSTEMİ (CSS) ---
# Senin gönderdiğin HTML dosyalarındaki renkleri ve fontları buraya işledik.
st.markdown("""
<style>
    /* 1. FONT YÜKLEME (Inter & JetBrains Mono) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* 2. TEMEL RENKLER VE DESENLER */
    :root {
        --primary-color: #00e5ff; /* Neon Cyan */
        --bg-color: #0b0f19;      /* Deep Charcoal */
        --surface-color: rgba(15, 23, 42, 0.6); /* Glass Surface */
        --border-color: rgba(255, 255, 255, 0.1);
    }

    /* 3. ANA GÖVDE (Grid Deseni Ekledik) */
    .stApp {
        background-color: var(--bg-color);
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        font-family: 'Inter', sans-serif;
    }

    /* 4. BAŞLIKLAR */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: white !important;
        letter-spacing: -0.02em;
    }
    
    /* 5. KOD VE VERİ ALANLARI (Monospace Font) */
    code, .stCodeBlock, .stMetricValue {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* 6. YAN MENÜ (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid var(--border-color);
    }

    /* 7. SOHBET KUTUSU (Neon Efektli) */
    .stTextInput input {
        background-color: #0f172a !important;
        border: 1px solid var(--border-color) !important;
        color: white !important;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.15) !important;
    }

    /* 8. BUTONLAR (DATALIG Tarzı) */
    .stButton button {
        background-color: rgba(0, 229, 255, 0.05);
        color: var(--primary-color);
        border: 1px solid rgba(0, 229, 255, 0.2);
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stButton button:hover {
        background-color: var(--primary-color);
        color: #0b0f19;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        border-color: var(--primary-color);
    }

    /* 9. MESAJ BALONLARI (Glassmorphism) */
    [data-testid="stChatMessage"] {
        background-color: rgba(15, 23, 42, 0.4);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Asistan İkonu */
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #1e293b !important;
        color: var(--primary-color) !important;
        border: 1px solid rgba(0, 229, 255, 0.2);
    }
    
    /* Kullanıcı İkonu */
    [data-testid="chatAvatarIcon-user"] {
        background-color: var(--primary-color) !important;
        color: #0b0f19 !important;
    }

    /* 10. Linkler */
    a {
        color: var(--primary-color) !important;
        text-decoration: none;
    }
    a:hover {
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK VE LOGO ALANI ---
col1, col2 = st.columns([1, 12])
with col1:
    # Logo benzeri bir yapı
    st.markdown("""
    <div style="
        width: 50px; height: 50px; 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
        border-radius: 8px; 
        display: flex; align-items: center; justify-content: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 0 15px rgba(0,0,0,0.5);">
        <span style="color: #00e5ff; font-weight: bold; font-family: 'JetBrains Mono'; font-size: 24px;">D</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="display: flex; flex-direction: column;">
        <h1 style="margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 0.05em;">DATALIG <span style="font-weight: 300; opacity: 0.5;">PRO SUITE</span></h1>
        <span style="font-family: 'JetBrains Mono'; font-size: 12px; color: #00e5ff; letter-spacing: 0.2em; opacity: 0.8;">TACTICAL INTELLIGENCE HUB v2.5</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- API VE MOTOR KURULUMLARI ---
if "GOOGLE_API_KEY" in st.secrets and "PINECONE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    try:
        pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
        index_name = "regista-arsiv"
        pinecone_index = pc.Index(index_name)
        
        # Colab ile uyumlu HuggingFace Motoru
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        db_status = "ONLINE"
        db_color = "#00e5ff" # Neon Cyan
        status_icon = "🟢"
    except Exception as e:
        pinecone_index = None
        db_status = "OFFLINE"
        db_color = "#ef4444" # Red
        status_icon = "🔴"
else:
    st.error("🚨 API KEY EKSİK! Lütfen secrets ayarlarını kontrol et.")
    st.stop()

# --- YAN MENÜ TASARIMI ---
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 10px; background: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.1); border-radius: 8px; margin-bottom: 20px;">
        <div style="font-family: 'JetBrains Mono'; font-size: 12px; color: #94a3b8;">SYSTEM STATUS</div>
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
            <div style="width: 8px; height: 8px; background-color: {db_color}; border-radius: 50%; box-shadow: 0 0 10px {db_color};"></div>
            <div style="font-weight: bold; color: white;">{db_status}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🛠️ KONTROL PANELİ")
    st.info("Model: **Gemini 2.5 Flash**")
    st.info("Motor: **HuggingFace**")
    
    st.markdown("---")
    st.markdown("""
    <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #64748b;">
        SHORTCUTS:<br>
        > "Klopp 4-3-3"<br>
        > "City Build-up"<br>
        > "Gegenpressing"
    </div>
    """, unsafe_allow_html=True)

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem hazır hocam. Maç verileri ve taktik kütüphanesi emrine amade. Nereden başlayalım?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FONKSİYONLAR ---
def arsivden_bul(soru):
    if not pinecone_index: return None, []
    try:
        soru_vektor = embeddings.embed_query(soru)
        sonuc = pinecone_index.query(vector=soru_vektor, top_k=4, include_metadata=True)
        metinler = ""
        kaynaklar = []
        for match in sonuc['matches']:
            if 'text' in match['metadata']:
                metinler += match['metadata']['text'] + "\n\n"
                kaynaklar.append(match['metadata'].get('source', 'Unknown'))
        return metinler, list(set(kaynaklar))
    except: return None, []

# --- SOHBET GİRİŞİ ---
if prompt := st.chat_input("Taktiksel analiz veya oyuncu sorgusu yap..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Animasyonlu Bekleme (Neon Efektli)
        with st.status("⚡ VERİ İŞLENİYOR...", expanded=True) as status:
            st.write("Vektör veritabanı taranıyor...")
            context, kaynaklar = arsivden_bul(prompt)
            st.write("Taktiksel desenler eşleştiriliyor...")
            time.sleep(0.3)
            status.update(label="ANALİZ TAMAMLANDI", state="complete", expanded=False)
        
        prompt_taslagi = """
        Sen 'DATALIG AI' adında profesyonel bir futbol analistisin.
        Aşağıdaki arşiv verilerini kullanarak teknik direktör seviyesinde cevap ver.
        
        SORU: {soru}
        ARŞİV: {bilgi}
        
        Kurallar:
        1. Verilere dayalı konuş.
        2. Taktiksel terimleri doğru kullan (Half-space, Rest Defense vb.)
        3. Cevabı yapılandır (Maddeler, Başlıklar).
        """
        
        final_prompt = prompt_taslagi.format(soru=prompt, bilgi=context if context else "(Veri yok)")
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(final_prompt)
            ai_response = response.text
            
            # Kaynakları Şık Gösterme
            if kaynaklar:
                ai_response += "\n\n<div style='background: rgba(0, 229, 255, 0.05); padding: 10px; border-radius: 8px; border: 1px solid rgba(0, 229, 255, 0.1); margin-top: 15px;'>"
                ai_response += "<div style='font-family: JetBrains Mono; font-size: 12px; color: #00e5ff; margin-bottom: 5px;'>📚 REFERANS DOSYALAR</div>"
                for k in kaynaklar:
                    ai_response += f"<div style='font-size: 12px; color: #94a3b8;'>📄 {k}</div>"
                ai_response += "</div>"
            
            message_placeholder.markdown(ai_response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
