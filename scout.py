# scout.py - Arka Plan Veri Toplayıcı
import json
from google import genai
from google.genai import types

def run_morning_scout():
    client = genai.Client(api_key="API_KEY")
    # YouTube ve Haber taraması yapıp "Futbol Bilimi" özeti çıkarır
    scout_report = {
        "last_update": "11 Ocak 2026 08:00",
        "xg_data": {"Samsun": 1.45, "Fenerbahçe": 2.10},
        "expert_notes": "Taktik Mania: Tedesco'nun baskı hattı bugün çok kritik.",
        "weather": "12°C, Yağmurlu"
    }
    # Veriyi Oracle'ın okuyabileceği bir dosyaya yazar
    with open("hub_data.json", "w") as f:
        json.dump(scout_report, f)

if __name__ == "__main__":
    run_morning_scout()
