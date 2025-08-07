"""
AI-powered recommendations and suggestions system for MOVA SDK
AI-підтримувана система рекомендацій та пропозицій для MOVA SDK

Provides intelligent suggestions for:
- Configuration optimization
- Error analysis and resolution
- Performance improvements
- Code quality enhancements
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .models import MLPrediction, IntentResult, EntityResult, SentimentResult
from .foundation import MLFoundation
from .metrics import MLMetrics


class RecommendationType(str, Enum):
    """Types of recommendations / Типи рекомендацій"""
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"
    ERROR_RESOLUTION = "error_resolution"
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    BEST_PRACTICES = "best_practices"


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations / Рівні пріоритету рекомендацій"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationCategory(str, Enum):
    """Categories of recommendations / Категорії рекомендацій"""
    OPTIMIZATION = "optimization"
    FIX = "fix"
    ENHANCEMENT = "enhancement"
    WARNING = "warning"
    INFO = "info"


@dataclass
class RecommendationContext:
    """Context for recommendation generation / Контекст для генерації рекомендацій"""
    session_id: str
    user_id: Optional[str] = None
    protocol_name: Optional[str] = None
    step_id: Optional[str] = None
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    usage_patterns: Optional[Dict[str, Any]] = None


class Recommendation(BaseModel):
    """AI-generated recommendation / AI-згенерована рекомендація"""
    id: str = Field(..., description="Unique recommendation ID / Унікальний ID рекомендації")
    type: RecommendationType = Field(..., description="Recommendation type / Тип рекомендації")
    category: RecommendationCategory = Field(..., description="Recommendation category / Категорія рекомендації")
    priority: RecommendationPriority = Field(..., description="Recommendation priority / Пріоритет рекомендації")
    title: str = Field(..., description="Recommendation title / Заголовок рекомендації")
    description: str = Field(..., description="Detailed description / Детальний опис")
    suggestion: str = Field(..., description="Specific suggestion / Конкретна пропозиція")
    code_example: Optional[str] = Field(default=None, description="Code example / Приклад коду")
    impact_score: float = Field(..., description="Impact score (0-1) / Оцінка впливу (0-1)")
    confidence: float = Field(..., description="AI confidence (0-1) / Впевненість AI (0-1)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context data / Контекстні дані")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp / Час створення")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata / Додаткові метадані")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rec_001",
                "type": "performance",
                "category": "optimization",
                "priority": "medium",
                "title": "Optimize Redis Connection Pool",
                "description": "Current Redis connection pool size may be insufficient for high load",
                "suggestion": "Increase connection_pool_size from 10 to 20",
                "code_example": '{"redis": {"connection_pool_size": 20}}',
                "impact_score": 0.75,
                "confidence": 0.85
            }
        }


class RecommendationEngine:
    """AI-powered recommendation engine / AI-підтримуваний двигун рекомендацій"""
    
    def __init__(self, ml_foundation: Optional[MLFoundation] = None):
        """Initialize recommendation engine / Ініціалізувати двигун рекомендацій"""
        self.ml_foundation = ml_foundation or MLFoundation()
        self.metrics = MLMetrics()
        self.logger = logging.getLogger(__name__)
        
        # Recommendation patterns and rules
        self.performance_patterns = {
            "slow_response": {
                "threshold": 2.0,
                "suggestions": [
                    "Enable caching for frequently accessed data",
                    "Optimize database queries",
                    "Increase connection pool size",
                    "Use async operations where possible"
                ]
            },
            "high_memory_usage": {
                "threshold": 0.8,
                "suggestions": [
                    "Implement memory cleanup",
                    "Reduce batch sizes",
                    "Optimize data structures",
                    "Use streaming for large datasets"
                ]
            }
        }
        
        self.error_patterns = {
            "connection_timeout": {
                "suggestions": [
                    "Increase timeout values",
                    "Implement retry mechanism",
                    "Check network connectivity",
                    "Use connection pooling"
                ]
            },
            "validation_error": {
                "suggestions": [
                    "Review input data format",
                    "Update validation rules",
                    "Add data sanitization",
                    "Implement better error handling"
                ]
            }
        }
        
        self.configuration_patterns = {
            "missing_required_fields": {
                "suggestions": [
                    "Add required configuration fields",
                    "Set default values",
                    "Implement configuration validation",
                    "Use configuration templates"
                ]
            },
            "suboptimal_settings": {
                "suggestions": [
                    "Optimize performance settings",
                    "Adjust security parameters",
                    "Configure logging levels",
                    "Set appropriate timeouts"
                ]
            }
        }

    async def analyze_configuration(self, config: Dict[str, Any], context: RecommendationContext) -> List[Recommendation]:
        """Analyze configuration and provide recommendations / Аналізувати конфігурацію та надати рекомендації"""
        recommendations = []
        
        try:
            # Check for missing required fields
            if "api" not in config:
                recommendations.append(Recommendation(
                    id=f"config_{context.session_id}_001",
                    type=RecommendationType.CONFIGURATION,
                    category=RecommendationCategory.FIX,
                    priority=RecommendationPriority.HIGH,
                    title="Missing API Configuration",
                    description="API configuration section is missing from the configuration file",
                    suggestion="Add API configuration section with timeout, retries, and rate limiting settings",
                    code_example=json.dumps({
                        "api": {
                            "timeout": 30,
                            "retries": 3,
                            "rate_limit": 100,
                            "base_url": "https://api.example.com"
                        }
                    }, indent=2),
                    impact_score=0.8,
                    confidence=0.9
                ))
            
            # Check performance settings
            if "performance" in config:
                perf_config = config["performance"]
                if perf_config.get("max_concurrent_requests", 0) < 10:
                    recommendations.append(Recommendation(
                        id=f"config_{context.session_id}_002",
                        type=RecommendationType.PERFORMANCE,
                        category=RecommendationCategory.OPTIMIZATION,
                        priority=RecommendationPriority.MEDIUM,
                        title="Low Concurrent Request Limit",
                        description=f"Current max_concurrent_requests is {perf_config.get('max_concurrent_requests', 0)}, which may limit performance",
                        suggestion="Increase max_concurrent_requests to at least 20 for better throughput",
                        code_example=json.dumps({"performance": {"max_concurrent_requests": 20}}, indent=2),
                        impact_score=0.6,
                        confidence=0.85
                    ))
            
            # Check security settings
            if "security" in config:
                sec_config = config["security"]
                if not sec_config.get("encryption_enabled", False):
                    recommendations.append(Recommendation(
                        id=f"config_{context.session_id}_003",
                        type=RecommendationType.SECURITY,
                        category=RecommendationCategory.ENHANCEMENT,
                        priority=RecommendationPriority.HIGH,
                        title="Encryption Not Enabled",
                        description="Data encryption is not enabled, which may pose security risks",
                        suggestion="Enable encryption for sensitive data transmission and storage",
                        code_example=json.dumps({
                            "security": {
                                "encryption_enabled": True,
                                "encryption_key": "your-secure-key-here"
                            }
                        }, indent=2),
                        impact_score=0.9,
                        confidence=0.95
                    ))
            
            # Check logging configuration
            if "logging" not in config:
                recommendations.append(Recommendation(
                    id=f"config_{context.session_id}_004",
                    type=RecommendationType.BEST_PRACTICES,
                    category=RecommendationCategory.ENHANCEMENT,
                    priority=RecommendationPriority.MEDIUM,
                    title="Missing Logging Configuration",
                    description="No logging configuration found, which may make debugging difficult",
                    suggestion="Add comprehensive logging configuration for better monitoring and debugging",
                    code_example=json.dumps({
                        "logging": {
                            "level": "INFO",
                            "file": "logs/mova.log",
                            "format": "{time} | {level} | {message}"
                        }
                    }, indent=2),
                    impact_score=0.5,
                    confidence=0.8
                ))
                
        except Exception as e:
            self.logger.error(f"Error analyzing configuration: {e}")
            
        return recommendations

    async def analyze_performance(self, metrics: Dict[str, Any], context: RecommendationContext) -> List[Recommendation]:
        """Analyze performance metrics and provide recommendations / Аналізувати метрики продуктивності та надати рекомендації"""
        recommendations = []
        
        try:
            # Analyze response times
            avg_response_time = metrics.get("avg_response_time", 0)
            if avg_response_time > self.performance_patterns["slow_response"]["threshold"]:
                recommendations.append(Recommendation(
                    id=f"perf_{context.session_id}_001",
                    type=RecommendationType.PERFORMANCE,
                    category=RecommendationCategory.OPTIMIZATION,
                    priority=RecommendationPriority.HIGH,
                    title="Slow Response Times Detected",
                    description=f"Average response time is {avg_response_time:.2f}s, which exceeds the recommended threshold",
                    suggestion="Implement caching, optimize database queries, and use async operations",
                    impact_score=0.8,
                    confidence=0.85,
                    context={"current_avg_response_time": avg_response_time}
                ))
            
            # Analyze memory usage
            memory_usage = metrics.get("memory_usage", 0)
            if memory_usage > self.performance_patterns["high_memory_usage"]["threshold"]:
                recommendations.append(Recommendation(
                    id=f"perf_{context.session_id}_002",
                    type=RecommendationType.PERFORMANCE,
                    category=RecommendationCategory.OPTIMIZATION,
                    priority=RecommendationPriority.MEDIUM,
                    title="High Memory Usage",
                    description=f"Memory usage is {memory_usage:.1%}, which may cause performance issues",
                    suggestion="Implement memory cleanup, reduce batch sizes, and optimize data structures",
                    impact_score=0.7,
                    confidence=0.8,
                    context={"current_memory_usage": memory_usage}
                ))
            
            # Analyze error rates
            error_rate = metrics.get("error_rate", 0)
            if error_rate > 0.05:  # 5% error rate threshold
                recommendations.append(Recommendation(
                    id=f"perf_{context.session_id}_003",
                    type=RecommendationType.ERROR_RESOLUTION,
                    category=RecommendationCategory.FIX,
                    priority=RecommendationPriority.CRITICAL,
                    title="High Error Rate",
                    description=f"Error rate is {error_rate:.1%}, which indicates system issues",
                    suggestion="Review error logs, implement better error handling, and add monitoring",
                    impact_score=0.9,
                    confidence=0.9,
                    context={"current_error_rate": error_rate}
                ))
                
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            
        return recommendations

    async def analyze_errors(self, error_message: str, context: RecommendationContext) -> List[Recommendation]:
        """Analyze error messages and provide resolution suggestions / Аналізувати повідомлення про помилки та надати пропозиції вирішення"""
        recommendations = []
        
        try:
            error_lower = error_message.lower()
            
            # Check for connection timeout errors
            if "timeout" in error_lower or "connection" in error_lower:
                recommendations.append(Recommendation(
                    id=f"error_{context.session_id}_001",
                    type=RecommendationType.ERROR_RESOLUTION,
                    category=RecommendationCategory.FIX,
                    priority=RecommendationPriority.HIGH,
                    title="Connection Timeout Error",
                    description=f"Connection timeout detected: {error_message}",
                    suggestion="Increase timeout values, implement retry mechanism, and check network connectivity",
                    code_example=json.dumps({
                        "api": {
                            "timeout": 60,
                            "retries": 5,
                            "retry_delay": 1
                        }
                    }, indent=2),
                    impact_score=0.8,
                    confidence=0.85,
                    context={"error_message": error_message}
                ))
            
            # Check for validation errors
            if "validation" in error_lower or "invalid" in error_lower:
                recommendations.append(Recommendation(
                    id=f"error_{context.session_id}_002",
                    type=RecommendationType.ERROR_RESOLUTION,
                    category=RecommendationCategory.FIX,
                    priority=RecommendationPriority.MEDIUM,
                    title="Validation Error",
                    description=f"Data validation failed: {error_message}",
                    suggestion="Review input data format, update validation rules, and add data sanitization",
                    impact_score=0.6,
                    confidence=0.8,
                    context={"error_message": error_message}
                ))
            
            # Check for authentication errors
            if "auth" in error_lower or "unauthorized" in error_lower:
                recommendations.append(Recommendation(
                    id=f"error_{context.session_id}_003",
                    type=RecommendationType.SECURITY,
                    category=RecommendationCategory.FIX,
                    priority=RecommendationPriority.CRITICAL,
                    title="Authentication Error",
                    description=f"Authentication failed: {error_message}",
                    suggestion="Check API keys, verify credentials, and ensure proper authentication setup",
                    impact_score=0.9,
                    confidence=0.9,
                    context={"error_message": error_message}
                ))
            
            # Check for rate limiting errors
            if "rate limit" in error_lower or "too many requests" in error_lower:
                recommendations.append(Recommendation(
                    id=f"error_{context.session_id}_004",
                    type=RecommendationType.PERFORMANCE,
                    category=RecommendationCategory.OPTIMIZATION,
                    priority=RecommendationPriority.MEDIUM,
                    title="Rate Limiting Error",
                    description=f"Rate limit exceeded: {error_message}",
                    suggestion="Implement request throttling, increase rate limits, and add request queuing",
                    code_example=json.dumps({
                        "api": {
                            "rate_limit": 200,
                            "rate_limit_window": 60,
                            "request_queue_size": 100
                        }
                    }, indent=2),
                    impact_score=0.7,
                    confidence=0.85,
                    context={"error_message": error_message}
                ))
                
        except Exception as e:
            self.logger.error(f"Error analyzing errors: {e}")
            
        return recommendations

    async def analyze_code_quality(self, protocol_data: Dict[str, Any], context: RecommendationContext) -> List[Recommendation]:
        """Analyze code quality and provide improvement suggestions / Аналізувати якість коду та надати пропозиції покращення"""
        recommendations = []
        
        try:
            # Check protocol structure
            if "steps" not in protocol_data or not protocol_data["steps"]:
                recommendations.append(Recommendation(
                    id=f"quality_{context.session_id}_001",
                    type=RecommendationType.CODE_QUALITY,
                    category=RecommendationCategory.FIX,
                    priority=RecommendationPriority.HIGH,
                    title="Empty Protocol Steps",
                    description="Protocol has no steps defined, which will cause execution failures",
                    suggestion="Add at least one step to the protocol with proper action and parameters",
                    code_example=json.dumps({
                        "steps": [
                            {
                                "id": "step_1",
                                "action": "prompt",
                                "prompt": "Hello! How can I help you?"
                            }
                        ]
                    }, indent=2),
                    impact_score=0.9,
                    confidence=0.95
                ))
            
            # Check for proper error handling
            has_error_handling = False
            if "steps" in protocol_data:
                for step in protocol_data["steps"]:
                    if "error_handler" in step or "fallback" in step:
                        has_error_handling = True
                        break
            
            if not has_error_handling:
                recommendations.append(Recommendation(
                    id=f"quality_{context.session_id}_002",
                    type=RecommendationType.CODE_QUALITY,
                    category=RecommendationCategory.ENHANCEMENT,
                    priority=RecommendationPriority.MEDIUM,
                    title="Missing Error Handling",
                    description="Protocol lacks error handling, which may cause unexpected failures",
                    suggestion="Add error handlers and fallback mechanisms to protocol steps",
                    code_example=json.dumps({
                        "steps": [
                            {
                                "id": "step_1",
                                "action": "api_call",
                                "endpoint": "https://api.example.com",
                                "error_handler": {
                                    "action": "prompt",
                                    "prompt": "Sorry, there was an error. Please try again."
                                }
                            }
                        ]
                    }, indent=2),
                    impact_score=0.7,
                    confidence=0.8
                ))
            
            # Check for proper documentation
            if "description" not in protocol_data or not protocol_data["description"]:
                recommendations.append(Recommendation(
                    id=f"quality_{context.session_id}_003",
                    type=RecommendationType.BEST_PRACTICES,
                    category=RecommendationCategory.ENHANCEMENT,
                    priority=RecommendationPriority.LOW,
                    title="Missing Protocol Description",
                    description="Protocol lacks description, which makes maintenance difficult",
                    suggestion="Add a clear description explaining the protocol's purpose and functionality",
                    code_example=json.dumps({
                        "name": "example_protocol",
                        "description": "This protocol handles user registration and validation",
                        "steps": []
                    }, indent=2),
                    impact_score=0.3,
                    confidence=0.9
                ))
                
        except Exception as e:
            self.logger.error(f"Error analyzing code quality: {e}")
            
        return recommendations

    async def generate_recommendations(self, context: RecommendationContext) -> List[Recommendation]:
        """Generate comprehensive recommendations based on context / Генерувати комплексні рекомендації на основі контексту"""
        all_recommendations = []
        
        try:
            # Analyze configuration if provided
            if context.configuration:
                config_recs = await self.analyze_configuration(context.configuration, context)
                all_recommendations.extend(config_recs)
            
            # Analyze performance metrics if provided
            if context.performance_metrics:
                perf_recs = await self.analyze_performance(context.performance_metrics, context)
                all_recommendations.extend(perf_recs)
            
            # Analyze errors if provided
            if context.error_message:
                error_recs = await self.analyze_errors(context.error_message, context)
                all_recommendations.extend(error_recs)
            
            # Use ML to enhance recommendations
            if self.ml_foundation:
                ml_recs = await self._generate_ml_recommendations(context)
                all_recommendations.extend(ml_recs)
            
            # Sort recommendations by priority and impact
            all_recommendations.sort(
                key=lambda x: (
                    {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.priority.value],
                    x.impact_score
                ),
                reverse=True
            )
            
            # Update metrics
            await self.metrics.update_recommendation_metrics(len(all_recommendations))
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            
        return all_recommendations

    async def _generate_ml_recommendations(self, context: RecommendationContext) -> List[Recommendation]:
        """Generate ML-powered recommendations / Генерувати ML-підтримувані рекомендації"""
        recommendations = []
        
        try:
            # Analyze usage patterns
            if context.usage_patterns:
                # Use ML to identify patterns and suggest optimizations
                pattern_analysis = self._analyze_usage_patterns(context.usage_patterns)
                
                if pattern_analysis.get("inefficient_patterns"):
                    recommendations.append(Recommendation(
                        id=f"ml_{context.session_id}_001",
                        type=RecommendationType.PERFORMANCE,
                        category=RecommendationCategory.OPTIMIZATION,
                        priority=RecommendationPriority.MEDIUM,
                        title="Inefficient Usage Pattern Detected",
                        description="ML analysis detected inefficient usage patterns that can be optimized",
                        suggestion="Consider implementing caching, batching, or parallel processing based on usage patterns",
                        impact_score=0.6,
                        confidence=0.75,
                        context={"pattern_analysis": pattern_analysis}
                    ))
            
            # Analyze error patterns
            if context.error_message:
                error_analysis = self._analyze_error_patterns(context.error_message)
                
                if error_analysis.get("common_cause"):
                    recommendations.append(Recommendation(
                        id=f"ml_{context.session_id}_002",
                        type=RecommendationType.ERROR_RESOLUTION,
                        category=RecommendationCategory.FIX,
                        priority=RecommendationPriority.HIGH,
                        title="Common Error Pattern Identified",
                        description=f"ML analysis identified a common cause for this error: {error_analysis['common_cause']}",
                        suggestion=error_analysis.get("suggested_fix", "Implement the suggested fix based on error pattern analysis"),
                        impact_score=0.8,
                        confidence=error_analysis.get("confidence", 0.7),
                        context={"error_analysis": error_analysis}
                    ))
                    
        except Exception as e:
            self.logger.error(f"Error generating ML recommendations: {e}")
            
        return recommendations

    def _analyze_usage_patterns(self, usage_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze usage patterns for optimization opportunities / Аналізувати патерни використання для можливостей оптимізації"""
        analysis = {
            "inefficient_patterns": [],
            "optimization_opportunities": [],
            "confidence": 0.7
        }
        
        # Check for high frequency requests
        if usage_patterns.get("high_frequency_requests", False):
            analysis["inefficient_patterns"].append("high_frequency_requests")
            analysis["optimization_opportunities"].append("Implement request batching")
        
        # Check for large data sets
        if usage_patterns.get("large_data_sets", False):
            analysis["inefficient_patterns"].append("large_data_sets")
            analysis["optimization_opportunities"].append("Use streaming and pagination")
        
        return analysis

    def _analyze_error_patterns(self, error_message: str) -> Dict[str, Any]:
        """Analyze error patterns for common causes / Аналізувати патерни помилок для поширених причин"""
        analysis = {
            "common_cause": None,
            "suggested_fix": None,
            "confidence": 0.6
        }
        
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            analysis["common_cause"] = "Network or service timeout"
            analysis["suggested_fix"] = "Increase timeout values and implement retry logic"
            analysis["confidence"] = 0.8
        elif "authentication" in error_lower or "auth" in error_lower:
            analysis["common_cause"] = "Authentication failure"
            analysis["suggested_fix"] = "Check API keys and authentication configuration"
            analysis["confidence"] = 0.9
        elif "validation" in error_lower:
            analysis["common_cause"] = "Data validation failure"
            analysis["suggested_fix"] = "Review input data format and validation rules"
            analysis["confidence"] = 0.7
        elif "rate limit" in error_lower:
            analysis["common_cause"] = "Rate limiting exceeded"
            analysis["suggested_fix"] = "Implement request throttling and rate limit handling"
            analysis["confidence"] = 0.8
        
        return analysis

    async def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get summary of recommendation statistics / Отримати зведення статистики рекомендацій"""
        try:
            metrics = await self.metrics.get_metrics_summary()
            
            return {
                "total_recommendations": metrics.get("recommendations_generated", 0),
                "recommendation_types": {
                    "configuration": metrics.get("config_recommendations", 0),
                    "performance": metrics.get("perf_recommendations", 0),
                    "error_resolution": metrics.get("error_recommendations", 0),
                    "code_quality": metrics.get("quality_recommendations", 0)
                },
                "priority_distribution": {
                    "critical": metrics.get("critical_recommendations", 0),
                    "high": metrics.get("high_recommendations", 0),
                    "medium": metrics.get("medium_recommendations", 0),
                    "low": metrics.get("low_recommendations", 0)
                },
                "average_impact_score": metrics.get("avg_impact_score", 0.0),
                "average_confidence": metrics.get("avg_confidence", 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting recommendation summary: {e}")
            return {}

    async def export_recommendations(self, recommendations: List[Recommendation], file_path: str) -> bool:
        """Export recommendations to file / Експортувати рекомендації до файлу"""
        try:
            data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_recommendations": len(recommendations),
                "recommendations": [rec.dict() for rec in recommendations]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Exported {len(recommendations)} recommendations to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting recommendations: {e}")
            return False 