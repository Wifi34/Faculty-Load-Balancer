import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Ensure project root is in sys.path so 'app' package is always resolvable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.database import SessionLocal, IS_VERCEL, get_db
from app.seed_data import init_db, seed_sample_data
from app.scheduler import start_background_scheduler, stop_background_scheduler, check_and_generate_reminders
from app.api.auth_routes import router as auth_router
from app.api.faculty_routes import router as faculty_router
from app.api.schedule_routes import router as schedule_router
from app.api.notification_routes import router as notification_router
from app.api.report_routes import router as report_router
from app.api.master_routes import router as master_router

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only run background services and local db setup on non-serverless environments
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

# Mount static files safely
static_candidates = [
    STATIC_DIR,
    os.path.join(os.getcwd(), "static"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
]
for sc in static_candidates:
    if os.path.exists(sc):
        app.mount("/static", StaticFiles(directory=sc), name="static")
        break

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    candidates = [
        os.path.join(TEMPLATES_DIR, "index.html"),
        os.path.join(BASE_DIR, "templates", "index.html"),
        os.path.join(os.getcwd(), "templates", "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "index.html")
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Suryodaya College Of Engineering and Technology</h1><p>Faculty Load Management System is loading...</p>")

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

@app.get("/robots.txt")
async def robots():
    return PlainTextResponse("User-agent: *\nDisallow:")

@app.api_route("/api/cron/reminders", methods=["GET", "POST"])
def cron_reminders(
    request: Request,
    db: Session = Depends(get_db)
):
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
