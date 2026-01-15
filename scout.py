import os
import json
from datetime import datetime
from google import genai
from google.genai import types

def run_morning_scout():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    # Bugünü dinamik al
    today = datetime.now().strftime("%d %B %Y")

    # SORGUNU GÜÇLENDİRDİK: Site kısıtlaması ve veri zorunluluğu ekledik
    scout_prompt = f"""
    Bugün {today}. 
    Google Search kullanarak 'Fenerbahçe fikstür 2026' ve 'Fenerbahçe sıradaki maç' araması yap.
    Mackolik, NTV Spor veya TFF sitelerindeki güncel veriyi temel al.
    
    Aşağıdaki JSON şablonunu EKSİKSİZ doldur. 
    Eğer maç bulamazsan 'next_match' kısmına 'Fikstür Aranıyor' yaz ama ASLA boş bırakma.
    
    {{
        "next_match": "Ev Sahibi - Deplasman",
        "match_date": "Gün Ay Saat",
        "match_date_iso": "2026-MM-DDTHH:MM:SS",
        "weather": "Tahmini Derece",
        "expert_notes": "Maçın önemi hakkında 1 cümle",
        "xg_data": {{"Ev": 1.5, "Dep": 1.3}},
        "last_update": "{today}"
    }}
    """

    try:
        # Temperature 0.0 yaparak hayal kurmasını engelliyoruz
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[scout_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0 
            )
        )

        content = response.text.strip()
        # JSON bloğunu cımbızla çek
        start = content.find("{")
        end = content.rfind("}") + 1
        
        if start != -1:
            final_data = json.loads(content[start:end])
            
            # Eğer halüsinasyon görüp şablonu doldurmadıysa hata fırlat
            if "Ev Sahibi" in final_data["next_match"]:
                raise ValueError("Gerçek maç verisi çekilemedi, taslak veri döndü.")

            with open("hub_data.json", "w", encoding="utf-8") as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)
            print(f"BAŞARILI: {final_data['next_match']} kaydedildi.")
        else:
            print("HATA: JSON formatı bulunamadı.")

    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    run_morning_scout()
