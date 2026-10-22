"""
Main application launcher for local development and direct executions.
Imports the configured FastAPI ASGI application from api.index.
"""
from api.index import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="127.0.0.1", port=8000, reload=True)
