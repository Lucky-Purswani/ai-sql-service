from app.db.connection import engine
# pyrefly: ignore [missing-import]
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            # 1. Test basic connectivity
            result = conn.execute(text("SELECT version();")).fetchone()
            print("SUCCESS: Connected to NeonDB!")
            print(f"PostgreSQL Version: {result[0][:50]}...")
            
            # 2. Enable pgvector extension (required for AI embeddings later)
            # This is safe to run multiple times
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("SUCCESS: pgvector extension is enabled!")
            
    except Exception as e:
        print("ERROR: Connection failed!")
        print(e)

if __name__ == "__main__":
    test_connection()
