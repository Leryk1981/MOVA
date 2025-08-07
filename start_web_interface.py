#!/usr/bin/env python3
"""
MOVA Web Interface Launcher
Запуск веб-інтерфейсу MOVA з кореневої директорії
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Головна функція запуску"""
    print("🚀 MOVA Web Interface Launcher")
    print("=" * 50)
    
    # Шлях до backend
    backend_path = Path(__file__).parent / "web_interface" / "backend"
    
    if not backend_path.exists():
        print(f"❌ Backend path not found: {backend_path}")
        return False
    
    print(f"📁 Backend path: {backend_path}")
    print(f"🌐 Server will be available at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/api/docs")
    print("=" * 50)
    
    try:
        # Змінюємо директорію на backend
        os.chdir(backend_path)
        
        # Запускаємо backend
        print("🚀 Starting MOVA Web Interface Backend...")
        subprocess.run([sys.executable, "run.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 