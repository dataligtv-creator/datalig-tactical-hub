import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import google.generativeai as genai  # <--- YENİ EKLENDİ

st.set_page_config(page_title="Regista Hub", layout="wide")
st.title("⚽ Regista Tactical Hub")

# --- 1. BAĞLANTI & AYARLAR ---
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        if "FIREBASE_KEY" in st.secrets:
            try:
                key_content = st.secrets["FIREBASE_KEY"]
                if key_content.startswith("'") and key_content.endswith("'"):
                     key_content = key_content[1:-1]
                key_dict = json.loads(key_content)
                cred = credentials.Certificate(key_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                st.error(f"❌ Firebase Hatası: {e}")
                st.stop()
        else:
            st.error("🚨 HATA: Firebase anahtarı yok.")
            st.stop()
    return firestore.client()

db = get_db()

# --- GEMINI AI AYARLARI (YENİ) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Yapay Zeka Kişiliği: Futbol Analisti
    model = genai.GenerativeModel('gemini-1.5-flash', 
        system_instruction="Sen 'Regista AI' adında, Klopp ve Guardiola karışımı zeki bir futbol analistisin. Kullanıcının sorularına taktiksel, veri odaklı ve kısa cevaplar ver. Asla futbol dışı konulara girme.")
else:
    st.warning("⚠️ Yapay Zeka için API Key girilmemiş.")

# --- KENAR ÇUBUĞU ---
st.sidebar.header("⚙️ Analiz Ayarları")
selected_team = st.sidebar.selectbox("Takım Seçiniz", ["Argentina", "France"])
match_id = 3869685

try:
    players_ref = db.collection("players").where("team", "==", selected_team).stream()
    player_list = sorted([doc.to_dict()["name"] for doc in players_ref])
except:
    player_list = []
filter_options = ["Tüm Takım"] + player_list

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Oyuncu Filtresi")
selected_player = st.sidebar.selectbox("Oyuncu Seçiniz", filter_options)

# --- SEKMELER (TAB) - ARTIK 5 TANE ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Kadro", "🕸️ Pas Ağı", "🔥 Isı Haritası", "🥅 Şut Haritası", "💬 AI Analist"])

# ... (TAB 1, 2, 3, 4 KODLARI AYNEN KALIYOR - KISALTTIM YER KAPLAMASIN) ...
with tab1:
    st.subheader(f"{selected_team} Kadrosu")
    try:
        players_ref = db.collection("players").where("team", "==", selected_team).stream()
        data = [doc.to_dict() for doc in players_ref]
        if data: st.dataframe(pd.DataFrame(data)[["name", "number", "position"]], use_container_width=True)
    except: st.warning("Veri yok.")

with tab2:
    st.subheader(f"🔗 {selected_team} Pas Trafiği")
    try:
        doc = db.collection("analytics").document(f"pass_network_{selected_team}_{match_id}").get()
        if doc.exists:
            data = doc.to_dict()
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
            fig, ax = pitch.draw(figsize=(16, 11))
            fig.set_facecolor("#22312b")
            links, locations = data.get("links", {}), data.get("locations", {})
            for key, count in links.items():
                if count > 2:
                    p, r = key.split(" -> ")
                    if p in locations and r in locations:
                        pitch.arrows(locations[p][0], locations[p][1], locations[r][0], locations[r][1], width=count/5, color="white", alpha=0.5, ax=ax)
            for n, l in locations.items():
                pitch.scatter(l[0], l[1], s=300, color='#1ea8bd', edgecolors='white', ax=ax)
                pitch.annotate(n, (l[0], l[1]-3), ax=ax, color='white', ha='center', fontsize=9)
            st.pyplot(fig)
    except: st.error("Hata.")

with tab3:
    st.subheader(f"🔥 {selected_team} Isı Haritası")
    try:
        doc = db.collection("analytics").document(f"heatmap_{selected_team}_{match_id}").get()
        if doc.exists:
            df = pd.DataFrame(doc.to_dict().get("events", []))
            if selected_player != "Tüm Takım": df = df[df["player"] == selected_player]
            if not df.empty:
                pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
                fig, ax = pitch.draw(figsize=(16, 11))
                fig.set_facecolor('#22312b')
                sns.kdeplot(x=df['x'], y=df['y'], fill=True, thresh=0.05, alpha=0.8, n_levels=100, cmap='magma', ax=ax)
                st.pyplot(fig)
    except: st.error("Hata.")

with tab4:
    st.subheader(f"🥅 {selected_team} Şut Analizi & xG")
    try:
        doc = db.collection("analytics").document(f"shots_{selected_team}_{match_id}").get()
        if doc.exists:
            df_shots = pd.DataFrame(doc.to_dict().get("shots", []))
            if selected_player != "Tüm Takım": df_shots = df_shots[df_shots["player"] == selected_player]
            if not df_shots.empty:
                pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
                fig, ax = pitch.draw(figsize=(16, 11))
                fig.set_facecolor("#22312b")
                goals = df_shots[df_shots["outcome"] == "Goal"]
                non_goals = df_shots[df_shots["outcome"] != "Goal"]
                pitch.scatter(non_goals.x, non_goals.y, s=non_goals.xg * 700 + 100, edgecolors='#ff4b4b', c='None', hatch='///', marker='o', ax=ax, alpha=0.8, label="Kaçan")
                pitch.scatter(goals.x, goals.y, s=goals.xg * 700 + 100, edgecolors='white', c='#00ff00', marker='*', ax=ax, alpha=1, label="GOL")
                st.pyplot(fig)
                st.dataframe(df_shots[["player", "outcome", "xg"]], use_container_width=True)
    except: st.error("Hata.")

# --- 5. SEKME: AI ANALİST (YENİ! 🤖) ---
with tab5:
    st.subheader("🤖 Regista AI: Taktik Asistanı")
    st.caption("Veri odaklı sorular sorabilirsin. Örn: 'Pas bağlantıları nasıl kurulmalı?'")

    # Sohbet Geçmişini Başlat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Eski mesajları ekrana bas
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Kullanıcıdan Girdi Al
    if prompt := st.chat_input("Taktik sorunu buraya yaz..."):
        # 1. Kullanıcı mesajını göster
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. AI Cevabını Üret
        with st.chat_message("assistant"):
            if "GOOGLE_API_KEY" in st.secrets:
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
            else:
                st.warning("Lütfen Streamlit Secrets kısmına GOOGLE_API_KEY ekleyin.")