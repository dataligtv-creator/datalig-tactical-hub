import os
import json
import re
from datetime import datetime
from google import genai
from google.genai import types

def run_morning_scout():
    # 0. API Yapılandırması
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ HATA: API Anahtarı bulunamadı.")
        return
    
    client = genai.Client(api_key=api_key)
    today = datetime.now().strftime("%d %B %Y")

    print(f"🚀 The Oracle Tactical Hub Başlatıldı | Tarih: {today}")

    # 1. AŞAMA: 3 FLASH - GENİŞ ALAN TARAMASI (Kota Dostu)
    # Bu aşama sadece ham bilgiyi internetten toplar.
    search_prompt = f"""
    Bugün {today}. Fenerbahçe SK için şu bilgileri Google Search ile doğrula:
    1. Güncel A Takım kadrosu (Ocak 2026 transferleri dahil, gidenler hariç).
    2. Son 3 maçın sonuçları ve kısa özeti (Skor, rakip).
    3. Önümüzdeki ilk maç (Rakip, tarih, saat, stadyum).
    4. Güncel sakatlık ve ceza raporu (Tüm pozisyonlar).
    """

    try:
        print("📡 Adım 1: Gemini 3 Flash ile internet taranıyor...")
        search_res = client.models.generate_content(
            model="gemini-3-flash",
            contents=[search_prompt],
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0
            )
        )
        raw_web_data = search_res.text

        # 2. AŞAMA: 2.5 FLASH - ANALİTİK FİLTRELEME
        # Ham veriyi alıp, hata payını sıfırlayarak JSON'a döker.
        print("🧹 Adım 2: Gemini 2.5 Flash ile veri rafine ediliyor...")
        filter_prompt = f"""
        Aşağıdaki ham veriyi incele. Oyuncu isimlerine takılmadan 'Pozisyonel Güç' ve 'Kadro Değişimi' odağıyla JSON üret. 
        Kostic gibi ayrılan oyuncuları 'historical' kısmına, yeni gelenleri 'arrivals' kısmına ekle.
        
        HAM VERİ: {raw_web_data}

        JSON ŞABLONU:
        {{
            "last_sync": "{today}",
            "squad_report": {{
                "arrivals_2026": [],
                "confirmed_departures": [],
                "unavailable_players": ["İsim - Sebep"],
                "positional_gaps": ["Eksik bölgeler"]
            }},
            "recent_form": [
                {{"match": "Rakip", "result": "W/D/L", "score": "0-0"}}
            ],
            "next_battle": {{
                "opponent": "Rakip Adı",
                "date": "Tarih Saat",
                "venue": "Stadyum",
                "weather": "Hava durumu"
            }}
        }}
        """

        filter_res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[filter_prompt],
            config=types.GenerateContentConfig(temperature=0.0)
        )
        
        # JSON Ayıklama
        content = filter_res.text.strip()
        clean_json = re.sub(r'```json\s?|```', '', content)
        start = clean_json.find("{")
        end = clean_json.rfind("}") + 1
        
        if start != -1:
            final_data = json.loads(clean_json[start:end])
            
            # 3. AŞAMA: KAYIT VE MÜHÜRLEME
            with open("hub_data.json", "w", encoding="utf-8") as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ BAŞARILI: {final_data['next_battle']['opponent']} maçı öncesi tüm veriler mühürlendi.")
            print(f"📌 Tespit Edilen Eksikler: {', '.join(final_data['squad_report']['positional_gaps'])}")
        
        else:
            print("❌ HATA: Veri formatlanamadı.")

    except Exception as e:
        # Kota hatası durumunda kullanıcıyı bilgilendir ama programı çökertme
        if "429" in str(e):
            print("⚠️ KOTA UYARISI: Google API limiti doldu. Mevcut 'hub_data.json' korunuyor.")
        else:
            print(f"⚠️ KRİTİK HATA: {e}")

if __name__ == "__main__":
    run_morning_scout()
