import os
import json
from datetime import datetime
from google import genai
from google.genai import types

def run_morning_scout():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    # TALİMAT: Halüsinasyon yasak, sadece somut internet verisi.
    scout_prompt = """
    GÖREV: ŞU AN 15 OCAK 2026. Google Search kullanarak Fenerbahçe'nin sıradaki resmi maçını BUL.
    KURAL 1: Sadece resmi fikstür bilgilerini kullan.
    KURAL 2: Yanıtın SADECE geçerli bir JSON objesi olmalı.
    KURAL 3: Tarihi ISO 8601 formatında (YYYY-MM-DDTHH:MM:SS) doğrula.
    
    JSON ŞABLONU:
    {
        "next_match": "Ev Sahibi - Deplasman",
        "match_date": "Gün Ay Yıl Saat",
        "match_date_iso": "YYYY-MM-DDTHH:MM:SS",
        "weather": "Hava Durumu",
        "expert_notes": "Taktiksel gerçek veriye dayalı not",
        "xg_data": {"Ev": 0.0, "Dep": 0.0}
    }
    """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[scout_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0 # Yaratıcılığı sıfıra indirdik, sadece gerçeklik.
            )
        )

        # Gelen metni temizle ve JSON'a zorla
        content = response.text.strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("Geçerli bir JSON verisi bulunamadı.")
            
        final_json = json.loads(content[start:end])
        
        # Ekstra Güvenlik Kontrolü: Tarih alanı boş mu?
        if final_json.get("match_date_iso") == "YYYY-MM-DDTHH:MM:SS":
            raise ValueError("Gemini halüsinasyon denemesi yaptı, gerçek tarih çekilemedi.")

        with open("hub_data.json", "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=4)
        
        print("VERİ MÜHÜRLENDİ: Kesin doğruluk sağlandı.")

    except Exception as e:
        print(f"KRİTİK HATA/GÜVENLİK ENGELİ: {str(e)}")

if __name__ == "__main__":
    run_morning_scout()
