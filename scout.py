import os
import json
from datetime import datetime
from google import genai
from google.genai import types

def run_morning_scout():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("CRITICAL ERROR: GOOGLE_API_KEY is not set.")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-flash-preview"

    # 1. STRATEJİK SORGU: SADECE GELECEK MAÇ VE ANALİTİK VERİ
    scout_prompt = """
    Bugün 15 Ocak 2026. Fenerbahçe'nin (Tedesco dönemi) sıradaki resmi maçını bul.
    SADECE aşağıdaki JSON formatında, hiçbir ek açıklama yapmadan yanıt ver:
    {
        "next_match": "Ev Sahibi - Deplasman",
        "match_date": "Gün Ay Yıl Saat",
        "match_date_iso": "YYYY-MM-DDTHH:MM:SS",
        "weather": "Derece ve Hava Durumu",
        "expert_notes": "Taktik Mania veya benzeri kaynaklardan 1 cümlelik analiz",
        "xg_data": {"Ev": 1.5, "Dep": 1.2}
    }
    """

    print("Scout is analyzing fixtures...")

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[scout_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.1
            )
        )

        # JSON temizleme
        raw_text = response.text
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        final_data = json.loads(clean_json)
        
        # Güncelleme zamanını mühürle
        final_data["last_update"] = datetime.now().strftime("%d %B %Y %H:%M")

        # 2. DOSYAYA MÜHÜRLE (Cache)
        with open("hub_data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"SUCCESS: {final_data['next_match']} verileri mühürlendi.")

    except Exception as e:
        print(f"SCOUT ERROR: {str(e)}")

if __name__ == "__main__":
    # Önce mevcut dosyayı kontrol et
    if os.path.exists("hub_data.json"):
        with open("hub_data.json", "r") as f:
            current_data = json.load(f)
        
        # Maç tarihi kontrolü (ISO Formatı sayesinde kolay karşılaştırma)
        try:
            match_time = datetime.fromisoformat(current_data.get("match_date_iso"))
            if datetime.now() < match_time:
                print("Oracle Bildirisi: Mevcut maç henüz oynanmadı. Veri çekme işlemi pas geçildi.")
                # Sadece hava durumunu tazelemek istersen buraya bir fonksiyon ekleyebiliriz.
                exit() # İşlemi durdur, kota harcama
        except:
            pass # Eğer tarih formatı bozuksa yeniden çek

    run_morning_scout()
