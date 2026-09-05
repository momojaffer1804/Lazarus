import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def load_data_to_db(csv_path, game_id):
    # 1. Load the database URL from the .env file
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("Error: DATABASE_URL not found in .env file.")
        return

    # 2. Connect to the Postgres Database
    print("Connecting to cloud database...")
    # SQLAlchemy requires 'postgresql://' not 'postgres://' (Supabase sometimes gives postgres://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    
    # 3. Create the table schema if it doesn't exist
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
    
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()
        print("Schema verified.")

    # 4. Load the clean CSV into Pandas
    print(f"Loading {csv_path} into memory...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}. Did you run the cleaning script?")
        return
        
    # Add the game_id column
    df['game_id'] = game_id

    # 5. Push the data to Postgres
    print("Pushing data to Postgres... (this might take a few seconds)")
    
    try:
        df.to_sql('reviews', engine, if_exists='append', index=False, method='multi')
        print(f"Success! {len(df)} rows inserted into the 'reviews' table.")
    except Exception as e:
        print("Error during insertion. You might be trying to insert duplicate review_ids.")
        print(f"Details: {e}")

if __name__ == "__main__":
    GAME_ID = 1091500 # Cyberpunk 2077
    CLEAN_CSV = f"data/processed/steam_reviews_clean_{GAME_ID}.csv"
    
    load_data_to_db(CLEAN_CSV, GAME_ID)