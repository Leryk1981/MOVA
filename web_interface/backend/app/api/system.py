"""
System API routes
API роути для системних операцій
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from ..models.system import (
    SystemStatus, LogResponse, MetricsResponse
)
from ..models.common import ResponseModel, StatusEnum
from ..services.system_service import system_service
from ..services.mova_service import mova_service

router = APIRouter()


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Отримання статусу системи"""
    try:
        return await system_service.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_system_info():
    """Отримання інформації про систему"""
    try:
        info = await system_service.get_system_info()
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="System info retrieved",
            data=info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_system_metrics(time_range: str = "1h"):
    """Отримання системних метрик"""
    try:
        metrics = await system_service.get_system_metrics(time_range)
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="System metrics retrieved",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/collect")
async def collect_metrics():
    """Збір метрик"""
    try:
        await system_service.collect_metrics()
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Metrics collected successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_system():
    """Очищення системи"""
    try:
        results = await system_service.cleanup_system()
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="System cleanup completed",
            data=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sdk/info")
async def get_sdk_info():
    """Отримання інформації про MOVA SDK"""
    try:
        sdk_info = mova_service.get_sdk_info()
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="SDK info retrieved",
            data=sdk_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check"""
    try:
        # Перевіряємо основні компоненти
        checks = {
            "api": True,
            "mova_sdk": mova_service.is_available(),
            "system": True
        }
        
        overall_healthy = all(checks.values())
        
        return ResponseModel(
            status=StatusEnum.SUCCESS if overall_healthy else StatusEnum.ERROR,
            message="Health check completed",
            data={
                "healthy": overall_healthy,
                "checks": checks,
                "timestamp": system_service.start_time.isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 