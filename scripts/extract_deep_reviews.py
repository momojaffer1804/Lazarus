import requests
import pandas as pd
import time
import os

def fetch_historical_reviews(app_id, max_reviews=3000):
    print(f"\n--- Initiating Deep Scrape for App ID {app_id} ---")
    url = f"https://store.steampowered.com/appreviews/{app_id}?json=1"
    
    reviews = []
    cursor = '*'
    
    while len(reviews) < max_reviews:
        params = {
            'json': 1,
            'filter': 'all',        # Pivot from 'recent' to 'all-time'
            'language': 'english',
            'cursor': cursor,
            'num_per_page': 100,
            'purchase_type': 'all'  # Captures both Steam and external key reviews
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"API Error {response.status_code}. Halting extraction for {app_id}.")
                break
                
            data = response.json()
            if 'reviews' not in data or not data['reviews']:
                print("No more historical reviews found.")
                break
                
            reviews.extend(data['reviews'])
            cursor = data['cursor']
            print(f"Archived {len(reviews)} / {max_reviews} reviews...")
            
            time.sleep(1.5) # Hard rate limit safeguard
            
        except Exception as e:
            print(f"Connection failure: {e}")
            break
            
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
        raw_reviews = fetch_historical_reviews(game_id, max_reviews=3000)
        if raw_reviews:
            df = pd.DataFrame(raw_reviews)
            output_file = f"data/raw/steam_reviews_raw_{game_id}.csv"
            df.to_csv(output_file, index=False)
            print(f"Success: Saved deep dataset for {game_name}")