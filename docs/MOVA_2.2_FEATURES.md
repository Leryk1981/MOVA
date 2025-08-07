# MOVA 2.2 - Нові функції та можливості

[English](#english) | [Українська](#ukrainian)

## English

### Overview

MOVA 2.2 introduces significant enhancements to the language and ecosystem, focusing on advanced validation, improved state management, and enhanced developer experience.

### Key New Features

#### 1. Async Support (asyncio)

MOVA 2.2 introduces comprehensive async support for high-performance applications:

**Async Components**
- **AsyncMovaEngine**: Asynchronous version of the main processing engine
- **AsyncMovaLLMClient**: Async LLM client with connection pooling
- **AsyncMovaHTTPClient**: Async HTTP client with aiohttp support
- **Async CLI**: Command-line interface with async operations

**Async Features**
- Concurrent protocol execution
- Async API calls with connection pooling
- Non-blocking LLM interactions
- Async session management
- Performance optimization for high-load scenarios

**Usage Example:**
```python
import asyncio
from mova.core.async_engine import create_async_mova_engine
from mova.async_llm_client import get_async_llm_client

async def main():
    # Create async engine
    engine = await create_async_mova_engine(
        redis_url="redis://localhost:6379",
        llm_api_key="your-api-key"
    )
    
    # Execute protocols concurrently
    tasks = []
    for i in range(10):
        task = engine.execute_protocol("weather_protocol", f"session_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Cleanup
    await engine.cleanup()

# Run async example
asyncio.run(main())
```

**Async CLI Usage:**
```bash
# Async validation
mova-async validate example.json --advanced

# Async execution
mova-async run example.json --step-by-step

# Async testing
mova-async test example.json --verbose
```

#### 2. Advanced Validation System

The new advanced validation system provides comprehensive checking of MOVA files:

**Structure Validation**
- Version compatibility checking
- Required sections validation
- Data format verification

**Uniqueness Validation**
- Unique ID checking for all components
- Duplicate detection across intents, protocols, and tools
- Step ID uniqueness within protocols

**Reference Validation**
- Cross-component reference verification
- API endpoint existence checking
- Variable and placeholder syntax validation

**Consistency Validation**
- Step sequence validation
- Cyclic dependency detection
- Condition and transition validation

**Usage Example:**
```bash
# Basic validation
mova validate example.json

# Advanced validation with detailed report
mova validate example.json --advanced --detailed

# Save validation report to file
mova validate example.json --advanced --output validation_report.json
```

#### 2. Redis Integration

State management and session persistence using Redis:

**Features:**
- Session state persistence
- Conversation history storage
- Cross-session data sharing
- Performance optimization

**Usage:**
```bash
# Run with Redis
mova run example.json --redis-url redis://localhost:6379

# Python API
from mova.redis_manager import RedisManager

redis_manager = RedisManager("redis://localhost:6379")
session_data = redis_manager.get_session("user123")
redis_manager.save_session("user123", session_data)
```

#### 3. LLM Client Integration

Support for multiple LLM providers:

**Supported Providers:**
- OpenAI (GPT-3.5, GPT-4)
- OpenRouter (multiple models)
- Extensible for other providers

**Features:**
- Model selection
- Temperature control
- Token limit management
- Timeout handling

**Usage:**
```bash
# OpenAI
mova run example.json --llm-api-key YOUR_KEY --llm-model gpt-4

# OpenRouter
mova run example.json --llm-api-key YOUR_KEY --llm-model openai/gpt-4

# Custom settings
mova run example.json --llm-temperature 0.8 --llm-max-tokens 2000
```

#### 4. Enhanced CLI

New CLI commands and options for better developer experience:

**New Commands:**
- `mova test` - Test components and APIs
- Enhanced `mova validate` with advanced options
- Enhanced `mova run` with step-by-step execution

**New Options:**
- `--step-by-step` - Interactive execution
- `--dry-run` - Test execution without changes
- `--verbose` - Detailed output
- `--detailed` - Comprehensive validation reports

**Usage Examples:**
```bash
# Test specific step
mova test example.json --step-id ask_city

# Test specific API
mova test example.json --api-id weather_service

# Step-by-step execution
mova run example.json --step-by-step

# Dry run test
mova test example.json --dry-run
```

#### 5. Step-by-Step Execution

Interactive protocol execution with user confirmation:

**Features:**
- Step-by-step protocol execution
- User confirmation for each step
- Detailed step information display
- Execution state visualization

**Usage:**
```bash
mova run example.json --step-by-step
```

Example output:
```
Step 1/3: ask_city
Action: prompt
Prompt: "In which city do you want to know the weather?"
Continue? [Y/n]: y

Step 2/3: call_weather_api
Action: tool_api
API: weather_service
Continue? [Y/n]: y

Step 3/3: end
Action: end
Protocol completed successfully!
```

### Technical Improvements

#### Performance Optimizations
- Caching mechanisms for repeated operations
- Optimized validation algorithms
- Efficient memory usage
- Reduced API call overhead

#### Error Handling
- Comprehensive error messages
- Graceful degradation
- Recovery mechanisms
- Detailed error reporting

#### Code Quality
- Enhanced type safety
- Improved code documentation
- Better test coverage
- Code style consistency

### Migration Guide

#### From MOVA 2.1 to 2.2

**Breaking Changes:**
- None - fully backward compatible

**New Features:**
- Advanced validation is optional and doesn't affect existing workflows
- Redis integration is optional
- LLM client supports existing configurations

**Recommended Upgrades:**
1. Update to use advanced validation for better error detection
2. Consider Redis integration for production deployments
3. Test new CLI features for improved workflow

### Future Roadmap

#### Planned Features for 2.3
- Plugin system for custom extensions
- Visual editor for protocol design
- Cloud integration for deployment
- Community tools and marketplace
- Enterprise features and support

## Ukrainian

### Огляд

MOVA 2.2 вводить значні покращення мови та екосистеми, фокусуючись на розширеній валідації, покращеному управлінні станом та покращеному досвіді розробника.

### Ключові нові функції

#### 1. Асинхронна підтримка (asyncio)

MOVA 2.2 вводить комплексну асинхронну підтримку для високопродуктивних додатків:

**Асинхронні компоненти**
- **AsyncMovaEngine**: Асинхронна версія основного обробного движка
- **AsyncMovaLLMClient**: Асинхронний LLM клієнт з пулом з'єднань
- **AsyncMovaHTTPClient**: Асинхронний HTTP клієнт з підтримкою aiohttp
- **Async CLI**: Інтерфейс командного рядка з асинхронними операціями

**Асинхронні можливості**
- Паралельне виконання протоколів
- Асинхронні виклики API з пулом з'єднань
- Неблокуючі взаємодії з LLM
- Асинхронне управління сесіями
- Оптимізація продуктивності для високонавантажених сценаріїв

**Приклад використання:**
```python
import asyncio
from mova.core.async_engine import create_async_mova_engine
from mova.async_llm_client import get_async_llm_client

async def main():
    # Створити асинхронний движок
    engine = await create_async_mova_engine(
        redis_url="redis://localhost:6379",
        llm_api_key="your-api-key"
    )
    
    # Виконати протоколи паралельно
    tasks = []
    for i in range(10):
        task = engine.execute_protocol("weather_protocol", f"session_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Очищення
    await engine.cleanup()

# Запустити асинхронний приклад
asyncio.run(main())
```

**Використання асинхронного CLI:**
```bash
# Асинхронна валідація
mova-async validate example.json --advanced

# Асинхронне виконання
mova-async run example.json --step-by-step

# Асинхронне тестування
mova-async test example.json --verbose
```

#### 2. Розширена система валідації

Нова розширена система валідації забезпечує комплексну перевірку MOVA файлів:

**Валідація структури**
- Перевірка сумісності версій
- Валідація обов'язкових розділів
- Перевірка формату даних

**Валідація унікальності**
- Перевірка унікальності ID для всіх компонентів
- Виявлення дублікатів у намірах, протоколах та інструментах
- Унікальність ID кроків у протоколах

**Валідація посилань**
- Перевірка перехресних посилань між компонентами
- Перевірка існування API ендпоінтів
- Валідація синтаксису змінних та плейсхолдерів

**Валідація консистентності**
- Валідація послідовності кроків
- Виявлення циклічних залежностей
- Валідація умов та переходів

**Приклад використання:**
```bash
# Базова валідація
mova validate example.json

# Розширена валідація з детальним звітом
mova validate example.json --advanced --detailed

# Збереження звіту валідації у файл
mova validate example.json --advanced --output validation_report.json
```

#### 2. Інтеграція з Redis

Управління станом та збереження сесій за допомогою Redis:

**Можливості:**
- Збереження стану сесій
- Зберігання історії діалогів
- Обмін даними між сесіями
- Оптимізація продуктивності

**Використання:**
```bash
# Запуск з Redis
mova run example.json --redis-url redis://localhost:6379

# Python API
from mova.redis_manager import RedisManager

redis_manager = RedisManager("redis://localhost:6379")
session_data = redis_manager.get_session("user123")
redis_manager.save_session("user123", session_data)
```

#### 3. Інтеграція клієнта LLM

Підтримка кількох провайдерів LLM:

**Підтримувані провайдери:**
- OpenAI (GPT-3.5, GPT-4)
- OpenRouter (багато моделей)
- Розширюваність для інших провайдерів

**Можливості:**
- Вибір моделі
- Контроль температури
- Управління лімітом токенів
- Обробка таймаутів

**Використання:**
```bash
# OpenAI
mova run example.json --llm-api-key YOUR_KEY --llm-model gpt-4

# OpenRouter
mova run example.json --llm-api-key YOUR_KEY --llm-model openai/gpt-4

# Користувацькі налаштування
mova run example.json --llm-temperature 0.8 --llm-max-tokens 2000
```

#### 4. Розширений CLI

Нові CLI команди та опції для кращого досвіду розробника:

**Нові команди:**
- `mova test` - Тестування компонентів та API
- Розширений `mova validate` з додатковими опціями
- Розширений `mova run` з покроковим виконанням

**Нові опції:**
- `--step-by-step` - Інтерактивне виконання
- `--dry-run` - Тестове виконання без змін
- `--verbose` - Детальний вивід
- `--detailed` - Комплексні звіти валідації

**Приклади використання:**
```bash
# Тестування конкретного кроку
mova test example.json --step-id ask_city

# Тестування конкретного API
mova test example.json --api-id weather_service

# Покрокове виконання
mova run example.json --step-by-step

# Тестове виконання
mova test example.json --dry-run
```

#### 5. Покрокове виконання

Інтерактивне виконання протоколів з підтвердженням користувача:

**Можливості:**
- Покрокове виконання протоколів
- Підтвердження користувача для кожного кроку
- Детальне відображення інформації про кроки
- Візуалізація стану виконання

**Використання:**
```bash
mova run example.json --step-by-step
```

Приклад виводу:
```
Крок 1/3: ask_city
Дія: prompt
Повідомлення: "В якому місті ви хочете дізнатися погоду?"
Продовжити? [Y/n]: y

Крок 2/3: call_weather_api
Дія: tool_api
API: weather_service
Продовжити? [Y/n]: y

Крок 3/3: end
Дія: end
Протокол успішно завершено!
```

### Технічні покращення

#### Оптимізація продуктивності
- Механізми кешування для повторних операцій
- Оптимізовані алгоритми валідації
- Ефективне використання пам'яті
- Зменшення накладних витрат API викликів

#### Обробка помилок
- Комплексні повідомлення про помилки
- Плавна деградація
- Механізми відновлення
- Детальна звітність про помилки

#### Якість коду
- Покращена типобезпека
- Покращена документація коду
- Краще покриття тестами
- Консистентність стилю коду

### Керівництво з міграції

#### Від MOVA 2.1 до 2.2

**Критичні зміни:**
- Відсутні - повна зворотна сумісність

**Нові функції:**
- Розширена валідація є опціональною і не впливає на існуючі робочі процеси
- Інтеграція з Redis є опціональною
- Клієнт LLM підтримує існуючі конфігурації

**Рекомендовані оновлення:**
1. Оновлення для використання розширеної валідації для кращого виявлення помилок
2. Розгляд інтеграції з Redis для продакшн розгортання
3. Тестування нових CLI функцій для покращеного робочого процесу

### Майбутня дорожня карта

#### Заплановані функції для 2.3
- Система плагінів для користувацьких розширень
- Візуальний редактор для проектування протоколів
- Хмарна інтеграція для розгортання
- Інструменти спільноти та маркетплейс
- Корпоративні функції та підтримка 