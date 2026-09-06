import pandas as pd
import os
import ast

def clean_review_data(game_id):
    input_file = f"data/raw/steam_reviews_raw_{game_id}.csv"
    output_file = f"data/processed/steam_reviews_clean_{game_id}.csv"
    
    if not os.path.exists(input_file):
        print(f"Skipping {game_id}: {input_file} not found.")
        return

    print(f"--- Cleaning Reviews for App ID {game_id} ---")
    df = pd.read_csv(input_file)
    
    def extract_author_data(row, key):
        try:
            author_dict = ast.literal_eval(row) if isinstance(row, str) else row
            return author_dict.get(key, None)
        except:
            return None

    if 'author' in df.columns:
        df['author_id'] = df['author'].apply(lambda x: str(extract_author_data(x, 'steamid')))
        df['playtime_at_review'] = df['author'].apply(lambda x: extract_author_data(x, 'playtime_at_review'))
    else:
        df['author_id'] = 'Unknown'
        df['playtime_at_review'] = 0

    df = df.rename(columns={
        'recommendationid': 'review_id',
        'voted_up': 'recommended',
        'votes_up': 'helpful_votes',
        'review': 'review_text'
    })
    
    if 'timestamp_created' in df.columns:
        df['review_date'] = pd.to_datetime(df['timestamp_created'], unit='s')
    
    df = df.dropna(subset=['review_id', 'review_text'])
    # Remove cursor pagination duplicates
    df = df.drop_duplicates(subset=['review_id'])
    
    final_cols = ['review_id', 'author_id', 'review_date', 'recommended', 'playtime_at_review', 'helpful_votes', 'review_text']
    df_clean = df[[col for col in final_cols if col in df.columns]]
    
    os.makedirs("data/processed", exist_ok=True)
    df_clean.to_csv(output_file, index=False)
    print(f"Success: Cleaned {len(df_clean)} rows and saved to {output_file}")

if __name__ == "__main__":
    TARGET_GAMES = [1091500, 275850, 379720, 397540, 553850, 1716740, 1151340, 1086940, 292030, 271590]
    for game_id in TARGET_GAMES:
        clean_review_data(game_id)