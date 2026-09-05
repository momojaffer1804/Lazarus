import pandas as pd
import ast
import os

def clean_raw_reviews(input_path, output_path):
    print(f"Loading raw data from {input_path}...")
    
    # Read the raw CSV
    df = pd.read_csv(input_path)
    
    # The 'author' column comes in as a string representation of a dictionary. 
    # ast.literal_eval safely turns it back into a real Python dictionary so we can extract data from it.
    print("Unpacking nested player data...")
    df['author'] = df['author'].apply(ast.literal_eval)
    
    # Extract the exact fields we need for our schema
    df['author_id'] = df['author'].apply(lambda x: x.get('steamid'))
    
    # Playtime is in minutes. We will keep it that way for granular analysis.
    df['playtime_at_review'] = df['author'].apply(lambda x: x.get('playtime_at_review'))
    
    # Convert Steam's Unix timestamp to a clean standard Date/Time
    print("Formatting timestamps...")
    df['review_date'] = pd.to_datetime(df['timestamp_created'], unit='s')
    
    # Rename columns so they map perfectly to our Postgres database schema
    df = df.rename(columns={
        'recommendationid': 'review_id',
        'voted_up': 'recommended',
        'votes_up': 'helpful_votes',
        'review': 'review_text'
    })
    
    # Select only the clean columns we want to keep
    final_cols = [
        'review_id', 'author_id', 'review_date', 
        'recommended', 'playtime_at_review', 'helpful_votes', 'review_text'
    ]
    df_cleaned = df[final_cols]
    
    # Drop any rows that are completely empty (just in case)
    df_cleaned = df_cleaned.dropna(subset=['review_id'])
    
    # Ensure the processed folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the polished data
    df_cleaned.to_csv(output_path, index=False)
    
    print(f"Success! Clean data saved to {output_path}\n")
    print("--- PREVIEW ---")
    print(df_cleaned.head(3))

if __name__ == "__main__":
    GAME_ID = '1091500' # Cyberpunk 2077
    
    INPUT_FILE = f"data/raw/steam_reviews_{GAME_ID}.csv"
    OUTPUT_FILE = f"data/processed/steam_reviews_clean_{GAME_ID}.csv"
    
    clean_raw_reviews(INPUT_FILE, OUTPUT_FILE)