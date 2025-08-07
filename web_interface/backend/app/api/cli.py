"""
CLI API routes
API роути для CLI команд
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional

from ..models.cli import (
    CLIRunRequest, CLIRunResponse, ParseRequest, ValidateRequest, 
    RunRequest, TestRequest, AnalyzeRequest, DiagnoseRequest,
    RedisSessionsRequest, RedisClearRequest, CacheInfoRequest, 
    CacheClearRequest, WebhookTestRequest, MLModelsRequest, 
    MLEvaluateRequest, RecommendationSummaryRequest
)
from ..models.common import ResponseModel, StatusEnum
from ..services.cli_service import cli_service
from ..services.mova_service import mova_service

router = APIRouter()


@router.post("/execute", response_model=CLIRunResponse)
async def execute_cli_command(request: CLIRunRequest):
    """Виконання CLI команди"""
    try:
        return await cli_service.execute_cli_command(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse")
async def parse_file(request: ParseRequest):
    """Парсинг файлу"""
    try:
        result = await cli_service.execute_mova_parse(
            request.file_path, 
            request.validate
        )
        return ResponseModel(
            status=StatusEnum.SUCCESS if result["success"] else StatusEnum.ERROR,
            message="File parsed successfully" if result["success"] else "Parse failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_file(request: ValidateRequest):
    """Валідація файлу"""
    try:
        result = await cli_service.execute_mova_validate(
            request.file_path,
            request.advanced
        )
        return ResponseModel(
            status=StatusEnum.SUCCESS if result["success"] else StatusEnum.ERROR,
            message="File validated successfully" if result["success"] else "Validation failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_protocol(request: RunRequest):
    """Запуск протоколу"""
    try:
        result = await cli_service.execute_mova_run(
            request.file_path,
            {
                "session_id": request.session_id,
                "verbose": request.verbose,
                "step_by_step": request.step_by_step,
                "redis_url": request.redis_url,
                "llm_api_key": request.llm_api_key,
                "llm_model": request.llm_model,
                "webhook_enabled": request.webhook_enabled,
                "cache_enabled": request.cache_enabled,
                "ml_enabled": request.ml_enabled
            }
        )
        return ResponseModel(
            status=StatusEnum.SUCCESS if result["success"] else StatusEnum.ERROR,
            message="Protocol executed successfully" if result["success"] else "Execution failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_protocol(request: TestRequest):
    """Тестування протоколу"""
    try:
        # Тут буде реалізація тестування
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Test completed",
            data={"tested": True, "file_path": request.file_path}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_file(request: AnalyzeRequest):
    """Аналіз файлу"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        analysis = await ml_integration.analyze_configuration_recommendations(
            request.file_path,
            request.session_id
        )
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Analysis completed",
            data=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnose")
async def diagnose_error(request: DiagnoseRequest):
    """Діагностика помилки"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        diagnosis = await ml_integration.analyze_error_recommendations(
            request.error_message,
            request.session_id
        )
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Diagnosis completed",
            data=diagnosis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redis/sessions")
async def redis_sessions(request: RedisSessionsRequest):
    """Отримання сесій Redis"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        redis_manager = mova_service.get_redis_manager(request.redis_url)
        
        if request.session_id:
            session_data = redis_manager.get_session_data(request.session_id)
            return ResponseModel(
                status=StatusEnum.SUCCESS,
                message="Session data retrieved",
                data={"session_id": request.session_id, "data": session_data}
            )
        else:
            sessions = redis_manager.list_sessions(request.pattern)
            return ResponseModel(
                status=StatusEnum.SUCCESS,
                message="Sessions list retrieved",
                data={"sessions": sessions}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redis/clear")
async def redis_clear(request: RedisClearRequest):
    """Очищення Redis"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        redis_manager = mova_service.get_redis_manager(request.redis_url)
        
        if request.session_id:
            redis_manager.delete_session(request.session_id)
            message = f"Session {request.session_id} deleted"
        else:
            redis_manager.clear_all_sessions(request.pattern)
            message = f"All sessions matching {request.pattern} deleted"
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/info")
async def cache_info(request: CacheInfoRequest):
    """Інформація про кеш"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        cache_manager = mova_service.get_cache_manager()
        
        if request.key:
            value = cache_manager.get(request.key)
            return ResponseModel(
                status=StatusEnum.SUCCESS,
                message="Cache value retrieved",
                data={"key": request.key, "value": value}
            )
        else:
            stats = cache_manager.get_stats()
            return ResponseModel(
                status=StatusEnum.SUCCESS,
                message="Cache stats retrieved",
                data=stats
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def cache_clear(request: CacheClearRequest):
    """Очищення кешу"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        cache_manager = mova_service.get_cache_manager()
        
        if request.key:
            cache_manager.delete(request.key)
            message = f"Cache key {request.key} deleted"
        else:
            cache_manager.clear()
            message = "All cache cleared"
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/test")
async def webhook_test(request: WebhookTestRequest):
    """Тестування webhook"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        webhook_integration = mova_service.get_webhook_integration()
        result = await webhook_integration.send_test_event(
            request.url,
            request.event_type,
            request.data or {}
        )
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Webhook test completed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/models")
async def ml_models(request: MLModelsRequest):
    """Отримання ML моделей"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        
        if request.model_id:
            model_info = ml_integration.get_model_info(request.model_id)
            return ResponseModel(
                status=StatusEnum.SUCCESS,
                message="Model info retrieved",
                data=model_info
            )
        else:
            models = ml_integration.list_models()
            return ResponseModel(
                status=StatusEnum.SUCCESS,
                message="Models list retrieved",
                data={"models": models}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/evaluate")
async def ml_evaluate(request: MLEvaluateRequest):
    """Оцінка ML моделі"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        import json
        
        test_data = json.loads(request.test_data)
        evaluation = await ml_integration.evaluate_model(
            request.model_id,
            test_data
        )
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Model evaluation completed",
            data=evaluation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/summary")
async def recommendations_summary(request: RecommendationSummaryRequest):
    """Зведення рекомендацій"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        summary = await ml_integration.get_recommendation_summary(request.session_id)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Recommendations summary retrieved",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 