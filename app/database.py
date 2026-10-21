import os
import shutil
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

IS_VERCEL = bool(os.environ.get("VERCEL"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_DB = os.path.join(BASE_DIR, "faculty_load.db")

# 1. Check for PostgreSQL DATABASE_URL (Supabase, Neon, etc.)
raw_db_url = os.environ.get("DATABASE_URL")

if raw_db_url:
    # SQLAlchemy 2.0+ requires 'postgresql://' instead of legacy 'postgres://'
    if raw_db_url.startswith("postgres://"):
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = raw_db_url

    # Serverless-friendly PostgreSQL engine with health pre-ping & connection recycling
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )
    print("[Database] Initialized with PostgreSQL connection pool")
else:
    # 2. Fallback to SQLite (local development or serverless /tmp)
    if IS_VERCEL:
        temp_dir = "/tmp" if os.path.isdir("/tmp") else tempfile.gettempdir()
        DATABASE_FILE = os.path.join(temp_dir, "faculty_load.db")
        
        # Copy pre-seeded DB if available
        if not os.path.exists(DATABASE_FILE) and os.path.exists(BUNDLED_DB):
            try:
                shutil.copy2(BUNDLED_DB, DATABASE_FILE)
                print(f"[Database] Copied bundled faculty_load.db to {DATABASE_FILE}")
            except Exception as e:
                print(f"[Database Copy Warning]: {e}")
    else:
        DATABASE_FILE = BUNDLED_DB

    DATABASE_URL = f"sqlite:///{DATABASE_FILE}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    print(f"[Database] Initialized with SQLite ({DATABASE_FILE})")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
