#!/usr/bin/env python3
"""
MOVA Web Interface Backend Runner
Запуск веб-інтерфейсу MOVA
"""

import sys
import os
from pathlib import Path

# Додаємо шлях до MOVA SDK
sdk_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(sdk_path))

if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🚀 Starting MOVA Web Interface Backend...")
    print(f"📁 SDK Path: {sdk_path}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/api/docs")
    print(f"📖 ReDoc: http://localhost:8000/api/redoc")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 