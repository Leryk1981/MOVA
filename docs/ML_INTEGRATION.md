# 🧠 ML Integration для MOVA SDK

## Обзор

ML Integration добавляет возможности машинного обучения в MOVA SDK для автоматического распознавания намерений, извлечения сущностей и понимания контекста пользовательских запросов.

## Возможности

### 🎯 Распознавание намерений (Intent Recognition)
- Автоматическая классификация пользовательских запросов
- Поддержка BERT/RoBERTa моделей
- Confidence scoring для принятия решений
- Fallback к правилам при низкой уверенности

### 🏷️ Извлечение сущностей (Entity Extraction)
- Named Entity Recognition (NER)
- Поддержка пользовательских сущностей
- Entity linking для связывания с внешними данными
- Извлечение email, телефонов, имен, организаций

### 🔄 Анализ контекста (Context Analysis)
- Анализ истории разговора
- Обучение профиля пользователя
- Контекстное обогащение запросов
- Управление сессиями

### 😊 Анализ настроений (Sentiment Analysis)
- Определение эмоциональной окраски текста
- Поддержка позитивных, негативных и нейтральных настроений
- Confidence scoring для каждого типа настроения

## Быстрый старт

### Установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка spaCy модели (опционально)
python -m spacy download ru_core_news_sm
```

### Базовое использование

```python
import asyncio
from mova.ml.integration import MLIntegration

async def main():
    # Инициализация ML интеграции
    ml_integration = MLIntegration()
    
    # Комплексный анализ текста
    text = "Зарегистрируй меня как пользователя john@example.com"
    prediction = await ml_integration.analyze_text(text, "session_123")
    
    if prediction:
        print(f"Намерение: {prediction.intent.intent.value}")
        print(f"Уверенность: {prediction.intent.confidence:.2f}")
        print(f"Сущности: {len(prediction.entities.entities)}")
        print(f"Настроение: {prediction.sentiment.sentiment.value}")
        print(f"Время обработки: {prediction.processing_time:.3f}s")

asyncio.run(main())
```

## Конфигурация

### Настройки ML в конфигурации

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

### Переменные окружения

```bash
# ML настройки
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

Основной класс для работы с ML функциональностью.

#### Методы

##### `analyze_text(text: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> Optional[MLPrediction]`

Комплексный анализ текста с распознаванием намерений, извлечением сущностей и анализом настроений.

```python
prediction = await ml_integration.analyze_text(
    "Зарегистрируй меня как пользователя",
    session_id="user_123",
    user_id="user_456"
)
```

##### `recognize_intent(text: str, model_id: str = "intent_classifier") -> Optional[IntentResult]`

Распознавание намерения в тексте.

```python
intent_result = await ml_integration.recognize_intent("Войди в систему")
```

##### `extract_entities(text: str, model_id: str = "entity_extractor") -> Optional[EntityResult]`

Извлечение сущностей из текста.

```python
entity_result = await ml_integration.extract_entities("Мой email john@example.com")
```

##### `analyze_context(session_id: str, text: str, user_id: Optional[str] = None) -> Optional[ContextResult]`

Анализ контекста для сессии.

```python
context_result = await ml_integration.analyze_context(
    "session_123", 
    "Привет! Меня зовут Иван",
    "user_456"
)
```

##### `predict_sentiment(text: str, model_id: str = "sentiment_analyzer") -> Optional[SentimentResult]`

Предсказание настроения текста.

```python
sentiment_result = await ml_integration.predict_sentiment("Отличная работа!")
```

##### `train_model(model_type: str, training_data: List[TrainingExample], config: TrainingConfig) -> Dict[str, Any]`

Обучение модели.

```python
training_data = [
    TrainingExample(text="Зарегистрируй меня", intent=IntentType.USER_REGISTRATION),
    TrainingExample(text="Войди в систему", intent=IntentType.USER_LOGIN)
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

Пакетный анализ нескольких текстов.

```python
texts = ["Зарегистрируй меня", "Войди в систему", "Проверь данные"]
results = await ml_integration.batch_analyze(texts)
```

##### `get_metrics_summary() -> Dict[str, Any]`

Получение сводки метрик.

```python
metrics = await ml_integration.get_metrics_summary()
```

##### `get_system_status() -> Dict[str, Any]`

Получение статуса системы.

```python
status = ml_integration.get_system_status()
```

## Типы данных

### IntentType

Типы намерений:

- `USER_REGISTRATION` - Регистрация пользователя
- `USER_LOGIN` - Вход в систему
- `DATA_VALIDATION` - Валидация данных
- `CONFIG_UPDATE` - Обновление конфигурации
- `CACHE_OPERATION` - Операции с кэшем
- `REDIS_OPERATION` - Операции с Redis
- `LLM_REQUEST` - Запрос к LLM
- `ERROR_REPORT` - Отчет об ошибке
- `HELP_REQUEST` - Запрос помощи
- `CUSTOM` - Пользовательское намерение

### EntityType

Типы сущностей:

- `PERSON` - Имя человека
- `EMAIL` - Email адрес
- `PHONE` - Номер телефона
- `ORGANIZATION` - Организация
- `LOCATION` - Местоположение
- `DATE` - Дата
- `TIME` - Время
- `MONEY` - Денежная сумма
- `PERCENT` - Процент
- `CUSTOM` - Пользовательская сущность

### SentimentType

Типы настроений:

- `POSITIVE` - Позитивное
- `NEGATIVE` - Негативное
- `NEUTRAL` - Нейтральное
- `MIXED` - Смешанное

## Примеры использования

### Распознавание намерений

```python
async def intent_example():
    ml_integration = MLIntegration()
    
    intent_examples = [
        "Зарегистрируй меня как пользователя",
        "Войди в систему с логином admin",
        "Проверь валидность данных",
        "Обнови настройки системы",
        "Очисти кэш"
    ]
    
    for text in intent_examples:
        result = await ml_integration.recognize_intent(text)
        if result:
            print(f"'{text}' -> {result.intent.value} (уверенность: {result.confidence:.2f})")
```

### Извлечение сущностей

```python
async def entity_example():
    ml_integration = MLIntegration()
    
    entity_examples = [
        "Мой email john@example.com и телефон +7 999 123 45 67",
        "Компания ООО 'Технологии будущего' находится в Москве",
        "Встреча назначена на 15.08.2024 в 14:30"
    ]
    
    for text in entity_examples:
        result = await ml_integration.extract_entities(text)
        if result and result.entities:
            print(f"'{text}' -> {len(result.entities)} сущностей")
            for entity in result.entities:
                print(f"  {entity.entity_type.value}: '{entity.text}'")
```

### Анализ настроений

```python
async def sentiment_example():
    ml_integration = MLIntegration()
    
    sentiment_examples = [
        "Отличная работа! Все работает как надо",
        "Ужасная ошибка в системе, ничего не работает",
        "Система работает нормально, но есть небольшие проблемы"
    ]
    
    for text in sentiment_examples:
        result = await ml_integration.predict_sentiment(text)
        if result:
            print(f"'{text}' -> {result.sentiment.value} (уверенность: {result.confidence:.2f})")
```

### Model training / Навчання моделі

```python
async def training_example():
    ml_integration = MLIntegration()
    
    # Подготовка данных
    training_data = [
        TrainingExample(text="Зарегистрируй меня", intent=IntentType.USER_REGISTRATION),
        TrainingExample(text="Создай аккаунт", intent=IntentType.USER_REGISTRATION),
        TrainingExample(text="Войди в систему", intent=IntentType.USER_LOGIN),
        TrainingExample(text="Авторизуйся", intent=IntentType.USER_LOGIN),
        TrainingExample(text="Проверь данные", intent=IntentType.DATA_VALIDATION)
    ]
    
    # Конфигурация обучения
    config = TrainingConfig(
        model_type=MLModelType.BERT,
        training_data=training_data,
        epochs=10,
        learning_rate=2e-5,
        batch_size=16,
        save_path="models/intent_classifier/"
    )
    
    # Обучение
    result = await ml_integration.train_model("intent_classifier", training_data, config)
    
    if result["success"]:
        print(f"Модель обучена и сохранена в {result['model_path']}")
        print(f"Метрики: {result['training_metrics']}")
```

### Работа с метриками

```python
async def metrics_example():
    ml_integration = MLIntegration()
    
    # Выполняем анализ для накопления метрик
    texts = ["Зарегистрируй меня", "Войди в систему", "Проверь данные"]
    for text in texts:
        await ml_integration.analyze_text(text, "metrics_session")
    
    # Получаем сводку метрик
    metrics = await ml_integration.get_metrics_summary()
    
    if metrics["success"]:
        for metric_name, metric_data in metrics["metrics"].items():
            print(f"{metric_name}: {metric_data['current_value']:.3f}")
```

## Webhook интеграция

ML Integration автоматически отправляет webhook события для всех операций:

### События ML

- `ml.intent.recognized` - Распознано намерение
- `ml.entity.extracted` - Извлечены сущности
- `ml.context.updated` - Обновлен контекст
- `ml.model.trained` - Обучена модель
- `ml.prediction.made` - Выполнено предсказание

### Пример webhook события

```json
{
  "event_type": "ml.intent.recognized",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "intent": "user_registration",
    "confidence": 0.95,
    "text": "Зарегистрируй меня как пользователя",
    "session_id": "user_123",
    "processing_time": 0.15
  },
  "source": "mova_sdk",
  "version": "2.2"
}
```

## Производительность

### Рекомендации

1. **Кэширование**: Включите кэширование предсказаний для повторяющихся запросов
2. **Пакетная обработка**: Используйте `batch_analyze` для обработки множества текстов
3. **Асинхронность**: Все операции асинхронные, используйте `await`
4. **Модели**: Загружайте только необходимые модели для экономии памяти

### Мониторинг

```python
# Получение статуса системы
status = ml_integration.get_system_status()
print(f"Загружено моделей: {status['models_loaded']}")
print(f"Активных сессий: {status['active_sessions']}")
print(f"Количество метрик: {status['metrics_count']}")

# Экспорт метрик
await ml_integration.export_metrics("metrics_export.json")
```

## Устранение неполадок

### Частые проблемы

1. **Низкая точность распознавания**
   - Проверьте качество входных данных
   - Уменьшите порог уверенности
   - Добавьте больше примеров для обучения

2. **Медленная работа**
   - Используйте кэширование
   - Оптимизируйте размер батча
   - Проверьте загрузку системы

3. **Ошибки загрузки моделей**
   - Проверьте пути к моделям
   - Убедитесь в наличии всех зависимостей
   - Проверьте права доступа к файлам

### Логирование

```python
import logging

# Настройка логирования для ML
logging.getLogger("mova.ml").setLevel(logging.DEBUG)
```

## Расширение функциональности

### Добавление пользовательских сущностей

```python
# Добавление паттерна для извлечения пользовательской сущности
await ml_integration.add_custom_entity_pattern(
    "CUSTOM", 
    r"\bcustom\b", 
    "entity_extractor"
)
```

### Создание пользовательских метрик

```python
from mova.ml.metrics import BaseMetric

class CustomMetric(BaseMetric):
    async def update(self, value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        await self.add_point(value, metadata)

# Добавление пользовательской метрики
ml_integration.metrics.add_custom_metric("custom_metric", CustomMetric("custom_metric"))
```

## Лицензия

ML Integration является частью MOVA SDK и распространяется под той же лицензией. 