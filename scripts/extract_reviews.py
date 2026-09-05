import requests
import pandas as pd
import time
import os

def fetch_steam_reviews(app_id, max_reviews=500):
    print(f"\n--- Starting extraction for App ID {app_id} ---")
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    
    reviews = []
    cursor = '*'
    
    while len(reviews) < max_reviews:
        params = {
            'json': 1,
            'filter': 'recent',
            'language': 'english',
            'cursor': cursor,
            'num_per_page': 100
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"API Error {response.status_code} for game {app_id}")
            break
            
        data = response.json()
        
        if 'reviews' not in data or not data['reviews']:
            break
            
        reviews.extend(data['reviews'])
        cursor = data['cursor']
        print(f"Fetched {len(reviews)} reviews...")
        
        time.sleep(1) # Respect API rate limits
        
    return reviews[:max_reviews]

if __name__ == "__main__":
    TARGET_GAMES = {
        1091500: "Cyberpunk 2077", 275850: "No Mans Sky", 
        379720: "DOOM", 397540: "Borderlands 3",
        553850: "Helldivers 2", 1716740: "Starfield", 
        1151340: "Fallout 76", 1086940: "Baldurs Gate 3", 
        292030: "The Witcher 3", 271590: "Grand Theft Auto V"
    }
    
    os.makedirs("data/raw", exist_ok=True)
    
    for game_id, game_name in TARGET_GAMES.items():
        raw_reviews = fetch_steam_reviews(game_id, max_reviews=500)
        if raw_reviews:
            df = pd.DataFrame(raw_reviews)
            output_file = f"data/raw/steam_reviews_raw_{game_id}.csv"
            df.to_csv(output_file, index=False)
            print(f"Saved {len(df)} reviews for {game_name}")