import pandas as pd
from sqlalchemy import create_engine, text
import os
import time
from dotenv import load_dotenv

def load_events_to_db(csv_path, game_id):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("Error: DATABASE_URL not found in .env file.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url, pool_pre_ping=True)
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS patch_events (
        event_id TEXT PRIMARY KEY,
        game_id INT,
        event_title TEXT,
        event_date DATE,
        url TEXT
    );
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_query))
            conn.commit()

        df = pd.read_csv(csv_path)
        df.to_sql('patch_events', engine, if_exists='append', index=False, method='multi')
        print(f"Success! {len(df)} patches inserted for App ID {game_id}.")
        
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}.")
    except Exception as e:
        print(f"Error during insertion for {game_id}: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    TARGET_GAMES = [1091500, 275850, 379720, 397540, 553850, 1716740, 1151340, 1086940, 292030, 271590]
    for game_id in TARGET_GAMES:
        CSV_FILE = f"data/raw/patch_events_{game_id}.csv"
        if os.path.exists(CSV_FILE):
            print(f"\n--- Loading Patches for App ID {game_id} ---")
            load_events_to_db(CSV_FILE, game_id)
            time.sleep(2)
        else:
            print(f"Skipping {game_id}: Patch CSV not found.")