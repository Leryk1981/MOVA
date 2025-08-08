"""
MOVA Web Interface Backend
Веб-інтерфейс MOVA - Backend
"""

import sys
import os
from pathlib import Path

# Додаємо шлях до MOVA SDK
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger

from app.core.config import settings
from app.api.routes import api_router
from app.core.events import create_start_app_handler, create_stop_app_handler


def create_application() -> FastAPI:
    """Створення FastAPI додатку"""
    
    app = FastAPI(
        title="MOVA Web Interface",
        description="Веб-інтерфейс для управління MOVA 2.2",
        version="2.2.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Event handlers
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))
    
    # API routes
    app.include_router(api_router, prefix="/api")
    
    # Static files (для production)
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Головна сторінка"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MOVA Web Interface</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .links { margin-top: 20px; }
                .links a { margin-right: 20px; color: #007bff; text-decoration: none; }
                .links a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 MOVA Web Interface</h1>
                    <p>Веб-інтерфейс для управління MOVA 2.2</p>
                </div>
                <div class="links">
                    <a href="/api/docs">📚 API Documentation</a>
                    <a href="/api/redoc">📖 ReDoc</a>
                    <a href="/api/health">🏥 Health Check</a>
                </div>
                <div style="margin-top: 40px;">
                    <h3>Quick Start:</h3>
                    <ul>
                        <li>API Documentation: <a href="/api/docs">/api/docs</a></li>
                        <li>Health Check: <a href="/api/health">/api/health</a></li>
                        <li>System Status: <a href="/api/system/status">/api/system/status</a></li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": "2.2.0",
            "service": "MOVA Web Interface"
        }
    
    return app


app = create_application()


if __name__ == "__main__":
    logger.info("Starting MOVA Web Interface...")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 