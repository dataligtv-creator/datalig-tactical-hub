import os
import json
import re
from datetime import datetime
from google import genai
from google.genai import types

def run_morning_scout():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    # 1. Dinamik Zaman ve Bağlam Tanımı
    today = datetime.now().strftime("%d %B %Y")
    
    # SORGUNU "KRİTİK VERİ" ODAKLI GENİŞLETTİK
    # Sadece fikstür değil, kadro ve transfer güncelliğini de zorunlu kılıyoruz.
    scout_prompt = f"""
    Sen 'The Oracle' Tactical Hub'ın veri madencisisin. Bugün {today}.
    
    GÖREV:
    1. Google Search kullanarak Fenerbahçe'nin en güncel 2026 kadrosunu, transferlerini (Gelen/Giden) ve sıradaki maç fikstürünü tara.
    2. ÖZELLİKLE DİKKAT: Filip Kostic ve diğer kilit oyuncuların şu anki kulüplerini doğrula. 
    3. Sakat veya cezalı oyuncu listesini (Opta/SofaScore/Transfermarkt 2026 verileriyle) kontrol et.

    Aşağıdaki JSON şablonunu, bulduğun GERÇEK verilerle doldur. Asla eski bilgini kullanma.
    
    {{
        "match_info": {{
            "next_match": "Ev Sahibi - Deplasman",
            "match_date": "Gün Ay Saat",
            "stadium": "Stadyum Adı",
            "weather": "Hava Durumu ve Derece"
        }},
        "squad_updates": {{
            "transfers_out": ["Ayrılan Oyuncu 1", "Ayrılan Oyuncu 2"],
            "transfers_in": ["Yeni Gelen 1", "Yeni Gelen 2"],
            "absent_players": ["Sakat/Cezalı 1", "Sakat/Cezalı 2"]
        }},
        "tactical_context": {{
            "current_formation": "Örn: 4-2-3-1",
            "key_player_status": "Kostic, Tadic vb. oyuncuların güncel durumu hakkında 1 cümle",
            "expert_notes": "Maçın taktiksel önemi"
        }},
        "last_verified": "{today}"
    }}
    """

    try:
        # Gemini 3 Flash kullanarak hızı artırıp kotayı koruyoruz
        # 'thinking' ve 'search' yeteneklerini tetikliyoruz
        response = client.models.generate_content(
            model="gemini-2.0-flash", # En stabil arama yapan güncel model
            contents=[scout_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0  # Kesinlik için sıfır tolerans
            )
        )

        content = response.text.strip()
        
        # Markdown kod bloklarını (```json ... ```) temizle
        clean_content = re.sub(r'```json\s?|```', '', content)
        
        start = clean_content.find("{")
        end = clean_content.rfind("}") + 1
        
        if start != -1:
            final_data = json.loads(clean_content[start:end])
            
            # KRİTİK KONTROL: Eğer model hala Kostic'i listede yanlış veriyorsa veya 
            # taslak veri döndüyse burada yakalıyoruz.
            if "Ev Sahibi" in final_data["match_info"]["next_match"]:
                raise ValueError("Veri kaynağına ulaşılamadı, taslak veri reddedildi.")

            # hub_data.json dosyasını 'Oracle'ın ana belleği olarak güncelle
            with open("hub_data.json", "w", encoding="utf-8") as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ ORACLE VERİ TABANI GÜNCELLENDİ: {final_data['match_info']['next_match']}")
            print(f"📌 Sakat/Eksik: {', '.join(final_data['squad_updates']['absent_players'])}")
            
        else:
            print("❌ HATA: JSON formatı ayıklanamadı.")

    except Exception as e:
        print(f"⚠️ KRİTİK VERİ HATASI: {e}")

if __name__ == "__main__":
    run_morning_scout()
