import os
import sys
import traceback

# Ensure VERCEL environment variable is set
os.environ["VERCEL"] = "1"

# Add project root directory to sys.path so modules like app, main can be resolved
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    err_trace = traceback.format_exc()
    print(f"[FATAL VERCEL STARTUP ERROR]: {err_trace}", file=sys.stderr)

    app = FastAPI(title="Startup Error")

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def catch_all_error(full_path: str):
        return HTMLResponse(
            status_code=500,
            content=f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Server Error - Faculty Load Balancer</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; }}
        .card {{ background: #1e293b; border: 1px solid #ef4444; border-radius: 10px; padding: 24px; max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #ef4444; margin-top: 0; }}
        pre {{ background: #090d16; color: #fca5a5; padding: 16px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; font-size: 13px; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Vercel Serverless Function Startup Error</h1>
        <p>The application encountered an unhandled exception during cold boot:</p>
        <pre>{err_trace}</pre>
    </div>
</body>
</html>"""
        )
