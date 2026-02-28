import os
import json
import re
from datetime import datetime
from google import genai
from google.genai import types

def run_oracle_scout():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    today = datetime.now().strftime("%d %B %Y")

    # --- AŞAMA 1: 3 FLASH (VERİ AVCISI) ---
    print("📡 Aşama 1: 3 Flash interneti tarıyor...")
    search_res = client.models.generate_content(
        model="gemini-3-flash", 
        contents=[f"Fenerbahçe 2026 kadro güncellemeleri, Ocak transferleri ve sıradaki maç detayları."],
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
    )
    raw_web_data = search_res.text

    # --- AŞAMA 2: 2.5 FLASH (FİLTRE VE DÜZENLEYİCİ) ---
    # 2.5 Flash, 3.1 Pro'ya gitmeden önce veriyi tertemiz bir JSON yapar.
    print("🧹 Aşama 2: 2.5 Flash veriyi rafine ediyor...")
    filter_prompt = f"Şu verideki gereksizleri at, sadece kadro değişimlerini ve maç verisini JSON yap: {raw_web_data}"
    filter_res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[filter_prompt],
        config=types.GenerateContentConfig(temperature=0.0)
    )
    
    # --- AŞAMA 3: 3.1 PRO (STRATEJİK ANALİZÖR - "THE ORACLE") ---
    # İşte 3.1'i burada, en yüksek IQ gerektiren noktada devreye sokuyoruz.
    print("🧠 Aşama 3: 3.1 Pro (The Oracle) strateji geliştiriyor...")
    
    clean_data = filter_res.text
    final_oracle_prompt = f"""
    Sen 'The Oracle' 3.1 Pro modelisin. Aşağıdaki rafine edilmiş veriyi kullanarak:
    1. Kadrodan giden oyuncuları (Kostic vb.) hafızandan SİL.
    2. Yeni gelen oyuncuların taktiksel uyumunu analiz et.
    3. Hoca (Kullanıcı) için derin bir 'Maç Önü Analizi' ve 'Risk Raporu' hazırla.

    Veri: {clean_data}
    """

    oracle_res = client.models.generate_content(
        model="gemini-3.1-pro", # En yüksek kapasiteli model
        contents=[final_oracle_prompt],
        config=types.GenerateContentConfig(temperature=0.4) # Taktiksel yaratıcılık için 0.4
    )

    # Nihai analiz raporunu kaydet
    try:
        with open("hub_data.json", "w", encoding="utf-8") as f:
            json.dump({"report": oracle_res.text, "sync": today}, f, ensure_ascii=False)
        print("🎯 MÜKEMMEL: 3.1 Pro stratejiyi belirledi ve hub_data.json güncellendi.")
    except Exception as e:
        print(f"⚠️ HATA: {e}")

if __name__ == "__main__":
    run_oracle_scout()
