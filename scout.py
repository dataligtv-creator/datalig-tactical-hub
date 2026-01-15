import os
import json
from datetime import datetime
from google import genai
from google.genai import types

def run_morning_scout():
    # 1. GitHub Secrets üzerinden API Key kontrolü
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("CRITICAL ERROR: GOOGLE_API_KEY is not set in environment variables.")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-flash-preview"

    # 2. Oracle Scout Sorgusu (2026 Gerçekliği)
    # Bu sorgu Google Search tool'u kullanarak en taze bilgiyi çeker
    scout_prompt = """
    Bugün 15 Ocak 2026. Fenerbahçe'nin (Teknik Direktör: Domenico Tedesco) bir sonraki maçını araştır.
    Aşağıdaki bilgileri JSON formatında getir:
    1. next_match: (Rakip Takım ismi)
    2. match_date: (Maç tarihi ve saati)
    3. weather: (Maçın oynanacağı şehirdeki tahmini hava durumu)
    4. expert_notes: (Süper Lig analistlerinin ve Taktik Mania gibi kaynakların bu maç hakkındaki 1 cümlelik kritik uyarısı)
    5. xg_data: (Takımların son maçlardaki xG ortalamaları)
    """

    print("Scout bot is searching for global and local tactical data...")

    try:
        # Google Search Tool'u aktif ederek sorgu atıyoruz
        response = client.models.generate_content(
            model=model_id,
            contents=[scout_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2
            )
        )

        # Gelen yanıtın içinden JSON verisini ayıklama (Basit temizlik)
        raw_text = response.text
        # Markdown kod bloklarını temizle
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        
        # 3. Veriyi Doğrula ve JSON'a Çevir
        final_data = json.loads(clean_json)
        final_data["last_update"] = datetime.now().strftime("%d %B %Y %H:%M")

        # 4. Hub Dosyasını Güncelle
        with open("hub_data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"SUCCESS: hub_data.json updated for {final_data['next_match']}.")

    except Exception as e:
        print(f"SCOUT ERROR: {str(e)}")
        # Hata durumunda sistemin çökmemesi için yedek bir dosya oluşturabiliriz
        fallback = {
            "last_update": datetime.now().strftime("%d %B %Y %H:%M"),
            "next_match": "Veri Çekilemedi",
            "match_date": "N/A",
            "weather": "N/A",
            "expert_notes": f"Hata oluştu: {str(e)}"
        }
        with open("hub_data.json", "w", encoding="utf-8") as f:
            json.dump(fallback, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_morning_scout()
