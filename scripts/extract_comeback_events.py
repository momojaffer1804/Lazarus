import requests
import pandas as pd
import os

def fetch_patch_events(app_id, output_path):
    print(f"Fetching update timeline for App ID {app_id}...")
    url = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={app_id}&count=200&maxlength=300&format=json"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error {response.status_code} for {app_id}.")
        return
        
    news_items = response.json().get('appnews', {}).get('newsitems', [])
    patches = []
    
    for item in news_items:
        title = item.get('title', '').lower()
        if 'patch' in title or 'update' in title or 'hotfix' in title:
            patches.append({
                'event_id': item.get('gid'),
                'game_id': app_id,
                'event_title': item.get('title'),
                'event_date': pd.to_datetime(item.get('date'), unit='s').strftime('%Y-%m-%d'),
                'url': item.get('url')
            })
    
    df = pd.DataFrame(patches)
    if df.empty:
        print(f"No patch notes found for {app_id}.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Success! {len(df)} events saved to {output_path}")

if __name__ == "__main__":
    TARGET_GAMES = [1091500, 275850, 379720, 397540, 553850, 1716740, 1151340, 1086940, 292030, 271590]
    for game_id in TARGET_GAMES:
        OUTPUT_FILE = f"data/raw/patch_events_{game_id}.csv"
        print(f"\n--- Extracting Patches for App ID {game_id} ---")
        fetch_patch_events(game_id, OUTPUT_FILE)