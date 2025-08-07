# 🧠 ML Integration для MOVA SDK

## Обзор

ML Integration додає можливості машинного навчання в MOVA SDK для автоматичного розпізнавання намірів, витягу сутностей та розуміння контексту користувацьких запитів.

## Можливості

### 🎯 Розпізнавання намірів (Intent Recognition)
- Автоматична класифікація користувацьких запитів
- Підтримка BERT/RoBERTa моделей
- Confidence scoring для прийняття рішень
- Fallback до правил при низькій впевненості

### 🏷️ Витяг сутностей (Entity Extraction)
- Named Entity Recognition (NER)
- Підтримка користувацьких сутностей
- Entity linking для зв'язування з зовнішніми даними
- Витяг email, телефонів, імен, організацій

### 🔄 Аналіз контексту (Context Analysis)
- Аналіз історії розмови
- Навчання профілю користувача
- Контекстне збагачення запитів
- Управління сесіями

### 😊 Аналіз настроєнь (Sentiment Analysis)
- Визначення емоційного забарвлення тексту
- Підтримка позитивних, негативних та нейтральних настроєнь
- Confidence scoring для кожного типу настроєнь

### 🤖 AI-рекомендації (AI-powered Recommendations)
- Автоматичні пропозиції для покращення конфігурації
- Аналіз продуктивності та рекомендації оптимізації
- Розумний аналіз помилок з пропозиціями вирішення
- Покращення якості коду та найкращі практики

## Швидкий старт

### Встановлення

```bash
# Встановлення залежностей
pip install -r requirements.txt

# Встановлення spaCy моделі (опціонально)
python -m spacy download uk_core_news_sm
```

### Базове використання

```python
import asyncio
from mova.ml.integration import MLIntegration

async def main():
    # Ініціалізація ML інтеграції
    ml_integration = MLIntegration()
    
    # Комплексний аналіз тексту
    text = "Зареєструй мене як користувача john@example.com"
    prediction = await ml_integration.analyze_text(text, "session_123")
    
    if prediction:
        print(f"Намір: {prediction.intent.intent.value}")
        print(f"Впевненість: {prediction.intent.confidence:.2f}")
        print(f"Сутності: {len(prediction.entities.entities)}")
        print(f"Настрої: {prediction.sentiment.sentiment.value}")
        print(f"Час обробки: {prediction.processing_time:.3f}s")

asyncio.run(main())
```

## Конфігурація

### Налаштування ML в конфігурації

```yaml
# ml_config.yaml
ml_integration:
  enabled: true
  models:
    intent_classifier:
      model_type: "bert"
      model_path: "models/intent_classifier/"
      confidence_threshold: 0.8
      fallback_to_rules: true
    
    entity_extractor:
      model_type: "spacy"
      model_path: "models/entity_extractor/"
      custom_entities: true
    
    context_analyzer:
      model_type: "transformer"
      model_path: "models/context_analyzer/"
      memory_size: 1000
  
  training:
    auto_retrain: true
    retrain_interval: "7d"
    min_samples: 1000
  
  performance:
    batch_size: 32
    max_concurrent_requests: 10
    cache_predictions: true
```

### Змінні середовища

```bash
# ML налаштування
MOVA_ML_ENABLED=true
MOVA_ML_MODELS_DIR=models
MOVA_ML_CONFIDENCE_THRESHOLD=0.8
MOVA_ML_BATCH_SIZE=32
MOVA_ML_MAX_CONCURRENT_REQUESTS=10
MOVA_ML_CACHE_PREDICTIONS=true
MOVA_ML_AUTO_RETRAIN=false
MOVA_ML_RETRAIN_INTERVAL=7d
MOVA_ML_MIN_SAMPLES=1000
```

## API Reference

### MLIntegration

Основний клас для роботи з ML функціональністю.

#### Методи

##### `analyze_text(text: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> Optional[MLPrediction]`

Комплексний аналіз тексту з розпізнаванням намірів, витягом сутностей та аналізом настроєнь.

```python
prediction = await ml_integration.analyze_text(
    "Зареєструй мене як користувача",
    session_id="user_123",
    user_id="user_456"
)
```

##### `recognize_intent(text: str, model_id: str = "intent_classifier") -> Optional[IntentResult]`

Розпізнавання наміру в тексті.

```python
intent_result = await ml_integration.recognize_intent("Увійди в систему")
```

##### `extract_entities(text: str, model_id: str = "entity_extractor") -> Optional[EntityResult]`

Витяг сутностей з тексту.

```python
entity_result = await ml_integration.extract_entities("Мій email john@example.com")
```

##### `analyze_context(session_id: str, text: str, user_id: Optional[str] = None) -> Optional[ContextResult]`

Аналіз контексту для сесії.

```python
context_result = await ml_integration.analyze_context(
    "session_123", 
    "Привіт! Мене звати Іван",
    "user_456"
)
```

##### `predict_sentiment(text: str, model_id: str = "sentiment_analyzer") -> Optional[SentimentResult]`

Передбачення настроїв тексту.

```python
sentiment_result = await ml_integration.predict_sentiment("Відмінна робота!")
```

##### `train_model(model_type: str, training_data: List[TrainingExample], config: TrainingConfig) -> Dict[str, Any]`

Навчання моделі.

```python
training_data = [
    TrainingExample(text="Зареєструй мене", intent=IntentType.USER_REGISTRATION),
    TrainingExample(text="Увійди в систему", intent=IntentType.USER_LOGIN)
]

config = TrainingConfig(
    model_type=MLModelType.BERT,
    training_data=training_data,
    epochs=10,
    learning_rate=2e-5,
    batch_size=16,
    save_path="models/intent_classifier/"
)

result = await ml_integration.train_model("intent_classifier", training_data, config)
```

##### `batch_analyze(texts: List[str], session_ids: Optional[List[str]] = None, user_ids: Optional[List[str]] = None) -> List[Optional[MLPrediction]]`

Пакетний аналіз кількох текстів.

```python
texts = ["Зареєструй мене", "Увійди в систему", "Перевір дані"]
results = await ml_integration.batch_analyze(texts)
```

##### `get_metrics_summary() -> Dict[str, Any]`

Отримання зведення метрик.

```python
metrics = await ml_integration.get_metrics_summary()
```

##### `get_system_status() -> Dict[str, Any]`

Отримання статусу системи.

```python
status = ml_integration.get_system_status()
```

#### AI-рекомендації

##### `generate_recommendations(session_id: str, **context) -> List[Recommendation]`

Генерація комплексних AI-рекомендацій на основі контексту.

```python
recommendations = await ml_integration.generate_recommendations(
    session_id="user_123",
    error_message="Connection timeout",
    performance_metrics={"avg_response_time": 3.5},
    configuration={"api": {"timeout": 15}}
)
```

##### `analyze_configuration_recommendations(config: Dict[str, Any], session_id: str) -> List[Recommendation]`

Аналіз конфігурації та генерація рекомендацій.

```python
config = {"logging": {"level": "INFO"}}  # Missing API config
recommendations = await ml_integration.analyze_configuration_recommendations(config, "session_123")
```

##### `analyze_performance_recommendations(metrics: Dict[str, Any], session_id: str) -> List[Recommendation]`

Аналіз продуктивності та генерація рекомендацій оптимізації.

```python
metrics = {"avg_response_time": 3.5, "memory_usage": 0.85}
recommendations = await ml_integration.analyze_performance_recommendations(metrics, "session_123")
```

##### `analyze_error_recommendations(error_message: str, session_id: str) -> List[Recommendation]`

Аналіз помилок та генерація рекомендацій вирішення.

```python
recommendations = await ml_integration.analyze_error_recommendations(
    "Connection timeout after 30 seconds", 
    "session_123"
)
```

##### `analyze_code_quality_recommendations(protocol_data: Dict[str, Any], session_id: str) -> List[Recommendation]`

Аналіз якості коду та генерація рекомендацій покращення.

```python
protocol_data = {"name": "test", "steps": []}  # Empty steps
recommendations = await ml_integration.analyze_code_quality_recommendations(protocol_data, "session_123")
```

##### `get_recommendation_summary() -> Dict[str, Any]`

Отримання зведення по рекомендаціях.

```python
summary = await ml_integration.get_recommendation_summary()
```

##### `export_recommendations(recommendations: List[Recommendation], file_path: str) -> bool`

Експорт рекомендацій до файлу.

```python
success = await ml_integration.export_recommendations(recommendations, "recommendations.json")
```

## Типи даних

### IntentType

Типи намірів:

- `USER_REGISTRATION` - Реєстрація користувача
- `USER_LOGIN` - Вхід в систему
- `DATA_VALIDATION` - Валідація даних
- `CONFIG_UPDATE` - Оновлення конфігурації
- `CACHE_OPERATION` - Операції з кешем
- `REDIS_OPERATION` - Операції з Redis
- `LLM_REQUEST` - Запит до LLM
- `ERROR_REPORT` - Звіт про помилку
- `HELP_REQUEST` - Запит допомоги
- `CUSTOM` - Користувацький намір

### EntityType

Типи сутностей:

- `PERSON` - Ім'я людини
- `EMAIL` - Email адреса
- `PHONE` - Номер телефону
- `ORGANIZATION` - Організація
- `LOCATION` - Місцезнаходження
- `DATE` - Дата
- `TIME` - Час
- `MONEY` - Грошова сума
- `PERCENT` - Відсоток
- `CUSTOM` - Користувацька сутність

### SentimentType

Типи настроєнь:

- `POSITIVE` - Позитивне
- `NEGATIVE` - Негативне
- `NEUTRAL` - Нейтральне
- `MIXED` - Змішане

## Приклади використання

### Розпізнавання намірів

```python
async def intent_example():
    ml_integration = MLIntegration()
    
    intent_examples = [
        "Зареєструй мене як користувача",
        "Увійди в систему з логіном admin",
        "Перевір валідність даних",
        "Онови налаштування системи",
        "Очисти кеш"
    ]
    
    for text in intent_examples:
        result = await ml_integration.recognize_intent(text)
        if result:
            print(f"'{text}' -> {result.intent.value} (впевненість: {result.confidence:.2f})")
```

### Витяг сутностей

```python
async def entity_example():
    ml_integration = MLIntegration()
    
    entity_examples = [
        "Мій email john@example.com та телефон +380 99 123 45 67",
        "Компанія ТОВ 'Технології майбутнього' знаходиться в Києві",
        "Зустріч призначена на 15.08.2024 о 14:30"
    ]
    
    for text in entity_examples:
        result = await ml_integration.extract_entities(text)
        if result and result.entities:
            print(f"'{text}' -> {len(result.entities)} сутностей")
            for entity in result.entities:
                print(f"  {entity.entity_type.value}: '{entity.text}'")
```

### Аналіз настроєнь

```python
async def sentiment_example():
    ml_integration = MLIntegration()
    
    sentiment_examples = [
        "Відмінна робота! Все працює як треба",
        "Жахлива помилка в системі, нічого не працює",
        "Система працює нормально, але є невеликі проблеми"
    ]
    
    for text in sentiment_examples:
        result = await ml_integration.predict_sentiment(text)
        if result:
            print(f"'{text}' -> {result.sentiment.value} (впевненість: {result.confidence:.2f})")
```

### Model training / Навчання моделі

```python
async def training_example():
    ml_integration = MLIntegration()
    
    # Підготовка даних
    training_data = [
        TrainingExample(text="Зареєструй мене", intent=IntentType.USER_REGISTRATION),
        TrainingExample(text="Створи акаунт", intent=IntentType.USER_REGISTRATION),
        TrainingExample(text="Увійди в систему", intent=IntentType.USER_LOGIN),
        TrainingExample(text="Авторизуйся", intent=IntentType.USER_LOGIN),
        TrainingExample(text="Перевір дані", intent=IntentType.DATA_VALIDATION)
    ]
    
    # Конфігурація навчання
    config = TrainingConfig(
        model_type=MLModelType.BERT,
        training_data=training_data,
        epochs=10,
        learning_rate=2e-5,
        batch_size=16,
        save_path="models/intent_classifier/"
    )
    
    # Навчання
    result = await ml_integration.train_model("intent_classifier", training_data, config)
    
    if result["success"]:
        print(f"Модель навчена та збережена в {result['model_path']}")
        print(f"Метрики: {result['training_metrics']}")
```

### Робота з метриками

```python
async def metrics_example():
    ml_integration = MLIntegration()
    
    # Виконуємо аналіз для накопичення метрик
    texts = ["Зареєструй мене", "Увійди в систему", "Перевір дані"]
    for text in texts:
        await ml_integration.analyze_text(text, "metrics_session")
    
    # Отримуємо зведення метрик
    metrics = await ml_integration.get_metrics_summary()
    
    if metrics["success"]:
        for metric_name, metric_data in metrics["metrics"].items():
            print(f"{metric_name}: {metric_data['current_value']:.3f}")
```

### AI-рекомендації

```python
async def recommendations_example():
    ml_integration = MLIntegration()
    
    # Аналіз конфігурації
    config = {"logging": {"level": "INFO"}}  # Missing API config
    config_recs = await ml_integration.analyze_configuration_recommendations(config, "session_123")
    
    # Аналіз продуктивності
    metrics = {"avg_response_time": 3.5, "memory_usage": 0.85}
    perf_recs = await ml_integration.analyze_performance_recommendations(metrics, "session_123")
    
    # Аналіз помилок
    error_recs = await ml_integration.analyze_error_recommendations(
        "Connection timeout after 30 seconds", 
        "session_123"
    )
    
    # Комплексний аналіз
    all_recommendations = await ml_integration.generate_recommendations(
        session_id="session_123",
        error_message="Connection timeout",
        performance_metrics=metrics,
        configuration=config
    )
    
    # Виведення результатів
    for rec in all_recommendations:
        print(f"🔍 {rec.title}")
        print(f"   Тип: {rec.type.value}")
        print(f"   Пріоритет: {rec.priority.value}")
        print(f"   Вплив: {rec.impact_score:.2f}")
        print(f"   Пропозиція: {rec.suggestion}")
        print()
    
    # Експорт рекомендацій
    await ml_integration.export_recommendations(all_recommendations, "recommendations.json")
```

## Webhook інтеграція

ML Integration автоматично відправляє webhook події для всіх операцій:

### Події ML

- `ml.intent.recognized` - Розпізнано намір
- `ml.entity.extracted` - Витягнуто сутності
- `ml.context.updated` - Оновлено контекст
- `ml.model.trained` - Навчена модель
- `ml.prediction.made` - Виконано передбачення

### Приклад webhook події

```json
{
  "event_type": "ml.intent.recognized",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "intent": "user_registration",
    "confidence": 0.95,
    "text": "Зареєструй мене як користувача",
    "session_id": "user_123",
    "processing_time": 0.15
  },
  "source": "mova_sdk",
  "version": "2.2"
}
```

## Продуктивність

### Рекомендації

1. **Кешування**: Включіть кешування передбачень для повторюваних запитів
2. **Пакетна обробка**: Використовуйте `batch_analyze` для обробки множини текстів
3. **Асинхронність**: Всі операції асинхронні, використовуйте `await`
4. **Моделі**: Завантажуйте тільки необхідні моделі для економії пам'яті

### Моніторинг

```python
# Отримання статусу системи
status = ml_integration.get_system_status()
print(f"Завантажено моделей: {status['models_loaded']}")
print(f"Активних сесій: {status['active_sessions']}")
print(f"Кількість метрик: {status['metrics_count']}")

# Експорт метрик
await ml_integration.export_metrics("metrics_export.json")
```

## Усунення неполадок

### Часті проблеми

1. **Низька точність розпізнавання**
   - Перевірте якість вхідних даних
   - Зменшіть поріг впевненості
   - Додайте більше прикладів для навчання

2. **Повільна робота**
   - Використовуйте кешування
   - Оптимізуйте розмір батчу
   - Перевірте завантаження системи

3. **Помилки завантаження моделей**
   - Перевірте шляхи до моделей
   - Переконайтеся у наявності всіх залежностей
   - Перевірте права доступу до файлів

### Логування

```python
import logging

# Налаштування логування для ML
logging.getLogger("mova.ml").setLevel(logging.DEBUG)
```

## Розширення функціональності

### Додавання користувацьких сутностей

```python
# Додавання паттерну для витягу користувацької сутності
await ml_integration.add_custom_entity_pattern(
    "CUSTOM", 
    r"\bcustom\b", 
    "entity_extractor"
)
```

### Створення користувацьких метрик

```python
from mova.ml.metrics import BaseMetric

class CustomMetric(BaseMetric):
    async def update(self, value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        await self.add_point(value, metadata)

# Додавання користувацької метрики
ml_integration.metrics.add_custom_metric("custom_metric", CustomMetric("custom_metric"))
```

## Ліцензія

ML Integration є частиною MOVA SDK та поширюється під тією ж ліцензією. 