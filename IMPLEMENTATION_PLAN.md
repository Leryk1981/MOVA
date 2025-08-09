# Комплексний план реалізації MOVA SDK

## Вступ

Цей документ визначає повний план реалізації функцій MOVA SDK, включаючи базовий функціонал та інтеграцію Presets і Tool-Calling через OpenRouter. План розроблено з урахуванням пріоритетів та поетапної реалізації.

## Частина 1: Базовий функціонал MOVA SDK

### 1.1 Розпізнавання намірів (Intent Recognition)

#### 1.1.1 Базовий модуль розпізнавання намірів
- Реалізація класу `IntentRecognizer`
- Підтримка класифікації текстових запитів
- Інтеграція з існуючими NLP-моделями

#### 1.1.2 Підтримка української мови
- Токенізація для української мови
- Навчання/інтеграція моделей для української мови
- Обробка специфічних українських фраз та виразів

#### 1.1.3 Навчання моделей намірів
- Система збору та анотування даних
- Тренування моделі класифікації намірів
- Валідація та тестування моделей

### 1.2 Система пам'яті

#### 1.2.1 Short-term пам'ять
- Реалізація буфера короткочасної пам'яті
- Механізм обмеження розміру та часу зберігання
- Швидкий доступ до недавніх взаємодій

#### 1.2.2 Episodic пам'ять
- Зберігання ключових подій та взаємодій
- Механізм пошуку та відновлення контексту
- Асоціативний зв'язок між подіями

#### 1.2.3 Semantic пам'ять
- Зберігання знань та фактів
- Семантичний пошук інформації
- Інтеграція з векторними базами даних

#### 1.2.4 Working пам'ять
- Оперативна пам'ять для поточних задач
- Механізм фокусування уваги
- Контекстне управління

#### 1.2.5 Управління пам'яттю
- Автоматичний вибір типу пам'яті
- Механізми оновлення та забування
- Оптимізація використання пам'яті

### 1.3 Навчання системи

#### 1.3.1 Supervised Learning
- Система збору навчальних даних
- Механізми анотування даних
- Тренування моделей з учителем

#### 1.3.2 RLHF (Reinforcement Learning from Human Feedback)
- Збір зворотного зв'язку від користувачів
- Механізми оцінки якості відповідей
- Оптимізація моделей на основі фідбеку

#### 1.3.3 Online Learning
- Адаптивне навчання в реальному часі
- Механізми оновлення моделей без перезапуску
- Моніторинг якості та відкат при погіршенні

#### 1.3.4 Інфраструктура навчання
- Система управління навчальними процесами
- Моніторинг метрик навчання
- Версіонування моделей

### 1.4 Explainable AI

#### 1.4.1 Система пояснення рішень
- Візуалізація процесу прийняття рішень
- Пояснення вибору конкретних відповідей
- Інтерпретація результатів моделі

#### 1.4.2 Прозорість алгоритмів
- Логування проміжних результатів
- Відстеження ланцюжків міркувань
- Аудит прийнятих рішень

### 1.5 Інтеграція з зовнішніми сервісами

#### 1.5.1 REST API
- Розробка RESTful API для MOVA
- Документація API (Swagger/OpenAPI)
- Аутентифікація та авторизація

#### 1.5.2 Вебхуки
- Механізм відправки подій
- Конфігурація вебхуків
- Обробка помилок та повторні спроби

#### 1.5.3 Інтеграція з касовими системами
- Підтримка популярних касових систем
- Синхронізація даних про клієнтів
- Обробка платежів

#### 1.5.4 Календарні системи
- Інтеграція з Google Calendar, Outlook
- Управління записами клієнтів
- Нагадування та сповіщення

### 1.6 Бізнес-логіка для барбершопу (орієнтир для прикладів)

#### 1.6.1 Управління клієнтами
- База даних клієнтів
- Історія візитів та послуг
- Персональні знижки та бонуси

#### 1.6.2 Запис клієнтів
- Перевірка доступності майстрів
- Автоматичний розклад
- Підтвердження та нагадування

#### 1.6.3 Фінансовий облік
- Облік доходів та витрат
- Аналіз прибутковості послуг
- Звіти та статистика

#### 1.6.4 Управління запасами
- Облік товарів та матеріалів
- Автоматичні замовлення
- Контроль термінів придатності

#### 1.6.5 Маркетинг
- Аналіз клієнтської бази
- Персоналізовані пропозиції
- SMS/email розсилки

### 1.7 Покращення існуючих компонентів

#### 1.7.1 LLM інтеграція
- Реальна інтеграція з OpenAI/OpenRouter
- Оптимізація запитів та відповідей
- Управління контекстом

#### 1.7.2 Валідація
- Розширена валідація даних
- Перевірка бізнес-логіки
- Обробка помилок

#### 1.7.3 Кешування
- Оптимізація кешування
- Розумне інвалідування
- Розподілене кешування

#### 1.7.4 Асинхронна обробка
- Покращення асинхронних компонентів
- Оптимізація продуктивності
- Обробка черг

### 1.8 Тестування та документація

#### 1.8.1 Комплексне тестування
- Юніт-тести для нових функцій
- Інтеграційні тести
- Тестування продуктивності

#### 1.8.2 Документація
- API документація
- Керівництва для розробників
- Приклади використання

#### 1.8.3 Моніторинг та логування
- Система моніторингу
- Розширене логування
- Аналітика використання

## Частина 2: Інтеграція Presets і Tool-Calling (OpenRouter)

### 2.1 Архітектурні зміни

#### 2.1.1 Нові файли та структури
```
mova_sdk/
  core/
    engine.py                 # оновлення: оркестрація tool-calling
    llm_client.py             # оновлення: presets integration
    tool_router.py            # новий: диспетчеризація та виконання tools
    tools/
      __init__.py
      registry.py             # новий: реєстр тулів
      base.py                 # новий: BaseTool, контракти
      builtin/
        calendar.py           # приклад тулу
        crm.py                # приклад тулу
  config/
    schema.py                 # новий: pydantic-схеми конфігу
    loader.py                 # новий: завантаження конфігу
  utils/
    jsonschema.py             # новий: валідатори
    logging.py                # новий: структуровані логи
examples/
  barbershop_admin/
    preset.yaml               # приклад пресету
    tools.yaml                # реєстр тулів
tests/
  core/
    test_engine_tools.py
    test_tool_router.py
  tools/
    test_registry.py
  integration/
    test_cli_preset_barbershop.py
```

### 2.2 Конфігурація: presets та tools

#### 2.2.1 Формат конфігурації `mova.yaml`
```yaml
llm:
  provider: openrouter
  api_key_env: OPENROUTER_API_KEY
  base_url: https://openrouter.ai/api/v1

presets:
  default: general
  profiles:
    general:
      model: openrouter/anthropic/claude-3-haiku
      temperature: 0.3
      max_tokens: 1024
      system: |
        You are MOVA default assistant.
    barbershop-admin:
      model: openrouter/openai/gpt-4o-mini
      temperature: 0.2
      max_tokens: 800
      system: |
        You are a barbershop admin assistant. Be concise, ask for date/time, service, and contact.
      tools:
        - calendar.create_event
        - crm.create_or_update_client
        - notifier.send_sms
```

#### 2.2.2 Реєстр тулів `tools.yaml`
```yaml
tools:
  - name: calendar.create_event
    description: Create an appointment in the calendar.
    schema:
      type: object
      properties:
        customer_name: {type: string}
        service: {type: string}
        start_time: {type: string, format: date-time}
        duration_min: {type: integer, minimum: 15, maximum: 240}
      required: [customer_name, service, start_time]
    policy:
      allow_models: ["*"]
      rate_limit_per_min: 60

  - name: crm.create_or_update_client
    description: Upsert client profile in CRM.
    schema:
      type: object
      properties:
        phone: {type: string}
        name: {type: string}
        notes: {type: string}
      required: [phone]

  - name: notifier.send_sms
    description: Send SMS confirmation.
    schema:
      type: object
      properties:
        phone: {type: string}
        message: {type: string, maxLength: 200}
      required: [phone, message]
```

### 2.3 Абстракція LLMClient з пресетами

#### 2.3.1 Інтерфейс `LLMClient`
```python
# mova_sdk/core/llm_client.py
from typing import Any, Dict, Optional, List, TypedDict

class ToolSpec(TypedDict, total=False):
    type: str               # "function"
    function: Dict[str, Any]# {name, description, parameters(JSON schema)}

class LLMResponse(TypedDict, total=False):
    text: str
    tool_calls: List[Dict[str, Any]]  # [{"name": str, "arguments": dict}]

class LLMClient:
    def __init__(self, config: Dict[str, Any]): ...
    def chat(self, messages: List[Dict[str, str]], *,
             preset: Optional[str] = None,
             tools: Optional[List[ToolSpec]] = None) -> LLMResponse: ...
```

#### 2.3.2 OpenRouter реалізація
- Інтеграція з OpenRouter API
- Підтримка tool-calling
- Обробка відповідей з tool_calls

### 2.4 Реєстр тулів і виконання

#### 2.4.1 Базовий контракт тулу
```python
# mova_sdk/core/tools/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    name: str
    description: str
    schema: Dict[str, Any]

    @abstractmethod
    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ...
```

#### 2.4.2 Реєстр тулів
```python
# mova_sdk/core/tools/registry.py
from typing import Dict, Callable, Any
from .base import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        return self._tools[name]

    def to_llm_specs(self, allowed: list[str] | None = None):
        specs = []
        for t in self._tools.values():
            if allowed and t.name not in allowed: 
                continue
            specs.append({
              "type": "function",
              "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema
              }
            })
        return specs
```

#### 2.4.3 Приклади тулів
- `calendar.create_event` - створення подій у календарі
- `crm.create_or_update_client` - управління клієнтами
- `notifier.send_sms` - відправка SMS

### 2.5 Оркестрація tool-calling у Engine

#### 2.5.1 ToolRouter
```python
# mova_sdk/core/tool_router.py
from typing import Dict, Any
from .tools.registry import ToolRegistry
from .utils.jsonschema import validate_json

class ToolRouter:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, call: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.registry.get(call["name"])
        validate_json(tool.schema, call["arguments"])
        return tool.run(call["arguments"])
```

#### 2.5.2 Розширення Engine
```python
# mova_sdk/core/engine.py (розширення run)
def run(self, payload: Any = None, *, preset: str | None = None) -> Any:
    self._state = "running"
    try:
        messages = payload_to_messages(payload)  # нормалізація
        allowed_tools = self._config.get("presets",{}).get("profiles",{}).get(preset or "default",{}).get("tools")
        tool_specs = self._tool_registry.to_llm_specs(allowed_tools)

        rsp = self._llm.chat(messages, preset=preset, tools=tool_specs)

        trace = []
        # поки модель викликає інструменти — виконуємо, додаємо результати та продовжуємо діалог
        while rsp.get("tool_calls"):
            for call in rsp["tool_calls"]:
                result = self._tool_router.execute(call)
                trace.append({"tool": call["name"], "args": call["arguments"], "result": result})
                messages.append({"role":"tool", "name": call["name"], "content": json.dumps(result)})
            rsp = self._llm.chat(messages, preset=preset, tools=tool_specs)

        return {"text": rsp.get("text",""), "trace": trace}
    finally:
        self._state = "idle"
```

### 2.6 CLI: додаткові прапори

#### 2.6.1 Розширення CLI
```bash
mova-cli run payload.json --preset barbershop-admin --trace --dry-run
```

#### 2.6.2 Нові опції
- `--preset` - обрати профіль
- `--trace` - виводити кроки/інструменти
- `--dry-run` - тільки перевірка схеми/доступності тулів

### 2.7 Тестування

#### 2.7.1 Unit тести
- `tests/tools/test_registry.py`: реєстрація інструментів, `to_llm_specs`
- `tests/core/test_tool_router.py`: валідація JSON, виклик `run`
- `tests/core/test_engine_tools.py`: ланцюжок tool-calls без зовнішніх інтеграцій (моки)

#### 2.7.2 Інтеграційні тести
- `tests/integration/test_cli_preset_barbershop.py`: тестування CLI сценарію з барбершопом

## Пріоритети реалізації

### Етап 1: Інтеграція Presets і Tool-Calling (OpenRouter) - Високий пріоритет

#### Ітерація A (Presets + Tool Registry + CLI) - 1-2 дні
1. **Конфігурація**
   - [ ] Додати `mova_sdk/config/{loader.py,schema.py}`
   - [ ] Реалізувати завантаження конфігурації з `mova.yaml`/`pyproject.toml`
   - [ ] Додати підтримку змінних оточення

2. **LLMClient з пресетами**
   - [ ] Оновити `mova_sdk/core/llm_client.py` (OpenRouter driver)
   - [ ] Додати підтримку `preset` параметра
   - [ ] Реалізувати вибір моделі та параметрів на основі пресету
   - [ ] Додати підтримку tool-calling в OpenRouter

3. **Реєстр тулів**
   - [ ] Додати `mova_sdk/core/tools/registry.py`
   - [ ] Додати `mova_sdk/core/tools/base.py`
   - [ ] Створити приклади тулів у `mova_sdk/core/tools/builtin/`
   - [ ] Реалізувати завантаження тулів з YAML

4. **CLI розширення**
   - [ ] Додати `--preset`, `--trace`, `--dry-run` опції
   - [ ] Оновити логування для трасування
   - [ ] Реалізувати dry-run режим

5. **Тести**
   - [ ] Unit тести для LLMClient (моки)
   - [ ] Unit тести для ToolRegistry
   - [ ] Тести завантаження конфігурації

#### Ітерація B (Engine Orchestration + Validations) - 1-2 дні
1. **ToolRouter**
   - [ ] Додати `mova_sdk/core/tool_router.py`
   - [ ] Реалізувати JSON-schema валідацію
   - [ ] Додати обробку помилок

2. **Engine оновлення**
   - [ ] Оновити `mova_sdk/core/engine.py` (tool-calling цикл)
   - [ ] Реалізувати оркестрацію tool-calling
   - [ ] Додати трасування виконання

3. **Утиліти**
   - [ ] Додати `mova_sdk/utils/jsonschema.py`
   - [ ] Додати `mova_sdk/utils/logging.py`
   - [ ] Реалізувати структуроване логування

4. **Тести**
   - [ ] Інтеграційні тести (CLI сценарій barbershop)
   - [ ] Тести для ToolRouter
   - [ ] Тести для Engine з tool-calling

5. **Документація та приклади**
   - [ ] Оновити документацію: Presets/Tools розділ
   - [ ] Створити приклади в `examples/barbershop_admin/`
   - [ ] Додати приклади використання

### Етап 2: Базовий функціонал MOVA SDK - Середній пріоритет

#### Ітерація C (Базові компоненти) - 3-4 дні
1. **Розпізнавання намірів**
   - [ ] Базовий модуль `IntentRecognizer`
   - [ ] Підтримка української мови
   - [ ] Інтеграція з NLP-моделями

2. **Покращення існуючих компонентів**
   - [ ] LLM інтеграція (реальна, не заглушка)
   - [ ] Розширена валідація
   - [ ] Оптимізація кешування
   - [ ] Покращення асинхронних компонентів

3. **Тестування**
   - [ ] Юніт-тести для нових функцій
   - [ ] Інтеграційні тести
   - [ ] Тестування продуктивності

#### Ітерація D (Розширені можливості) - 3-4 дні
1. **Система пам'яті (базова)**
   - [ ] Short-term пам'ять
   - [ ] Episodic пам'ять
   - [ ] Semantic пам'ять
   - [ ] Working пам'ять
   - [ ] Управління пам'яттю

2. **Інтеграція з зовнішніми сервісами**
   - [ ] REST API
   - [ ] Вебхуки
   - [ ] Календарні системи

3. **Тестування та документація**
   - [ ] Комплексні тести
   - [ ] API документація
   - [ ] Керівництва для розробників

### Етап 3: Просунуті функції - Низький пріоритет

#### Ітерація E (Навчання та Explainable AI) - 4-5 днів
1. **Навчання системи**
   - [ ] Supervised Learning
   - [ ] RLHF
   - [ ] Online Learning
   - [ ] Інфраструктура навчання

2. **Explainable AI**
   - [ ] Система пояснення рішень
   - [ ] Прозорість алгоритмів

3. **Тестування та документація**
   - [ ] Тести для ML компонентів
   - [ ] Документація ML функцій
   - [ ] Приклади використання

#### Ітерація F (Повна інтеграція та оптимізація) - 3-4 дні
1. **Інтеграція з касовими системами**
   - [ ] Підтримка популярних касових систем
   - [ ] Синхронізація даних
   - [ ] Обробка платежів

2. **Оптимізація та моніторинг**
   - [ ] Оптимізація продуктивності
   - [ ] Система моніторингу
   - [ ] Розширене логування
   - [ ] Аналітика використання

3. **Фінальне тестування**
   - [ ] Комплексне тестування
   - [ ] Тестування навантаження
   - [ ] Тестування безпеки

## Технічні вимоги

### Залежності
- Розширення requirements.txt
- Додавання ML-бібліотек
- Бази даних для зберігання даних
- Бібліотеки для роботи з JSON Schema

### Інфраструктура
- Налаштування баз даних
- Налаштування черг завдань
- Налаштування моніторингу
- Налаштування логування

### Безпека
- Аутентифікація та авторизація
- Шифрування даних
- Захист API
- Політики доступу для тулів

## Висновок

Цей комплексний план визначає повний шлях розробки MOVA SDK від базової архітектури до повноцінної системи з Presets, Tool-Calling, ML-можливостями та бізнес-логікою. Реалізація розбита на етапи з чіткими пріоритетами, що дозволить поступово розширювати функціональність системи.

Першочерговим завданням є інтеграція Presets і Tool-Calling через OpenRouter, що створить основу для подальшої розробки та дозволить швидко створювати приклади використання на основі барбершопу.