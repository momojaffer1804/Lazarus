import pandas as pd
from sqlalchemy import create_engine, text
import os
import time
from dotenv import load_dotenv

def load_data_to_db(csv_path, game_id):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("Error: DATABASE_URL not found in .env file.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url, pool_pre_ping=True)
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS reviews (
        review_id BIGINT PRIMARY KEY,
        game_id INT,
        author_id TEXT,
        review_date TIMESTAMP,
        recommended BOOLEAN,
        playtime_at_review INT,
        helpful_votes INT,
        review_text TEXT
    );
    """
    
    try:
        # 1. Force a strict commit for table creation
        with engine.begin() as conn:
            conn.execute(text(create_table_query))

        df = pd.read_csv(csv_path)
        df['game_id'] = game_id

        # 2. Force a strict commit for the Pandas insert
        with engine.begin() as conn:
            df.to_sql('reviews', conn, if_exists='append', index=False, method='multi')
            
        print(f"Success! {len(df)} rows actually committed for App ID {game_id}.")
        
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}.")
    except Exception as e:
        print(f"Error for {game_id}: {e}")
    finally:
        engine.dispose()
if __name__ == "__main__":
    TARGET_GAMES = [1091500, 275850, 379720, 397540, 553850, 1716740, 1151340, 1086940, 292030, 271590]
    for game_id in TARGET_GAMES:
        CLEAN_CSV = f"data/processed/steam_reviews_clean_{game_id}.csv"
        if os.path.exists(CLEAN_CSV):
            print(f"\n--- Loading Reviews for App ID {game_id} ---")
            load_data_to_db(CLEAN_CSV, game_id)
            # FIX 3: Let the DB breathe
            time.sleep(2)
        else:
            print(f"Skipping {game_id}: Clean CSV not found.")