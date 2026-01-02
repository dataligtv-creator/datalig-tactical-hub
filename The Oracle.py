import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import time

# --- 1. SAYFA KONFİGÜRASYONU ---
st.set_page_config(page_title="DATALIG Mastermind OS", page_icon="🧠", layout="wide")

# --- 2. SESSION STATE (BELLEK) ---
# Hataları önlemek için tüm değişkenleri burada başlatıyoruz
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Seçilmedi",
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "scouting_report": "Sistem aktif. Mastermind hazır.",
        "dna_summary": "Analiz için takım seçin.",
        "messages": [] 
    }

# --- 3. ANALİZ MOTORU (GEMINI 2.5 FLASH - GERÇEKLİK AYARLI) ---
def get_mastermind_analysis(query, mode="TACTIC"):
    MODEL_ID = "gemini-2.5-flash"
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    current_date = "2 Ocak 2026"
    
    # Fenerbahçe 3'lü oynamıyor uyarısını buraya mühürledik
    fact_check = (
        "ÖNEMLİ BİLGİ: 2026 itibarıyla Fenerbahçe ana plan olarak 4-2-3-1 oynamaktadır. "
        "Eski 3'lü savunma verilerini hata olarak kabul et ve analizlerini güncel 4'lü savunma üzerine kur."
    )
    
    if mode == "DNA":
        sys_instruction = (
            f"Sen Domenico Tedesco'sun. {fact_check} Rakibi deşifre et. "
            "Yanıtının en başına '### OZET START ###' yaz ve altına rakibin en zayıf 5 noktasını madde madde ekle. "
            "Ardından '### OZET END ###' yaz ve detaylı analize geç."
        )
    else:
        sys_instruction = f"Sen efsanevi hocaların hibrit zekasısın. {fact_check} Tarih: {current_date}."

    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=sys_instruction)
    response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
    return response.text

# --- 4. 🏟️ UI MOTORU ---
def render_dashboard(context):
    # Değişkenlerin boş gelme ihtimaline karşı koruma
    report = context.get('scouting_report', "").replace("\n", "<br>").replace('"', "'")
    dna_indices = context.get('dna_summary', "").replace("\n", "<br>").replace('"', "'")
    form = context.get('formation', "4-3-3")
    team = context.get('focus_team', "Seçilmedi")

    # Diziliş Veritabanı
    pos_db = {
        "4-3-3": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (55, 30, "8"), (60, 50, "6"), (55, 70, "10"), (30, 20, "7"), (25, 50, "9"), (30, 80, "11")],
        "4-2-3-1": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (65, 40, "6"), (65, 60, "8"), (45, 20, "7"), (42, 50, "10"), (45, 80, "11"), (25, 50, "9")]
    }
    
    players_html = "".join([f"<div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:20;'><div style='width:22px; height:22px; border-radius:50%; background:white; border:2px solid #13c8ec; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:bold; color:black;'>{num}</div></div>" for t, l, num in pos_db.get(form, pos_db["4-3-3"])])

    html_code = f"""
    <div style="background:#0b1011; color:white; font-family:sans-serif; padding:10px; display:grid; grid-template-columns: 1fr 2fr 1fr; gap:15px;">
        <div style="background:#111718; border:1px solid #283639; border-radius:8px; padding:12px; height:500px; border-left:4px solid #facc15; overflow-y:auto;">
            <h3 style="color:#facc15; font-size:10px; font-weight:bold; text-transform:uppercase;">🧬 DNA ÖZETİ (ZAYIF NOKTALAR)</h3>
            <div style="font-size:11px; color:#fbbf24; margin-top:10px; line-height:1.6;">{dna_indices}</div>
        </div>
        <div style="background:#0f1516; border-radius:15px; border:1px solid #283639; position:relative; overflow:hidden; display:flex; justify-content:center; align-items:center;">
            <div style="width:350px; height:480px; background:#173828; border:2px solid rgba(255,255,255,0.2); position:relative; border-radius:10px; background-image:repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(255,255,255,0.02) 40px, rgba(255,255,255,0.02) 80px);">
                <div style="position:absolute; inset:10px; border:1px solid rgba(255,255,255,0.2);">
                    <div style="position:absolute; top:50%; left:0; right:0; height:1px; background:rgba(255,255,255,0.2);"></div>
                </div>
                {players_html}
            </div>
        </div>
        <div style="background:#111718; border:1px solid #283639; border-radius:8px; padding:12px;">
            <p style="font-size:10px; color:#94a3b8; text-transform:uppercase;">Aktif Takım</p>
            <p style="font-size:18px; font-weight:bold;">{team}</p>
            <p style="font-size:10px; color:#94a3b8; text-transform:uppercase; margin-top:20px;">Diziliş</p>
            <p style="font-size:18px; font-weight:bold; color:#13c8ec;">{form}</p>
        </div>
    </div>
    """
    return components.html(html_code, height=550)

# --- 5. SIDEBAR ---
ALL_TEAMS = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Real Madrid", "Man City", "Arsenal", "Barcelona", "Liverpool", "Bayer Leverkusen"]

with st.sidebar:
    st.title("🧠 MASTERMIND OS")
    # Değişkeni sidebar içinde tanımlayıp anında context'e yazıyoruz
    st.session_state.tactic_context['focus_team'] = st.selectbox(
        "🎯 TAKIM ODAĞI", 
        options=ALL_TEAMS, 
        index=None, 
        placeholder="Takım Seçiniz..."
    ) or "Seçilmedi"
    
    selected_team = st.session_state.tactic_context['focus_team']
    
    if selected_team != "Seçilmedi":
        if st.button("🔬 RAKİBİ DEŞİFRE ET", use_container_width=True):
            with st.spinner("🧬 DNA Analizi yapılıyor..."):
                full_dna = get_mastermind_analysis(f"{selected_team} takımını deşifre et.", mode="DNA")
                
                if "### OZET START ###" in full_dna:
                    summary = full_dna.split("### OZET START ###")[1].split("### OZET END ###")[0]
                    detail = full_dna.replace("### OZET START ###", "").replace("### OZET END ###", "").replace(summary, "")
                    st.session_state.tactic_context['dna_summary'] = summary.strip()
                    st.session_state.tactic_context['messages'].append({"role": "assistant", "content": f"🧬 **{selected_team.upper()} DNA DEŞİFRESİ:**\n\n{detail.strip()}"})
                else:
                    st.session_state.tactic_context['dna_summary'] = "Analiz chat ekranında."
                    st.session_state.tactic_context['messages'].append({"role": "assistant", "content": full_dna})
                st.rerun()

# --- 6. RENDER & CHAT ---
render_dashboard(st.session_state.tactic_context)

st.markdown("---")
for msg in st.session_state.tactic_context['messages'][-3:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Mastermind'a direktif ver..."):
    st.session_state.tactic_context['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        ans = get_mastermind_analysis(prompt)
        st.markdown(ans)
        st.session_state.tactic_context['messages'].append({"role": "assistant", "content": ans})
        
        # Diziliş güncelleme mantığı
        if "4-2-3-1" in ans: st.session_state.tactic_context['formation'] = "4-2-3-1"
        elif "4-3-3" in ans: st.session_state.tactic_context['formation'] = "4-3-3"
        st.rerun()
