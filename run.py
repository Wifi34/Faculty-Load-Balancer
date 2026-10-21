"""
Launcher script for Faculty Load Management System
Run this with: python run.py
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("  FACULTY LOAD MANAGEMENT SYSTEM - SURYODAYA COLLEGE OF ENGG & TECH")
    print("=" * 70)
    print("  Starting server at http://127.0.0.1:8000")
    print("  HOD Login:     Username: hod_cs      | Password: admin123")
    print("  Faculty Login: Username: prof_amit   | Password: faculty123")
    print("  API Docs:      http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
