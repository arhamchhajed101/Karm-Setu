#!/usr/bin/env python3
"""
Convenience launcher to run KarmSetu Backend from the repository root.
Usage:
    python run_backend.py
"""
import sys
import os
import uvicorn

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if __name__ == "__main__":
    print("🚀 Starting KarmSetu Backend on http://localhost:8000 ...")
    print("📖 Swagger API Docs: http://localhost:8000/docs")
    print("📚 ReDoc API Docs:   http://localhost:8000/redoc")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=BACKEND_DIR)
