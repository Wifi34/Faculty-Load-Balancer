import os
import shutil
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

IS_VERCEL = bool(os.environ.get("VERCEL"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_DB = os.path.join(BASE_DIR, "faculty_load.db")

if IS_VERCEL:
    # Use /tmp on Linux/Vercel Lambda, fallback to OS temp dir for cross-platform support
    temp_dir = "/tmp" if os.path.isdir("/tmp") else tempfile.gettempdir()
    DATABASE_FILE = os.path.join(temp_dir, "faculty_load.db")
    
    # In Vercel serverless environment, copy the pre-seeded DB to temp if not already present
    if not os.path.exists(DATABASE_FILE) and os.path.exists(BUNDLED_DB):
        try:
            shutil.copy2(BUNDLED_DB, DATABASE_FILE)
            print(f"[Database] Copied bundled faculty_load.db to {DATABASE_FILE}")
        except Exception as e:
            print(f"[Database Copy Warning]: {e}")
else:
    DATABASE_FILE = BUNDLED_DB

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# check_same_thread=False is needed for SQLite with multi-threaded FastAPI / background scheduler
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
