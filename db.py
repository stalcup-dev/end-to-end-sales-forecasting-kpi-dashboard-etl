# db.py (repo root)
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

def get_engine():
    # Load .env only once per process; safe to call multiple times
    load_dotenv()
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        # Alternatively build from PG_USER/PG_PASS/PG_HOST/PG_PORT/PG_DB
        user = os.getenv("PG_USER")
        pwd  = os.getenv("PG_PASS")
        host = os.getenv("PG_HOST", "localhost")
        port = os.getenv("PG_PORT", "5432")
        db   = os.getenv("PG_DB")
        if not all([user, pwd, db]):
            raise RuntimeError("Database credentials not found. Set DB_URI or PG_* vars in .env")
        db_uri = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(db_uri, pool_pre_ping=True)
