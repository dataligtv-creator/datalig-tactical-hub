import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="DATALIG Mastermind OS", page_icon="🧬", layout="wide")

# --- 2. SESSION STATE (BELLEK) ---
if 'tactic_context' not in st.session_state:
    st.session_state.tactic_context = {
        "focus_team": "Seçilmedi",
        "formation": "4-3-3",
        "game_phase": "SET HÜCUMU",
        "scouting_report": "Stratejik merkez hazır.",
        "dna_summary": "Analiz için takım seçin.", # Sol panel için kısa başlıklar
        "messages": [] 
    }

# --- 3. ANALİZ MOTORU (GEMINI 2.5 FLASH) ---
# --- ANALİZ MOTORU GÜNCELLEMESİ (Hatasız Özetleme Modu) ---
def get_mastermind_analysis(query, mode="TACTIC"):
    MODEL_ID = "gemini-2.5-flash"
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    if mode == "DNA":
        sys_instruction = (
            "Sen Domenico Tedesco ve Luis Enrique'sin. Rakibi deşifre et. "
            "ÖNEMLİ: Yanıtının en başına tam olarak '### OZET START ###' yaz ve altına rakibin en zayıf 5 noktasını madde madde ekle. "
            "Ardından '### OZET END ###' yaz ve detaylı analize geç."
        )
    else:
        sys_instruction = "Sen Pep, Mourinho ve Klopp'un birleşimi bir taktik dehasısın."

    config = types.GenerateContentConfig(tools=[search_tool], system_instruction=sys_instruction)
    response = client.models.generate_content(model=MODEL_ID, contents=[query], config=config)
    return response.text

# --- SIDEBAR BUTON GÜNCELLEMESİ ---
if selected_team:
    st.session_state.tactic_context['focus_team'] = selected_team
    if st.button("🔬 RAKİBİ DEŞİFRE ET", use_container_width=True):
        with st.spinner(f"🧬 {selected_team} DNA'sı çözülüyor..."):
            full_response = get_mastermind_analysis(f"{selected_team} takımını deşifre et.", mode="DNA")
            
            # --- Akıllı Parçalama Mantığı ---
            if "### OZET START ###" in full_response:
                try:
                    # Özeti çek
                    summary_part = full_response.split("### OZET START ###")[1].split("### OZET END ###")[0]
                    # Detaylı analizi temizle (başlıkları çıkararak chat'e yolla)
                    detailed_part = full_response.replace("### OZET START ###", "").replace("### OZET END ###", "").replace(summary_part, "")
                    
                    st.session_state.tactic_context['dna_summary'] = summary_part.strip()
                    st.session_state.tactic_context['messages'].append({
                        "role": "assistant", 
                        "content": f"🧬 **{selected_team.upper()} DETAYLI DNA ANALİZİ**\n\n{detailed_part.strip()}"
                    })
                except:
                    st.session_state.tactic_context['dna_summary'] = "Özet ayrıştırılamadı, detaylar chat'te."
            else:
                st.session_state.tactic_context['dna_summary'] = "Analiz tamamlandı. Detaylar aşağıda."
                st.session_state.tactic_context['messages'].append({"role": "assistant", "content": full_response})
            
            st.rerun()

# --- 4. 🏟️ UI MOTORU ---
def render_dashboard(context):
    report = context['scouting_report'].replace("\n", "<br>").replace('"', "'")
    dna_indices = context['dna_summary'].replace("\n", "<br>").replace('"', "'")
    form = context['formation']
    team = context['focus_team']

    # Piyon Yerleşimi
    pos_db = {
        "4-3-3": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (55, 30, "8"), (60, 50, "6"), (55, 70, "10"), (30, 20, "7"), (25, 50, "9"), (30, 80, "11")],
        "4-2-3-1": [(93, 50, "1"), (80, 15, "3"), (82, 38, "4"), (82, 62, "5"), (80, 85, "2"), (65, 40, "6"), (65, 60, "8"), (45, 20, "7"), (42, 50, "10"), (45, 80, "11"), (25, 50, "9")]
    }
    players_html = "".join([f"<div style='position:absolute; top:{t}%; left:{l}%; transform:translate(-50%,-50%); z-index:20;'><div style='width:22px; height:22px; border-radius:50%; background:white; border:2px solid #13c8ec; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:bold; color:black;'>{num}</div></div>" for t, l, num in pos_db.get(form, pos_db["4-3-3"])])

    html_code = f"""
    <body style="background:#0b1011; color:white; font-family:sans-serif; margin:0;">
        <div style="display:grid; grid-template-columns: 1fr 2fr 1fr; gap:15px; padding:10px;">
            <div style="background:#111718; border:1px solid #283639; border-radius:8px; padding:12px; height:500px; border-left:4px solid #facc15;">
                <h3 style="color:#facc15; font-size:10px; font-weight:bold; letter-spacing:1px; margin-bottom:10px;">🧬 DNA ÖZETİ & ZAYIF NOKTALAR</h3>
                <div style="font-size:11px; color:#fbbf24; line-height:1.6; font-family:monospace;">{dna_indices}</div>
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
                <h3 style="font-size:10px; color:#94a3b8; text-transform:uppercase;">Aktif Odak</h3>
                <div style="font-size:16px; font-weight:bold;">{team}</div>
                <div style="margin-top:20px; font-size:10px; color:#94a3b8; text-transform:uppercase;">Formasyon</div>
                <div style="font-size:16px; font-weight:bold; color:#13c8ec;">{form}</div>
            </div>
        </div>
    </body>
    """
    return components.html(html_code, height=550)

# --- 5. SIDEBAR ---
ALL_TEAMS = ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Real Madrid", "Man City", "Arsenal", "Barcelona"]

with st.sidebar:
    st.title("🧠 MASTERMIND OS")
    selected_team = st.selectbox("🎯 TAKIM ODAĞI", options=ALL_TEAMS, index=None, placeholder="Takım Seçiniz...")
    
    if selected_team:
        st.session_state.tactic_context['focus_team'] = selected_team
        if st.button("🔬 RAKİBİ DEŞİFRE ET", use_container_width=True):
            with st.spinner("DNA Analizi yapılıyor..."):
                full_dna = get_mastermind_analysis(f"{selected_team} takımını deşifre et.", mode="DNA")
                
                # Özet ve Detayı Ayırıyoruz
                if "ÖZET BAŞLIKLAR:" in full_dna:
                    parts = full_dna.split("ÖZET BAŞLIKLAR:")
                    detail = parts[0] if parts[0] else parts[1]
                    summary = parts[1].split("\n\n")[0] if len(parts)>1 else "Analiz tamamlandı."
                else:
                    summary = "Detaylar chat ekranına aktarıldı."
                    detail = full_dna

                st.session_state.tactic_context['dna_summary'] = summary
                st.session_state.tactic_context['messages'].append({"role": "assistant", "content": f"🧬 **{selected_team.upper()} DNA DEŞİFRESİ:**\n\n{full_dna}"})
                st.rerun()

# --- 6. RENDER & CHAT ---
render_dashboard(st.session_state.tactic_context)

st.markdown("---")
# Sohbet Geçmişi (Sadece son 3 mesaj)
for msg in st.session_state.tactic_context['messages'][-3:]:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Mastermind'a direktif ver..."):
    st.session_state.tactic_context['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        ans = get_mastermind_analysis(prompt)
        st.markdown(ans)
        st.session_state.tactic_context['messages'].append({"role": "assistant", "content": ans})
        st.rerun()
