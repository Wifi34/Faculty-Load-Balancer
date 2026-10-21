import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import SessionLocal, IS_VERCEL, get_db
from app.seed_data import init_db, seed_sample_data
from app.scheduler import start_background_scheduler, stop_background_scheduler, check_and_generate_reminders
from app.api.auth_routes import router as auth_router
from app.api.faculty_routes import router as faculty_router
from app.api.schedule_routes import router as schedule_router
from app.api.notification_routes import router as notification_router
from app.api.report_routes import router as report_router
from app.api.master_routes import router as master_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

def setup_database():
    """Ensure database schema exists and seed data is populated if empty."""
    try:
        init_db()
        db: Session = SessionLocal()
        try:
            seed_sample_data(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[Database Setup Warning]: {e}")

# If running on Vercel, initialize DB immediately on module import
if IS_VERCEL:
    setup_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not IS_VERCEL:
        print("[Application Lifecycle] Initializing database...")
        setup_database()
        print("[Application Lifecycle] Starting background scheduler...")
        try:
            start_background_scheduler()
        except Exception as e:
            print(f"[Scheduler Startup Warning]: {e}")
        print("[Application Lifecycle] System ready at http://127.0.0.1:8000")
    yield
    # Shutdown
    if not IS_VERCEL:
        print("[Application Lifecycle] Stopping background services...")
        try:
            stop_background_scheduler()
        except Exception as e:
            print(f"[Scheduler Shutdown Warning]: {e}")

app = FastAPI(
    title="Faculty Load Management System - SCET",
    description="Suryodaya College Of Engineering and Technology - Faculty Load, Timetable, Duty Assignment, and Notification Portal",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router)
app.include_router(faculty_router)
app.include_router(schedule_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(master_router)

# Ensure directories exist (only attempt on writable filesystem)
if not IS_VERCEL:
    try:
        os.makedirs(STATIC_DIR, exist_ok=True)
        os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
        os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
    except OSError:
        pass

# Mount static files if directory exists
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    candidates = [
        os.path.join(TEMPLATES_DIR, "index.html"),
        os.path.join(BASE_DIR, "templates", "index.html"),
        os.path.join(os.getcwd(), "templates", "index.html")
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Suryodaya College Of Engineering and Technology</h1><p>Faculty Load Management System is loading...</p>")

@app.api_route("/api/cron/reminders", methods=["GET", "POST"])
def cron_reminders(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Automated reminder cron endpoint called by Vercel Cron or external scheduler.
    Optionally verified against CRON_SECRET if configured.
    """
    cron_secret = os.environ.get("CRON_SECRET")
    auth_header = request.headers.get("authorization")
    if cron_secret and auth_header != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized cron invocation")

    import datetime
    check_and_generate_reminders(db)
    return {
        "status": "success",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "college": "Suryodaya College Of Engineering and Technology",
        "message": "Automated schedule reminders scanned and generated successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
