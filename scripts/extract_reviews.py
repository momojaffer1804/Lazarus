import requests
import time
import pandas as pd
import os

def fetch_steam_reviews(app_id, target_review_count=1000):
    """
    Pulls reviews for a specific Steam game using cursor pagination.
    """
    url = f"https://store.steampowered.com/appreviews/{app_id}"
    
    reviews_data = []
    cursor = '*'  # The API requires '*' for the very first page request
    
    print(f"Starting extraction for App ID: {app_id}...")
    
    while len(reviews_data) < target_review_count:
        params = {
            'json': 1,
            'filter': 'recent',       # Sorts by most recent
            'language': 'english',    # English only for clean sentiment tracking
            'cursor': cursor,
            'review_type': 'all',
            'purchase_type': 'all',
            'num_per_page': 100       # Max allowed per request
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error {response.status_code}. Stopping.")
            break
            
        data = response.json()
        
        if data.get('success') != 1:
            print("API returned unsuccessful status. Stopping.")
            break
            
        batch = data.get('reviews', [])
        
        if not batch:
            print("No more reviews left to pull.")
            break
            
        reviews_data.extend(batch)
        print(f"Pulled {len(reviews_data)} reviews...")
        
        new_cursor = data.get('cursor')
        if new_cursor == cursor:
            break
            
        cursor = new_cursor
        time.sleep(1.5) # CRITICAL: Prevents Steam from IP banning you
        
    return reviews_data

if __name__ == "__main__":
    # Test case: Cyberpunk 2077 (Famous for a disastrous launch and massive recovery)
    GAME_ID = '1091500' 
    TARGET_REVIEWS = 500
    
    raw_reviews = fetch_steam_reviews(app_id=GAME_ID, target_review_count=TARGET_REVIEWS)
    
    # Convert to DataFrame
    df = pd.DataFrame(raw_reviews)
    
    # Ensure the raw data folder exists
    os.makedirs('data/raw', exist_ok=True)
    
    # Save raw JSON-like data to CSV
    output_path = f"data/raw/steam_reviews_{GAME_ID}.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\nSuccess! Raw data saved to {output_path}")