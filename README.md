# MOVA - Machine-Operable Verbal Actions

[English](#english) | [Українська](#ukrainian)

## English

MOVA (Machine-Operable Verbal Actions) is a declarative language designed for interaction with Large Language Models (LLM). It provides a structured approach to managing conversations, automating business processes, and integrating AI capabilities into applications.

### Key Features

- **Declarative Language**: JSON-based syntax for describing LLM interactions
- **Modular Design**: Separation of concerns into distinct classes (intent, protocol, tool_api, etc.)
- **Multi-step Scenarios**: Support for complex workflows and branching logic
- **API Integration**: Built-in support for external API calls with retry mechanisms
- **Context Management**: Advanced session and profile management
- **Redis Integration**: Scalable session storage with TTL support
- **LLM Integration**: Support for OpenAI/OpenRouter API with configurable parameters
- **Presets System**: Predefined LLM configurations for different use cases
- **Tool-Calling Support**: Advanced tool orchestration with OpenRouter integration
- **Memory System**: Context-aware memory management for conversations
- **Advanced Validation**: Comprehensive validation with detailed reports and recommendations
- **CLI Extensions**: Component testing and step-by-step execution
- **Webhook Support**: Real-time event notifications for external integrations
- **ML Integration**: Intent recognition, entity extraction, context analysis, and sentiment analysis
- **Bilingual Documentation**: Full documentation in English and Ukrainian

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Leryk1981/MOVA.git
cd MOVA

# Create virtual environment
python -m venv mova_env
mova_env\Scripts\Activate.ps1  # Windows
source mova_env/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development
python -m mova.cli

# Run with Redis (optional)
python -c "from src.mova.cli.cli import main; main()" run examples/basic_example.json --redis-url redis://localhost:6379
```

### 🤖 LLM Integration with OpenRouter

MOVA SDK 2.2 includes enhanced LLM integration with OpenRouter for accessing various AI models:

```python
import os
from src.mova.core.engine import MovaEngine

# Set your OpenRouter API key
os.environ["OPENROUTER_API_KEY"] = "your-api-key-here"

# Initialize engine with LLM support
engine = MovaEngine()

# Create protocol with LLM prompt
protocol = Protocol(
    protocol_id="ai_assistant",
    name="AI Assistant",
    steps=[
        ProtocolStep(
            id="step1",
            action=ActionType.PROMPT,
            prompt="User asked: {session.data.user_input}. Provide a helpful response."
        )
    ]
)

engine.add_protocol(protocol)

# Usage
session = engine.create_session("user123")
engine.update_session_data(session.session_id, {"user_input": "What is AI?"})
result = engine.execute_protocol("ai_assistant", session.session_id)
print(result["response"])
```

**Supported Models:**
- `openai/gpt-3.5-turbo` - Fast and cost-effective
- `openai/gpt-4` - More powerful
- `anthropic/claude-3-haiku` - Fast Claude
- `anthropic/claude-3-sonnet` - Balanced Claude
- `anthropic/claude-3-opus` - Most powerful Claude

**CLI Usage with LLM:**
```bash
# Run with LLM support
python -c "from src.mova.cli.cli import main; main()" run examples/config.json \
  --llm-api-key "your-api-key" \
  --llm-model "openai/gpt-4"
```

### ⚙️ Presets System

MOVA SDK 2.2 introduces a powerful presets system for predefined LLM configurations:

```python
from src.mova.core.engine import MovaEngine
from src.mova.config.loader import load_config

# Load configuration with presets
config = load_config("examples/config.yaml")
engine = MovaEngine(config=config)

# Use different presets for different tasks
# General conversation preset
session_general = engine.create_session("user123", preset="general")

# Creative writing preset
session_creative = engine.create_session("user123", preset="creative")

# Technical analysis preset
session_technical = engine.create_session("user123", preset="technical")
```

**Available Presets:**
- `general` - Balanced for everyday conversations
- `creative` - Enhanced for creative writing
- `technical` - Optimized for technical analysis
- `concise` - Brief and to the point responses

**Configuration Example:**
```yaml
llm:
  provider: openrouter
  api_key_env: OPENROUTER_API_KEY
  base_url: https://openrouter.ai/api/v1
  default_model: openrouter/anthropic/claude-3-haiku

presets:
  general:
    model: openrouter/anthropic/claude-3-haiku
    temperature: 0.3
    max_tokens: 1024
    system: "You are a helpful assistant."
  
  creative:
    model: openai/gpt-4
    temperature: 0.8
    max_tokens: 2048
    system: "You are a creative writing assistant."
  
  technical:
    model: anthropic/claude-3-sonnet
    temperature: 0.1
    max_tokens: 1536
    system: "You are a technical expert."
```

### 🛠️ Tool-Calling Support

MOVA SDK 2.2 includes advanced tool-calling capabilities with OpenRouter integration:

```python
from src.mova.core.engine import MovaEngine
from src.mova.core.tools.registry import ToolRegistry

# Initialize engine with tool support
engine = MovaEngine()

# Register tools
registry = ToolRegistry()

# Define a weather tool
weather_tool = {
    "name": "get_weather",
    "description": "Get current weather information for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            }
        },
        "required": ["location"]
    }
}

# Add tool to registry
registry.register_tool("get_weather", weather_tool)

# Create protocol with tool-calling
protocol = Protocol(
    protocol_id="weather_assistant",
    name="Weather Assistant",
    steps=[
        ProtocolStep(
            id="step1",
            action=ActionType.PROMPT,
            prompt="What's the weather like in {session.data.location}?",
            tools=["get_weather"]
        )
    ]
)

engine.add_protocol(protocol)

# Usage
session = engine.create_session("user123")
engine.update_session_data(session.session_id, {"location": "Kyiv, Ukraine"})
result = engine.execute_protocol("weather_assistant", session.session_id)
print(result["response"])
```

**Tool-Calling Features:**
- **Dynamic Tool Selection**: Tools are selected based on LLM analysis
- **Parameter Extraction**: Automatic extraction of parameters from user input
- **Error Handling**: Graceful handling of tool execution errors
- **Result Integration**: Tool results are integrated back into the conversation
- **Parallel Execution**: Support for parallel tool execution when appropriate

**CLI Usage with Tools:**
```bash
# Run with tool support
python -c "from src.mova.cli.cli import main; main()" run examples/presets_and_tool_calling_example.json \
  --tools-enabled \
  --tools-dir examples/tools/
```

### 🧠 Memory System

MOVA SDK 2.2 includes a sophisticated memory system for context-aware conversations:

```python
from src.mova.core.engine import MovaEngine
from src.mova.core.memory_system import MemorySystem

# Initialize engine with memory support
engine = MovaEngine()

# Access memory system
memory = engine.memory_system

# Store information in memory
memory.add_to_memory(
    session_id="user123",
    content="User prefers concise responses",
    memory_type="semantic",
    importance=0.8
)

# Retrieve relevant context
context = memory.get_relevant_context(
    session_id="user123",
    query="What are the user's preferences?",
    limit=5
)

# Search memory
results = memory.search_memory(
    session_id="user123",
    query="preferences",
    memory_type="semantic"
)
```

**Memory Types:**
- **Short-term Memory**: Temporary context for current conversation
- **Episodic Memory**: Stores specific events and interactions
- **Semantic Memory**: General knowledge and preferences
- **Working Memory**: Active processing of current information

**Memory Features:**
- **Automatic Context Retrieval**: Relevant memories are automatically retrieved
- **Importance Scoring**: Memories are scored by importance and relevance
- **Memory Consolidation**: Important short-term memories are promoted to long-term
- **Memory Search**: Full-text search across all memory types
- **Memory Management**: Tools for managing and pruning memories

**CLI Usage with Memory:**
```bash
# Run with memory support
python -c "from src.mova.cli.cli import main; main()" run examples/config.json \
  --memory-enabled \
  --memory-ttl 86400  # 24 hours
```

### 🧠 ML Integration

MOVA SDK 2.2 includes comprehensive ML capabilities for natural language understanding:

```python
from mova.ml.integration import MLIntegration

# Initialize ML integration
ml_integration = MLIntegration()

# Analyze text with intent recognition, entity extraction, and sentiment analysis
text = "Зарегистрируй меня как пользователя john@example.com"
prediction = await ml_integration.analyze_text(text, "session_123")

if prediction:
    print(f"Intent: {prediction.intent.intent.value}")
    print(f"Confidence: {prediction.intent.confidence:.2f}")
    print(f"Entities: {len(prediction.entities.entities)}")
    print(f"Sentiment: {prediction.sentiment.sentiment.value}")
    print(f"Processing time: {prediction.processing_time:.3f}s")
```

**ML Features:**
- **Intent Recognition**: BERT/RoBERTa models for intent classification
- **Entity Extraction**: NER with custom entity support
- **Context Analysis**: Conversation history and user profile learning
- **Sentiment Analysis**: Emotion detection and confidence scoring
- **Model Training**: Custom model training with metrics tracking
- **Webhook Events**: Real-time ML event notifications

**CLI Usage with ML:**
```bash
# Run ML analysis
python examples/ml_example.py

# Train custom model
python -c "from mova.ml.integration import MLIntegration; import asyncio; asyncio.run(MLIntegration().train_model(...))"
```

### Redis Integration

MOVA SDK 2.2 includes Redis integration for scalable session management:

```python
from src.mova.core.engine import MovaEngine

# Initialize with Redis
engine = MovaEngine(redis_url="redis://localhost:6379")

# Create session with TTL
session = engine.create_session("user123", ttl=3600)

# Session data is automatically stored in Redis
engine.update_session_data(session.session_id, {
    "user_name": "John",
    "preferences": {"language": "en"}
})
```

**Features:**
- 🚀 **Scalable**: Store sessions in Redis instead of memory
- ⏰ **TTL Support**: Automatic cleanup of expired sessions
- 🔄 **Fallback**: Automatic fallback to memory if Redis unavailable
- 📊 **Monitoring**: Built-in session monitoring and management

### Project Structure

```
MOVA/
├── docs/                 # Documentation
│   ├── REDIS_INTEGRATION.md  # Redis integration guide
│   ├── WEBHOOK_SUPPORT.md    # Webhook support guide
│   └── DEVELOPMENT_PROCESS.md # Development documentation
├── src/mova/            # Source code
│   ├── core/           # Core language components
│   ├── parser/         # JSON/YAML parsers
│   ├── validator/      # Schema validation
│   ├── redis_manager.py # Redis integration
│   ├── webhook.py      # Webhook support
│   ├── webhook_integration.py # Webhook integration
│   └── cli/           # Command line interface
├── tests/              # Test suite
│   ├── test_redis_integration.py # Redis tests
│   └── test_webhook.py # Webhook tests
├── examples/           # Usage examples
│   ├── redis_example.py # Redis usage example
│   └── webhook_example.py # Webhook usage example
└── schemas/           # JSON schemas
```

### CLI Commands

```bash
# Parse MOVA file
python -c "from src.mova.cli.cli import main; main()" parse example.json

# Test components
python -c "from src.mova.cli.cli import main; main()" test example.json --verbose

# Test specific step
python -c "from src.mova.cli.cli import main; main()" test example.json --step-id step1

# Test specific API
python -c "from src.mova.cli.cli import main; main()" test example.json --api-id api1

# Run with step-by-step execution
python -c "from src.mova.cli.cli import main; main()" run example.json --step-by-step

# Run with LLM parameters
python -c "from src.mova.cli.cli import main; main()" run example.json \
  --llm-api-key "your-key" \
  --llm-model "openai/gpt-4" \
  --llm-temperature 0.7 \
  --llm-max-tokens 1000
```

# Validate schema
python -c "from src.mova.cli.cli import main; main()" validate example.json

# Run with Redis
python -c "from src.mova.cli.cli import main; main()" run example.json --redis-url redis://localhost:6379

# Run with webhooks
python -c "from src.mova.cli.cli import main; main()" run example.json --webhook-enabled

# Initialize new project
python -c "from src.mova.cli.cli import main; main()" init
```

## Ukrainian

MOVA (Machine-Operable Verbal Actions) - це декларативна мова, розроблена для взаємодії з великими мовними моделями (LLM). Вона забезпечує структурований підхід до управління діалогами, автоматизації бізнес-процесів та інтеграції можливостей ШІ в додатки.

### Основні особливості

- **Декларативна мова**: JSON-синтаксис для опису взаємодій з LLM
- **Модульна архітектура**: Розділення відповідальності на окремі класи (intent, protocol, tool_api, тощо)
- **Багатоетапні сценарії**: Підтримка складних робочих процесів та логіки розгалуження
- **Інтеграція API**: Вбудована підтримка викликів зовнішніх API
- **Управління контекстом**: Розширене управління сесіями та профілями
- **Redis інтеграція**: Масштабоване зберігання сесій з підтримкою TTL
- **LLM інтеграція**: Підтримка OpenAI/OpenRouter API з налаштовуваними параметрами
- **Система пресетів**: Попередньо визначені конфігурації LLM для різних випадків використання
- **Підтримка Tool-Calling**: Розширена оркестрація інструментів з інтеграцією OpenRouter
- **Система пам'яті**: Контекстно-орієнтоване управління пам'яттю для розмов
- **Розширена валідація**: Комплексна валідація з детальними звітами та рекомендаціями
- **CLI розширення**: Тестування компонентів та покрокове виконання
- **Підтримка вебхуків**: Сповіщення про події в реальному часі для зовнішніх інтеграцій
- **ML інтеграція**: Розпізнавання намірів, витягування сутностей, аналіз контексту та настроїв
- **Двомовна документація**: Повна документація українською та англійською мовами

### Швидкий старт

```bash
# Клонувати репозиторій
git clone https://github.com/Leryk1981/MOVA.git
cd MOVA

# Створити віртуальне середовище
python -m venv mova_env
mova_env\Scripts\Activate.ps1  # Windows
source mova_env/bin/activate   # Linux/Mac

# Встановити залежності
pip install -r requirements.txt

# Запустити тести
pytest

# Почати розробку
python -m mova.cli

# Запустити з Redis (опціонально)
python -c "from src.mova.cli.cli import main; main()" run examples/basic_example.json --redis-url redis://localhost:6379
```

### 🤖 LLM інтеграція з OpenRouter

MOVA SDK 2.2 включає покращену LLM інтеграцію з OpenRouter для доступу до різних AI моделей:

```python
import os
from src.mova.core.engine import MovaEngine

# Встановіть ваш OpenRouter API ключ
os.environ["OPENROUTER_API_KEY"] = "your-api-key-here"

# Ініціалізуйте двигун з підтримкою LLM
engine = MovaEngine()

# Створіть протокол з LLM промптом
protocol = Protocol(
    protocol_id="ai_assistant",
    name="AI Assistant",
    steps=[
        ProtocolStep(
            id="step1",
            action=ActionType.PROMPT,
            prompt="Користувач запитав: {session.data.user_input}. Надайте корисну відповідь."
        )
    ]
)

engine.add_protocol(protocol)

# Використання
session = engine.create_session("user123")
engine.update_session_data(session.session_id, {"user_input": "Що таке ШІ?"})
result = engine.execute_protocol("ai_assistant", session.session_id)
print(result["response"])
```

**Підтримувані моделі:**
- `openai/gpt-3.5-turbo` - Швидка та економічна
- `openai/gpt-4` - Потужніша
- `anthropic/claude-3-haiku` - Швидкий Claude
- `anthropic/claude-3-sonnet` - Балансований Claude
- `anthropic/claude-3-opus` - Найпотужніший Claude

**Використання CLI з LLM:**
```bash
# Запустити з підтримкою LLM
python -c "from src.mova.cli.cli import main; main()" run examples/config.json \
  --llm-api-key "your-api-key" \
  --llm-model "openai/gpt-4"
```

### ⚙️ Система пресетів

MOVA SDK 2.2 представляє потужну систему пресетів для попередньо визначених конфігурацій LLM:

```python
from src.mova.core.engine import MovaEngine
from src.mova.config.loader import load_config

# Завантажте конфігурацію з пресетами
config = load_config("examples/config.yaml")
engine = MovaEngine(config=config)

# Використовуйте різні пресети для різних завдань
# Пресет для загальної розмови
session_general = engine.create_session("user123", preset="general")

# Пресет для творчого письма
session_creative = engine.create_session("user123", preset="creative")

# Пресет для технічного аналізу
session_technical = engine.create_session("user123", preset="technical")
```

**Доступні пресети:**
- `general` - Балансовий для повсякденних розмов
- `creative` - Покращений для творчого письма
- `technical` - Оптимізований для технічного аналізу
- `concise` - Короткі та по суті відповіді

**Приклад конфігурації:**
```yaml
llm:
  provider: openrouter
  api_key_env: OPENROUTER_API_KEY
  base_url: https://openrouter.ai/api/v1
  default_model: openrouter/anthropic/claude-3-haiku

presets:
  general:
    model: openrouter/anthropic/claude-3-haiku
    temperature: 0.3
    max_tokens: 1024
    system: "Ви - корисний асистент."
  
  creative:
    model: openai/gpt-4
    temperature: 0.8
    max_tokens: 2048
    system: "Ви - асистент з творчого письма."
  
  technical:
    model: anthropic/claude-3-sonnet
    temperature: 0.1
    max_tokens: 1536
    system: "Ви - технічний експерт."
```

### 🛠️ Підтримка Tool-Calling

MOVA SDK 2.2 включає розширені можливості tool-calling з інтеграцією OpenRouter:

```python
from src.mova.core.engine import MovaEngine
from src.mova.core.tools.registry import ToolRegistry

# Ініціалізуйте двигун з підтримкою інструментів
engine = MovaEngine()

# Зареєструйте інструменти
registry = ToolRegistry()

# Визначте інструмент для погоди
weather_tool = {
    "name": "get_weather",
    "description": "Отримати поточну інформацію про погоду для локації",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Місто та область, наприклад, Київ, Україна"
            }
        },
        "required": ["location"]
    }
}

# Додайте інструмент до реєстру
registry.register_tool("get_weather", weather_tool)

# Створіть протокол з tool-calling
protocol = Protocol(
    protocol_id="weather_assistant",
    name="Weather Assistant",
    steps=[
        ProtocolStep(
            id="step1",
            action=ActionType.PROMPT,
            prompt="Яка погода в {session.data.location}?",
            tools=["get_weather"]
        )
    ]
)

engine.add_protocol(protocol)

# Використання
session = engine.create_session("user123")
engine.update_session_data(session.session_id, {"location": "Київ, Україна"})
result = engine.execute_protocol("weather_assistant", session.session_id)
print(result["response"])
```

**Можливості Tool-Calling:**
- **Динамічний вибір інструментів**: Інструменти вибираються на основі аналізу LLM
- **Витягування параметрів**: Автоматичне витягування параметрів з введення користувача
- **Обробка помилок**: Гнучка обробка помилок виконання інструментів
- **Інтеграція результатів**: Результати інструментів інтегруються назад в розмову
- **Паралельне виконання**: Підтримка паралельного виконання інструментів, коли це доречно

**Використання CLI з інструментами:**
```bash
# Запустити з підтримкою інструментів
python -c "from src.mova.cli.cli import main; main()" run examples/presets_and_tool_calling_example.json \
  --tools-enabled \
  --tools-dir examples/tools/
```

### 🧠 Система пам'яті

MOVA SDK 2.2 включає складну систему пам'яті для контекстно-орієнтованих розмов:

```python
from src.mova.core.engine import MovaEngine
from src.mova.core.memory_system import MemorySystem

# Ініціалізуйте двигун з підтримкою пам'яті
engine = MovaEngine()

# Доступ до системи пам'яті
memory = engine.memory_system

# Збережіть інформацію в пам'яті
memory.add_to_memory(
    session_id="user123",
    content="Користувач віддає перевагу коротким відповідям",
    memory_type="semantic",
    importance=0.8
)

# Отримайте релевантний контекст
context = memory.get_relevant_context(
    session_id="user123",
    query="Які переваги користувача?",
    limit=5
)

# Пошук в пам'яті
results = memory.search_memory(
    session_id="user123",
    query="переваги",
    memory_type="semantic"
)
```

**Типи пам'яті:**
- **Короткочасна пам'ять**: Тимчасовий контекст для поточної розмови
- **Епізодична пам'ять**: Зберігає конкретні події та взаємодії
- **Семантична пам'ять**: Загальні знання та переваги
- **Робоча пам'ять**: Активна обробка поточної інформації

**Можливості пам'яті:**
- **Автоматичне отримання контексту**: Релевантні спогади автоматично отримуються
- **Оцінювання важливості**: Спогади оцінюються за важливістю та релевантністю
- **Консолідація пам'яті**: Важливі короткочасні спогади переносяться в довготривалу пам'ять
- **Пошук в пам'яті**: Повнотекстовий пошук по всіх типах пам'яті
- **Управління пам'яттю**: Інструменти для управління та очищення спогадів

**Використання CLI з пам'яттю:**
```bash
# Запустити з підтримкою пам'яті
python -c "from src.mova.cli.cli import main; main()" run examples/config.json \
  --memory-enabled \
  --memory-ttl 86400  # 24 години
```

### Redis інтеграція

MOVA SDK 2.2 включає Redis інтеграцію для масштабованого управління сесіями:

```python
from src.mova.core.engine import MovaEngine

# Ініціалізація з Redis
engine = MovaEngine(redis_url="redis://localhost:6379")

# Створення сесії з TTL
session = engine.create_session("user123", ttl=3600)

# Дані сесії автоматично зберігаються в Redis
engine.update_session_data(session.session_id, {
    "user_name": "Іван",
    "preferences": {"language": "uk"}
})
```

**Можливості:**
- 🚀 **Масштабованість**: Зберігання сесій в Redis замість пам'яті
- ⏰ **TTL підтримка**: Автоматичне очищення застарілих сесій
- 🔄 **Fallback**: Автоматичний перехід до пам'яті при недоступності Redis
- 📊 **Моніторинг**: Вбудований моніторинг та управління сесіями

### Структура проекту

```
MOVA/
├── docs/                 # Документація
│   ├── REDIS_INTEGRATION.md  # Гід по Redis інтеграції
│   └── DEVELOPMENT_PROCESS.md # Документація розробки
├── src/mova/            # Вихідний код
│   ├── core/           # Основні компоненти мови
│   ├── parser/         # JSON/YAML парсери
│   ├── validator/      # Валідація схем (базова + розширена)
│   ├── redis_manager.py # Redis інтеграція
│   ├── llm_client.py   # LLM інтеграція
│   └── cli/           # Інтерфейс командного рядка
├── tests/              # Набір тестів
│   ├── test_redis_integration.py # Тести Redis
│   ├── test_llm_integration.py   # Тести LLM
│   ├── test_advanced_validation.py # Тести розширеної валідації
│   └── test_cli_extensions.py    # Тести CLI розширень
├── examples/           # Приклади використання
│   └── redis_example.py # Приклад використання Redis
└── schemas/           # JSON схеми
```

### CLI розширення

MOVA SDK 2.2 включає потужні розширення CLI для тестування та діагностики:

#### Тестування компонентів
```bash
# Тестувати всі компоненти
python -c "from src.mova.cli.cli import main; main()" test example.json --verbose

# Тестувати конкретний крок
python -c "from src.mova.cli.cli import main; main()" test example.json --step-id step1

# Тестувати конкретний API
python -c "from src.mova.cli.cli import main; main()" test example.json --api-id api1

# Режим dry run
python -c "from src.mova.cli.cli import main; main()" test example.json --dry-run
```

#### Покрокове виконання
```bash
# Виконувати протокол покроково з підтвердженням
python -c "from src.mova.cli.cli import main; main()" run example.json --step-by-step
```

#### Параметри LLM
```bash
# Налаштувати поведінку LLM
python -c "from src.mova.cli.cli import main; main()" run example.json \
  --llm-temperature 0.7 \
  --llm-max-tokens 1000 \
  --llm-timeout 30
```

### Реальні HTTP API виклики

MOVA SDK 2.2 підтримує реальні HTTP виклики до зовнішніх API:

```python
# Приклад ToolAPI конфігурації
{
  "id": "weather_api",
  "name": "Weather Service",
  "endpoint": "https://api.weatherapi.com/v1/current.json",
  "method": "GET",
  "parameters": {
    "key": "{session.data.api_key}",
    "q": "{session.data.city}"
  },
  "authentication": {
    "type": "api_key",
    "credentials": {
      "api_key": "{session.data.weather_api_key}"
    }
  }
}
```

**Можливості:**
- 🔄 **Retry механізм**: Автоматичні повторні спроби при помилках
- 🔐 **Автентифікація**: Підтримка API key, Basic auth, Bearer токенів
- 🔧 **Плейсхолдери**: Динамічна заміна параметрів з сесійних даних
- ⏱️ **Таймаути**: Налаштовувані таймаути для запитів
- 📊 **Обробка помилок**: Детальна обробка та логування помилок API

### Розширена валідація

MOVA SDK 2.2 включає комплексну систему валідації з розширеними можливостями:

#### Базова валідація
```bash
mova validate examples/basic_example.json
```

#### Розширена валідація
```bash
# Розширена валідація з підсумком
mova validate examples/basic_example.json --advanced

# Детальний звіт валідації
mova validate examples/basic_example.json --advanced --detailed

# Збереження звіту в файл
mova validate examples/basic_example.json --advanced --output report.json
```

#### Можливості розширеної валідації

**Перевірка унікальності:**
- Унікальність ID для всіх компонентів
- Відсутність дублікатів в intents, protocols, tools

**Валідація посилань:**
- Перевірка правильності посилань між кроками
- Валідація tool_api_id посилань
- Виявлення циклічних посилань

**Консистентність кроків:**
- Перевірка логічної послідовності кроків
- Виявлення сиротських кроків
- Валідація next_step_id посилань

**API ендпоінти:**
- Валідація URL форматів
- Перевірка HTTP методів
- Валідація автентифікації

**Синтаксис умов:**
- Перевірка операторів умов
- Валідація синтаксису змінних
- Контроль правильності виразів

**Плейсхолдери:**
- Валідація синтаксису плейсхолдерів
- Перевірка формату `{session.data.key}`
- Контроль правильності заміни

**Звіти та рекомендації:**
- Детальна статистика компонентів
- Список помилок та попереджень
- Автоматичні рекомендації для виправлення

```python
from src.mova.core.models import ToolAPI

# Визначити API інструмент
weather_api = ToolAPI(
    id="weather_service",
    name="Weather API",
    endpoint="https://api.weatherapi.com/v1/current.json",
    method="GET",
    parameters={
        "key": "{session.data.api_key}",
        "q": "{session.data.city}",
        "aqi": "no"
    },
    authentication={
        "type": "api_key",
        "credentials": {
            "key": "{session.data.api_key}"
        }
    }
)

# Додати до двигуна
engine.add_tool(weather_api)
```

**Можливості:**
- 🔄 **Механізм повтору**: Автоматичний повтор при невдачах (3 спроби)
- 🔐 **Автентифікація**: Підтримка API ключів та Basic auth
- 📝 **Заміна плейсхолдерів**: Динамічна підстановка параметрів
- ⏱️ **Обробка таймаутів**: Налаштовувані таймаути запитів
- 🛡️ **Обробка помилок**: Комплексне управління помилками

### CLI команди

```bash
# Парсити MOVA файл
python -c "from src.mova.cli.cli import main; main()" parse example.json

# Валідувати схему
python -c "from src.mova.cli.cli import main; main()" validate example.json

# Запустити з Redis
python -c "from src.mova.cli.cli import main; main()" run example.json --redis-url redis://localhost:6379

# Ініціалізувати новий проект
python -c "from src.mova.cli.cli import main; main()" init
```

### Тестування

```bash
# Всі тести
pytest

# Тести Redis інтеграції
pytest tests/test_redis_integration.py -v

# Тести з покриттям
pytest --cov=src/mova
```

### Приклади використання

```python
# Базовий приклад
from src.mova.core.engine import MovaEngine

engine = MovaEngine()
session = engine.create_session("user123")

# Приклад з Redis
from src.mova.core.engine import MovaEngine

engine = MovaEngine(redis_url="redis://localhost:6379")
session = engine.create_session("user123", ttl=1800)
```

### Документація

- [Redis Integration Guide](docs/REDIS_INTEGRATION.md) - Детальний гід по Redis інтеграції
- [Development Process](docs/DEVELOPMENT_PROCESS.md) - Процес розробки
- [Examples](examples/) - Приклади використання

## License / Ліцензія

GNU General Public License v3 (GPLv3) - see LICENSE file for details
GNU General Public License v3 (GPLv3) - дивіться файл LICENSE для деталей 