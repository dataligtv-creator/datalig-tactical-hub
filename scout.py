import os
import json
from datetime import datetime
import locale
from google import genai
from google.genai import types

def run_morning_scout():
    # API Anahtarı Kontrolü
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("HATA: GOOGLE_API_KEY bulunamadı.")
        return

    client = genai.Client(api_key=api_key)
    
    # DİNAMİK ZAMAN: Bot her zaman 'şu an'da olduğunu bilir.
    now = datetime.now()
    today_str = now.strftime("%d %B %Y %H:%M")

    # KESİN DOĞRULUK TALİMATI
    scout_prompt = f"""
    GÖREV: Bugün {today_str}. Google Search kullanarak Fenerbahçe'nin BU TARİHTEN SONRAKİ İLK RESMİ maçını bul.
    
    PRENSİP: Tahmin yürütme. Sadece TFF, UEFA veya resmi kulüp kanallarındaki veriyi kullan.
    
    Yalnızca aşağıdaki JSON formatında yanıt ver:
    {{
        "next_match": "Ev Sahibi - Deplasman",
        "match_date": "Gün Ay Yıl Saat",
        "match_date_iso": "YYYY-MM-DDTHH:MM:SS",
        "weather": "Derece ve Durum",
        "expert_notes": "Resmi kaynaklara dayalı kısa taktik not",
        "xg_data": {{"Ev": 0.0, "Dep": 0.0}},
        "last_update": "{today_str}"
    }}
    """

    print(f"Scout raporu hazırlanıyor... (Referans Tarih: {today_str})")

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[scout_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0  # Sıfır yaratıcılık, tam gerçeklik.
            )
        )

        # Yanıtı temizle ve JSON'a zorla
        content = response.text.strip()
        start = content.find("{")
        end = content.rfind("}") + 1
        final_data = json.loads(content[start:end])

        # Dosyayı mühürle
        with open("hub_data.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"BAŞARILI: {final_data['next_match']} verisi mühürlendi.")

    except Exception as e:
        print(f"SİSTEM HATASI: {e}")

if __name__ == "__main__":
    run_morning_scout()
