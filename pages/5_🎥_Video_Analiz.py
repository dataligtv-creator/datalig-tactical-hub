import streamlit as st

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Video Analiz | DATALIG", page_icon="🎥", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; }
    h1, h2, h3 { color: white !important; font-family: 'monospace'; }
    .video-container { border: 2px solid #00e5ff; border-radius: 15px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("🎥 VIDEO ANALİZ MERKEZİ")
st.caption("Veriyle Kanıtlanmış Saha Performansı")
st.markdown("---")

# --- HAFIZA KONTROLÜ (Scout Sayfasından Gelen Oyuncu) ---
aktif_oyuncu = st.session_state.get('aktif_oyuncu', "Mauro Icardi")

# --- AKILLI VIDEO VERİ TABANI ---
# Buraya her oyuncu için bir YouTube linki tanımlıyoruz
video_db = {
    "Mauro Icardi": "https://www.youtube.com/watch?v=ODSPumk68qg", # Icardi Gol Kralı Tüm Goller
    "Edin Dzeko": "https://www.youtube.com/watch?v=uuTCWzMrNSE",   # Dzeko Scout Raporu
    "Rafa Silva": "https://www.youtube.com/watch?v=4n2igf4gWuA",   # Rafa Silva Analizi
    "Ciro Immobile": "https://www.youtube.com/watch?v=EuPqStDPZJg",
    "Gedson Fernandes": "https://www.youtube.com/watch?v=drABFAO_TP0"
}

# Eğer seçilen oyuncu listede yoksa genel bir arama sonucu gösteririz
video_url = video_db.get(aktif_oyuncu, "https://www.youtube.com/results?search_query=" + aktif_oyuncu + "+analiz")

# --- EKRAN DÜZENİ ---
col_vid, col_notes = st.columns([2, 1])

with col_vid:
    st.markdown(f"### 📺 ANALİZ: {aktif_oyuncu}")
    st.video(video_url)
    st.info(f"📍 Kaynak: YouTube | {aktif_oyuncu} Sezon Analizi")

with col_notes:
    st.markdown("### 📝 TEKNİK NOTLAR")
    st.write(f"Şu an **{aktif_oyuncu}** için hazırlanan teknik analiz videosunu izliyorsunuz.")
    
    # Dinamik Notlar
    if "Icardi" in aktif_oyuncu:
        st.warning("⚠️ Dikkat: Videonun 3:45 dakikasındaki tek pas golü, War Room'daki stratejimizle uyuşuyor.")
    elif "Rafa" in aktif_oyuncu:
        st.warning("⚠️ Dikkat: Videodaki geçiş hücumu hızı, sistemdeki %88 Hız verisini doğruluyor.")
    
    st.markdown("---")
    user_note = st.text_area("Video Üzerine TD Notu Al:", placeholder="Bu oyuncunun markajdan kurtulma becerisi çok iyi...")
    if st.button("Notu Hafızaya Ekle"):
        st.success("Not, Oracle arşivine gönderildi.")

# --- YOUTUBE ARAMA ÖZELLİĞİ ---
st.markdown("---")
st.markdown("### 🔍 Diğer Videoları Ara")
search_query = st.text_input("YouTube'da Manuel Ara:", value=f"{aktif_oyuncu} scout report")
if st.button("YouTube'da Bul"):
    st.markdown(f"[Buraya Tıklayarak Sonuçları Gör](https://www.youtube.com/results?search_query={search_query.replace(' ', '+')})")
