import firebase_admin
from firebase_admin import credentials, firestore
from statsbombpy import sb
import pandas as pd

# 1. BAĞLANTI
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

MATCH_ID = 3869685
TEAMS = ["Argentina", "France"]

print(f"📊 {MATCH_ID} nolu maç verisi çekiliyor...")
events = sb.events(match_id=MATCH_ID)

for team in TEAMS:
    print(f"\n🔥 {team} verileri işleniyor...")
    
    # --- A. PAS AĞI (SABİT) ---
    team_passes = events[(events.team == team) & (events.type == "Pass") & (events.pass_outcome.isna())].copy()
    team_passes["x"] = team_passes["location"].apply(lambda x: x[0])
    team_passes["y"] = team_passes["location"].apply(lambda x: x[1])
    
    avg_loc = team_passes.groupby("player").agg({"x": "mean", "y": "mean"}).reset_index()
    locations_dict = {row["player"]: [row["x"], row["y"]] for _, row in avg_loc.iterrows()}
    
    pass_links = team_passes.groupby(["player", "pass_recipient"]).size().reset_index(name="count")
    pass_links = pass_links[pass_links["count"] > 2]
    links_dict = {f"{r['player']} -> {r['pass_recipient']}": int(r["count"]) for _, r in pass_links.iterrows()}

    db.collection("analytics").document(f"pass_network_{team}_{MATCH_ID}").set({
        "locations": locations_dict, "links": links_dict
    })

    # --- B. ISI HARİTASI (SABİT) ---
    team_events = events[(events.team == team) & (events.location.notna())].copy()
    heat_data = [{"player": r["player"], "x": r["location"][0], "y": r["location"][1]} for _, r in team_events.iterrows()]
    
    db.collection("analytics").document(f"heatmap_{team}_{MATCH_ID}").set({"events": heat_data})

    # --- C. ŞUT HARİTASI (YENİ! 🥅) ---
    # Sadece şutları al
    team_shots = events[(events.team == team) & (events.type == "Shot")].copy()
    
    shot_data = []
    for _, row in team_shots.iterrows():
        shot_data.append({
            "player": row["player"],
            "x": row["location"][0],
            "y": row["location"][1],
            "xg": row["shot_statsbomb_xg"] if "shot_statsbomb_xg" in row else 0, # xG değeri
            "outcome": row["shot_outcome"] # Gol mü, kaçtı mı?
        })
        
    db.collection("analytics").document(f"shots_{team}_{MATCH_ID}").set({
        "shots": shot_data
    })
    print(f"   ✅ Şut verileri ({len(shot_data)} şut) kaydedildi.")

print("\n🚀 TÜM İŞLEMLER TAMAM! Şutlar hazır.")