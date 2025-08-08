"""
ML API routes
API роути для ML операцій
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any

from ..models.common import ResponseModel, StatusEnum
from ..services.mova_service import mova_service

router = APIRouter()


@router.get("/status")
async def get_ml_status():
    """Отримання статусу ML системи"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        
        # Отримуємо статус ML системи
        models = ml_integration.list_models()
        active_models = [m for m in models if m.get("active", False)]
        
        status = {
            "enabled": True,
            "models_count": len(models),
            "active_models": len(active_models),
            "last_training": ml_integration.last_training_time,
            "average_accuracy": ml_integration.get_average_accuracy(),
            "models": models
        }
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="ML status retrieved",
            data=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """Отримання списку ML моделей"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        models = ml_integration.list_models()
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Models list retrieved",
            data={"models": models}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """Отримання інформації про модель"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        model_info = ml_integration.get_model_info(model_id)
        
        if model_info is None:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Model info retrieved",
            data=model_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/evaluate")
async def evaluate_model(model_id: str, test_data: Dict[str, Any]):
    """Оцінка ML моделі"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        evaluation = await ml_integration.evaluate_model(model_id, test_data)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Model evaluation completed",
            data=evaluation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/train")
async def train_model(model_id: str, training_config: Dict[str, Any]):
    """Тренування ML моделі"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        training_result = await ml_integration.train_model(model_id, training_config)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Model training completed",
            data=training_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/intent")
async def analyze_intent(text: str):
    """Аналіз наміру"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        intent_result = await ml_integration.analyze_intent(text)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Intent analysis completed",
            data=intent_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/entities")
async def extract_entities(text: str):
    """Витяг сущностей"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        entities_result = await ml_integration.extract_entities(text)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Entity extraction completed",
            data=entities_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/sentiment")
async def analyze_sentiment(text: str):
    """Аналіз настрою"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        sentiment_result = await ml_integration.analyze_sentiment(text)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Sentiment analysis completed",
            data=sentiment_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/generate")
async def generate_recommendations(
    file_path: str,
    session_id: str = "web_session"
):
    """Генерація рекомендацій"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        recommendations = await ml_integration.generate_recommendations(
            file_path, session_id
        )
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Recommendations generated",
            data=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/summary")
async def get_recommendations_summary(session_id: str = "web_session"):
    """Отримання зведення рекомендацій"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        summary = await ml_integration.get_recommendation_summary(session_id)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Recommendations summary retrieved",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/export")
async def export_recommendations(
    session_id: str = "web_session",
    format: str = "json"
):
    """Експорт рекомендацій"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        export_data = await ml_integration.export_recommendations(session_id, format)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Recommendations exported",
            data=export_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_ml_metrics():
    """Отримання ML метрик"""
    try:
        if not mova_service.is_available():
            raise HTTPException(status_code=500, detail="MOVA SDK not available")
        
        ml_integration = mova_service.get_ml_integration()
        metrics = ml_integration.get_metrics()
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="ML metrics retrieved",
            data=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 