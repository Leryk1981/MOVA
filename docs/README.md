# MOVA Documentation / Документація MOVA

[English](#english) | [Українська](#ukrainian)

## Документація

- [Основна документація](README.md) - Загальний огляд та використання
- [Процес розробки](DEVELOPMENT_PROCESS.md) - Хронологія та принципи розробки
- [Функції MOVA 2.2](MOVA_2.2_FEATURES.md) - Нові можливості та покращення
- [Інтеграція з Redis](REDIS_INTEGRATION.md) - Детальна інформація про Redis

## English

### Overview

MOVA (Machine-Operable Verbal Actions) is a declarative language designed for interaction with Large Language Models (LLM). It provides a structured approach to managing conversations, automating business processes, and integrating AI capabilities into applications.

### Architecture

The MOVA language consists of several core components:

1. **Intents** - User intention classification
2. **Protocols** - Multi-step conversation flows
3. **Tools** - API integrations and external services
4. **Instructions** - Documentation and guidance
5. **Profiles** - User preferences and settings
6. **Sessions** - Conversation state management
7. **Contracts** - Business logic and agreements

### Language Structure

#### Intent Definition

```json
{
  "name": "greeting",
  "patterns": ["hello", "hi", "привіт"],
  "priority": 1,
  "intent_type": "greeting",
  "response_template": "Hello! How can I help you?"
}
```

#### Protocol Definition

```json
{
  "name": "weather_protocol",
  "description": "Protocol for getting weather information",
  "steps": [
    {
      "id": "ask_city",
      "action": "prompt",
      "prompt": "In which city do you want to know the weather?"
    },
    {
      "id": "call_weather_api",
      "action": "tool_api",
      "tool_api_id": "weather_service"
    },
    {
      "id": "end",
      "action": "end"
    }
  ]
}
```

#### Tool Definition

```json
{
  "id": "weather_service",
  "name": "Weather API",
  "endpoint": "https://api.weatherapi.com/v1/current.json",
  "method": "GET",
  "parameters": {
    "key": "{API_KEY}",
    "q": "{city}"
  }
}
```

### Usage Examples

#### Basic Usage

```bash
# Validate a MOVA file
mova validate examples/basic_example.json

# Parse and display MOVA file contents
mova parse examples/basic_example.json

# Run a MOVA file
mova run examples/basic_example.json

# Initialize a new MOVA project
mova init
```

#### Python API

```python
from mova.core.engine import MovaEngine
from mova.parser.json_parser import MovaJsonParser

# Initialize engine
engine = MovaEngine()

# Parse MOVA file
parser = MovaJsonParser()
data = parser.parse_file("example.json")

# Create session
session = engine.create_session("user123")

# Execute protocol
result = engine.execute_protocol("weather_protocol", session.session_id)
```

### Development

#### Project Structure

```
MOVA/
├── src/mova/           # Source code
│   ├── core/          # Core language components
│   ├── parser/        # JSON/YAML parsers
│   ├── validator/     # Schema validation
│   └── cli/          # Command line interface
├── examples/          # Usage examples
├── tests/            # Test suite
├── docs/             # Documentation
└── schemas/          # JSON schemas
```

#### Running Tests

```bash
pytest
```

#### Building Documentation

```bash
cd docs
make html
```

## Ukrainian

### Огляд

MOVA (Machine-Operable Verbal Actions) - це декларативна мова, розроблена для взаємодії з великими мовними моделями (LLM). Вона забезпечує структурований підхід до управління діалогами, автоматизації бізнес-процесів та інтеграції можливостей ШІ в додатки.

### Архітектура

Мова MOVA складається з кількох основних компонентів:

1. **Наміри (Intents)** - Класифікація намірів користувача
2. **Протоколи (Protocols)** - Багатоетапні потоки діалогів
3. **Інструменти (Tools)** - Інтеграції API та зовнішні сервіси
4. **Інструкції (Instructions)** - Документація та керівництво
5. **Профілі (Profiles)** - Налаштування та уподобання користувача
6. **Сесії (Sessions)** - Управління станом діалогу
7. **Контракти (Contracts)** - Бізнес-логіка та угоди

### Структура мови

#### Визначення наміру

```json
{
  "name": "greeting",
  "patterns": ["hello", "hi", "привіт"],
  "priority": 1,
  "intent_type": "greeting",
  "response_template": "Привіт! Як я можу вам допомогти?"
}
```

#### Визначення протоколу

```json
{
  "name": "weather_protocol",
  "description": "Протокол для отримання інформації про погоду",
  "steps": [
    {
      "id": "ask_city",
      "action": "prompt",
      "prompt": "В якому місті ви хочете дізнатися погоду?"
    },
    {
      "id": "call_weather_api",
      "action": "tool_api",
      "tool_api_id": "weather_service"
    },
    {
      "id": "end",
      "action": "end"
    }
  ]
}
```

#### Визначення інструменту

```json
{
  "id": "weather_service",
  "name": "Weather API",
  "endpoint": "https://api.weatherapi.com/v1/current.json",
  "method": "GET",
  "parameters": {
    "key": "{API_KEY}",
    "q": "{city}"
  }
}
```

### Приклади використання

#### Базове використання

```bash
# Валідувати MOVA файл
mova validate examples/basic_example.json

# Розширена валідація з детальним звітом
mova validate examples/basic_example.json --advanced --detailed

# Парсити та відобразити вміст MOVA файлу
mova parse examples/basic_example.json

# Парсити з валідацією
mova parse examples/basic_example.json --validate

# Запустити MOVA файл
mova run examples/basic_example.json

# Запустити з покроковим виконанням
mova run examples/basic_example.json --step-by-step

# Тестувати компоненти
mova test examples/basic_example.json

# Тестувати конкретний крок
mova test examples/basic_example.json --step-id ask_city

# Ініціалізувати новий проект MOVA
mova init
```

#### Python API

```python
from mova.core.engine import MovaEngine
from mova.parser.json_parser import MovaJsonParser
from mova.validator.advanced_validator import MovaAdvancedValidator

# Ініціалізація движка
engine = MovaEngine()

# Парсинг MOVA файлу
parser = MovaJsonParser()
data = parser.parse_file("example.json")

# Розширена валідація
validator = MovaAdvancedValidator()
validator.validate_mova_structure(data)
validator.validate_unique_ids(data)
validator.validate_references(data)
validator.validate_step_consistency(data)
validator.validate_api_endpoints(data)

# Отримання звіту валідації
report = validator.generate_validation_report()
print(f"Валідація пройшла: {validator.is_valid}")
print(f"Помилки: {len(validator.errors)}")
print(f"Попередження: {len(validator.warnings)}")

# Створення сесії
session = engine.create_session("user123")

# Виконання протоколу
result = engine.execute_protocol("weather_protocol", session.session_id)
```

### Розширена валідація

MOVA 2.2 включає розширену систему валідації, яка перевіряє:

#### Перевірка структури
- Валідація версії та обов'язкових розділів
- Перевірка наявності всіх необхідних полів
- Валідація формату даних

#### Перевірка унікальності
- Унікальність ID для всіх компонентів
- Відсутність дублікатів намірів, протоколів, інструментів
- Унікальність кроків у протоколах

#### Перевірка посилань
- Валідація посилань між компонентами
- Перевірка існування API ендпоінтів
- Валідація змінних та плейсхолдерів

#### Перевірка консистентності
- Валідація послідовності кроків
- Перевірка циклічних залежностей
- Валідація умов та переходів

#### Звіт валідації
```python
# Отримання детального звіту
report = validator.generate_validation_report()

# Статистика валідації
print(f"Перевірено намірів: {report['stats']['intents']}")
print(f"Перевірено протоколів: {report['stats']['protocols']}")
print(f"Перевірено інструментів: {report['stats']['tools']}")
print(f"Знайдено дублікатів: {report['stats']['duplicates']}")

# Рекомендації щодо покращення
for recommendation in report['recommendations']:
    print(f"💡 {recommendation}")
```

### Розробка

#### Структура проекту

```
MOVA/
├── src/mova/           # Вихідний код
│   ├── core/          # Основні компоненти мови
│   ├── parser/        # JSON/YAML парсери
│   ├── validator/     # Валідація схем
│   │   ├── schema_validator.py    # Базова валідація схем
│   │   └── advanced_validator.py  # Розширена валідація
│   ├── cli/          # Інтерфейс командного рядка
│   ├── redis_manager.py  # Управління Redis
│   └── llm_client.py     # Клієнт для LLM
├── examples/          # Приклади використання
├── tests/            # Набір тестів
├── docs/             # Документація
└── schemas/          # JSON схеми
```

#### CLI Команди

MOVA 2.2 надає розширений набір CLI команд:

**Основні команди:**
- `mova parse` - Парсинг та відображення MOVA файлів
- `mova validate` - Валідація схеми та структури
- `mova run` - Запуск протоколів
- `mova test` - Тестування компонентів
- `mova init` - Ініціалізація нового проекту

**Розширені опції:**
- `--advanced` - Використання розширеної валідації
- `--detailed` - Детальний звіт валідації
- `--step-by-step` - Покрокове виконання
- `--verbose` - Детальний вивід
- `--dry-run` - Тестове виконання без змін

#### Запуск тестів

```bash
pytest
```

#### Інтеграція з Redis

MOVA 2.2 підтримує збереження стану в Redis:

```bash
# Запуск з Redis
mova run example.json --redis-url redis://localhost:6379

# Використання в Python
from mova.redis_manager import RedisManager

redis_manager = RedisManager("redis://localhost:6379")
session_data = redis_manager.get_session("user123")
```

#### Інтеграція з LLM

Підтримка різних LLM провайдерів:

```bash
# Використання OpenRouter
mova run example.json --llm-api-key YOUR_KEY --llm-model openai/gpt-4

# Використання OpenAI
mova run example.json --llm-api-key YOUR_KEY --llm-model gpt-3.5-turbo
```

#### Створення документації

```bash
cd docs
make html
``` 