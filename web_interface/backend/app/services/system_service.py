"""
System service for monitoring and management
Системний сервіс для моніторингу та управління
"""

import os
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from ..models.system import (
    SystemStatus, ComponentStatus, RedisStatus, CacheStatus, 
    WebhookStatus, MLStatus, LogEntry, LogResponse, MetricsData, MetricsResponse
)
from ..models.common import StatusEnum
from .mova_service import mova_service
from .file_service import file_service


class SystemService:
    """Системний сервіс"""
    
    def __init__(self):
        """Ініціалізація сервісу"""
        self.start_time = datetime.now()
        self.metrics_history: List[MetricsData] = []
    
    async def get_system_status(self) -> SystemStatus:
        """Отримання статусу системи"""
        try:
            # Загальний статус
            overall_status = StatusEnum.SUCCESS
            
            # Компоненти
            components = []
            
            # MOVA SDK
            sdk_info = mova_service.get_sdk_info()
            components.append(ComponentStatus(
                name="MOVA SDK",
                status=StatusEnum.SUCCESS if sdk_info["available"] else StatusEnum.ERROR,
                version=sdk_info["version"],
                details=sdk_info["components"]
            ))
            
            # Redis
            redis_status = await self._get_redis_status()
            components.append(ComponentStatus(
                name="Redis",
                status=StatusEnum.SUCCESS if redis_status.connected else StatusEnum.ERROR,
                details={"url": redis_status.url, "sessions": redis_status.session_count}
            ))
            
            # Cache
            cache_status = await self._get_cache_status()
            components.append(ComponentStatus(
                name="Cache",
                status=StatusEnum.SUCCESS if cache_status.enabled else StatusEnum.ERROR,
                details={"files": cache_status.total_files, "size": cache_status.total_size}
            ))
            
            # Webhook
            webhook_status = await self._get_webhook_status()
            components.append(ComponentStatus(
                name="Webhook",
                status=StatusEnum.SUCCESS if webhook_status.enabled else StatusEnum.ERROR,
                details={"endpoints": webhook_status.endpoints_count}
            ))
            
            # ML
            ml_status = await self._get_ml_status()
            components.append(ComponentStatus(
                name="ML Integration",
                status=StatusEnum.SUCCESS if ml_status.enabled else StatusEnum.ERROR,
                details={"models": ml_status.models_count}
            ))
            
            # Файлова система
            file_system_status = await self._get_file_system_status()
            components.append(ComponentStatus(
                name="File System",
                status=StatusEnum.SUCCESS,
                details=file_system_status
            ))
            
            # Перевіряємо чи є помилки
            if any(c.status == StatusEnum.ERROR for c in components):
                overall_status = StatusEnum.ERROR
            
            return SystemStatus(
                overall_status=overall_status,
                version="2.2.0",
                uptime=(datetime.now() - self.start_time).total_seconds(),
                components=components
            )
        
        except Exception as e:
            logger.error(f"System status retrieval failed: {e}")
            return SystemStatus(
                overall_status=StatusEnum.ERROR,
                version="2.2.0",
                uptime=(datetime.now() - self.start_time).total_seconds(),
                components=[]
            )
    
    async def _get_redis_status(self) -> RedisStatus:
        """Отримання статусу Redis"""
        try:
            if not mova_service.is_available():
                return RedisStatus(
                    connected=False,
                    url="N/A",
                    session_count=0,
                    error="MOVA SDK not available"
                )
            
            redis_manager = mova_service.get_redis_manager()
            sessions = redis_manager.list_sessions()
            
            return RedisStatus(
                connected=True,
                url=redis_manager.redis_url,
                session_count=len(sessions)
            )
        
        except Exception as e:
            return RedisStatus(
                connected=False,
                url="redis://localhost:6379",
                session_count=0,
                error=str(e)
            )
    
    async def _get_cache_status(self) -> CacheStatus:
        """Отримання статусу кешу"""
        try:
            if not mova_service.is_available():
                return CacheStatus(
                    enabled=False,
                    cache_dir="N/A",
                    total_files=0,
                    total_size=0
                )
            
            cache_manager = mova_service.get_cache_manager()
            stats = cache_manager.get_stats()
            
            return CacheStatus(
                enabled=True,
                cache_dir=str(cache_manager.cache_dir),
                total_files=stats.get("total_files", 0),
                total_size=stats.get("total_size", 0),
                hit_rate=stats.get("hit_rate", 0.0)
            )
        
        except Exception as e:
            return CacheStatus(
                enabled=False,
                cache_dir="N/A",
                total_files=0,
                total_size=0
            )
    
    async def _get_webhook_status(self) -> WebhookStatus:
        """Отримання статусу webhook"""
        try:
            if not mova_service.is_available():
                return WebhookStatus(
                    enabled=False,
                    endpoints_count=0
                )
            
            webhook_integration = mova_service.get_webhook_integration()
            
            return WebhookStatus(
                enabled=True,
                endpoints_count=len(webhook_integration.endpoints),
                last_event=webhook_integration.last_event_time,
                error_rate=webhook_integration.error_rate
            )
        
        except Exception as e:
            return WebhookStatus(
                enabled=False,
                endpoints_count=0
            )
    
    async def _get_ml_status(self) -> MLStatus:
        """Отримання статусу ML"""
        try:
            if not mova_service.is_available():
                return MLStatus(
                    enabled=False,
                    models_count=0,
                    active_models=[]
                )
            
            ml_integration = mova_service.get_ml_integration()
            models = ml_integration.list_models()
            
            return MLStatus(
                enabled=True,
                models_count=len(models),
                active_models=[m["id"] for m in models if m.get("active", False)],
                last_training=ml_integration.last_training_time,
                accuracy=ml_integration.get_average_accuracy()
            )
        
        except Exception as e:
            return MLStatus(
                enabled=False,
                models_count=0,
                active_models=[]
            )
    
    async def _get_file_system_status(self) -> Dict[str, Any]:
        """Отримання статусу файлової системи"""
        try:
            # Розмір завантажень
            upload_size = await file_service.get_directory_size("mova")
            temp_size = await file_service.get_directory_size("temp")
            exports_size = await file_service.get_directory_size("exports")
            
            # Вільне місце на диску
            disk_usage = psutil.disk_usage('/')
            
            return {
                "upload_size": upload_size,
                "temp_size": temp_size,
                "exports_size": exports_size,
                "disk_free": disk_usage.free,
                "disk_total": disk_usage.total,
                "disk_used": disk_usage.used
            }
        
        except Exception as e:
            logger.error(f"File system status failed: {e}")
            return {}
    
    async def get_system_metrics(self, time_range: str = "1h") -> MetricsResponse:
        """Отримання системних метрик"""
        try:
            # Визначаємо часовий діапазон
            now = datetime.now()
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(days=1)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(hours=1)
            
            # Фільтруємо історію метрик
            filtered_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= start_time
            ]
            
            return MetricsResponse(
                metrics=filtered_metrics,
                time_range=time_range,
                aggregation="average"
            )
        
        except Exception as e:
            logger.error(f"Metrics retrieval failed: {e}")
            return MetricsResponse(
                metrics=[],
                time_range=time_range,
                aggregation="average"
            )
    
    async def collect_metrics(self):
        """Збір метрик"""
        try:
            now = datetime.now()
            
            # CPU використання
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_history.append(MetricsData(
                timestamp=now,
                value=cpu_percent,
                label="CPU Usage",
                category="system"
            ))
            
            # Використання пам'яті
            memory = psutil.virtual_memory()
            self.metrics_history.append(MetricsData(
                timestamp=now,
                value=memory.percent,
                label="Memory Usage",
                category="system"
            ))
            
            # Використання диску
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics_history.append(MetricsData(
                timestamp=now,
                value=disk_percent,
                label="Disk Usage",
                category="system"
            ))
            
            # Кількість активних з'єднань
            connections = len(psutil.net_connections())
            self.metrics_history.append(MetricsData(
                timestamp=now,
                value=connections,
                label="Active Connections",
                category="network"
            ))
            
            # Обмежуємо історію до останніх 1000 записів
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
        
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Отримання інформації про систему"""
        try:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage('/').total,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "process_id": os.getpid(),
                "user": os.getlogin(),
                "hostname": platform.node()
            }
        
        except Exception as e:
            logger.error(f"System info retrieval failed: {e}")
            return {}
    
    async def cleanup_system(self) -> Dict[str, Any]:
        """Очищення системи"""
        try:
            results = {}
            
            # Очищення тимчасових файлів
            temp_cleaned = await file_service.cleanup_temp_files()
            results["temp_files_cleaned"] = temp_cleaned
            
            # Очищення кешу (якщо доступний)
            if mova_service.is_available():
                try:
                    cache_manager = mova_service.get_cache_manager()
                    cache_manager.clear()
                    results["cache_cleared"] = True
                except Exception as e:
                    results["cache_cleared"] = False
                    results["cache_error"] = str(e)
            
            # Очищення Redis сесій (якщо доступний)
            if mova_service.is_available():
                try:
                    redis_manager = mova_service.get_redis_manager()
                    redis_manager.clear_all_sessions()
                    results["redis_sessions_cleared"] = True
                except Exception as e:
                    results["redis_sessions_cleared"] = False
                    results["redis_error"] = str(e)
            
            logger.info(f"System cleanup completed: {results}")
            return results
        
        except Exception as e:
            logger.error(f"System cleanup failed: {e}")
            return {"error": str(e)}


# Глобальний екземпляр сервісу
system_service = SystemService() 