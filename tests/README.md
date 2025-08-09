# Тестування MOVA SDK

Цей каталог містить тести для MOVA SDK 2.2. Тести охоплюють всі основні компоненти системи та забезпечують надійність роботи SDK.

## Структура тестів

```
tests/
├── __init__.py                 # Ініціалізація пакету тестів
├── test_utils.py               # Утиліти для тестування
├── run_tests.py                # Запускач тестів
├── config/                     # Тести конфігурації
│   ├── __init__.py
│   ├── test_schema.py          # Тести схеми конфігурації
│   └── test_loader.py          # Тести завантажувача конфігурації
├── core/                       # Тести основних компонентів
│   ├── __init__.py
│   ├── test_engine.py          # Тести движка MOVA
│   ├── test_llm_client.py      # Тести LLM клієнта
│   ├── test_memory_system.py   # Тести системи пам'яті
│   └── test_tool_router.py     # Тести роутера інструментів
├── tools/                      # Тести інструментів
│   ├── __init__.py
│   ├── test_registry.py        # Тести реєстру інструментів
│   ├── test_base.py            # Тести базового класу інструментів
│   └── test_builtin.py         # Тести вбудованих інструментів
├── llm/                        # Тести LLM компонентів
│   ├── __init__.py
│   ├── test_llm_client.py      # Тести LLM клієнта
│   └── test_openrouter.py      # Тести інтеграції OpenRouter
└── integration/                # Інтеграційні тести
    ├── __init__.py
    └── test_full_system.py     # Тести повної системи
```

## Запуск тестів

### Запуск всіх тестів

```bash
# Використовуючи pytest (рекомендовано)
python tests/run_tests.py

# Використовуючи unittest
python tests/run_tests.py --unittest

# З детальним виводом
python tests/run_tests.py --verbose
```

### Запуск конкретних тестів

```bash
# Запуск тестів для конкретного модуля
python tests/run_tests.py --module core.test_engine

# Запуск тестів для конкретного класу
python tests/run_tests.py --module core.test_engine --class TestMovaEngine

# Запуск конкретного тесту
python tests/run_tests.py --module core.test_engine --class TestMovaEngine --method test_initialization
```

### Запуск тестів з покриттям

```bash
# Запуск тестів з генерацією звіту про покриття
python tests/run_tests.py --coverage
```

### Перегляд доступних тестів

```bash
# Показати всі доступні тести
python tests/run_tests.py --list
```

## Типи тестів

### Юніт-тести
Тестують окремі компоненти системи в ізоляції:
- Конфігурація (schema, loader)
- Основні компоненти (engine, llm_client, memory_system, tool_router)
- Інструменти (registry, base, builtin)
- LLM компоненти (llm_client, openrouter)

### Інтеграційні тести
Тестують взаємодію між компонентами:
- Повна система (full_system)

## Налаштування тестів

### Змінні середовища

Для налаштування тестів можна використовувати наступні змінні середовища:

```bash
# Встановити URL для тестування OpenRouter
export OPENROUTER_API_URL="https://openrouter.ai/api/v1"

# Встановити API ключ для тестування
export OPENROUTER_API_KEY="your-api-key"

# Встановити URL Redis для тестування
export REDIS_URL="redis://localhost:6379"
```

### Конфігурація тестів

Тести використовують тестову конфігурацію, яка визначена в `tests/test_utils.py`. Ви можете змінити цю конфігурацію для своїх потреб.

## Писання тестів

### Структура тестового файлу

```python
import unittest
from unittest.mock import Mock, patch

from mova.core.engine import MovaEngine
from tests.test_utils import create_test_config


class TestMovaEngine(unittest.TestCase):
    """
    Test class for Mova Engine
    Тестовий клас для движка MOVA
    """
    
    def setUp(self):
        """Set up test method / Налаштувати тестовий метод"""
        self.config = create_test_config()
        self.engine = MovaEngine(self.config)
    
    def test_initialization(self):
        """Test engine initialization / Тест ініціалізації движка"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.config, self.config)
    
    @patch('mova.core.llm_client.openai.OpenAI')
    def test_execute_scenario(self, mock_openai):
        """Test scenario execution / Тест виконання сценарію"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Execute scenario
        scenario = {
            "scenario": {
                "name": "Test Scenario",
                "description": "Test scenario"
            },
            "steps": [
                {
                    "type": "prompt",
                    "content": "Hello"
                }
            ]
        }
        
        result = self.engine.execute_scenario(scenario)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertIn("steps", result)
        self.assertEqual(len(result["steps"]), 1)
```

### Кращі практики

1. **Використовуйте описові імена тестів**: Імена тестів повинні чітко описувати, що вони тестують.
2. **Використовуйте setUp і tearDown**: Для налаштування та очищення тестового середовища.
3. **Мокайте зовнішні залежності**: Використовуйте `unittest.mock` для мокування зовнішніх залежностей.
4. **Тестуйте різні сценарії**: Тестуйте не тільки щасливий шлях, але й помилкові сценарії.
5. **Використовуйте тести для документації**: Тести повинні служити прикладом використання коду.

## Вирішення проблем

### Поширені проблеми

1. **ImportError**: Переконайтеся, що ви додали `src` до `PYTHONPATH`.
2. **ModuleNotFoundError**: Переконайтеся, що всі необхідні модулі встановлені.
3. **AttributeError**: Переконайтеся, що ви правильно використовуєте моки.

### Налагодження тестів

```bash
# Запуск тестів з налагодженням
python -m pdb tests/run_tests.py --module core.test_engine

# Запуск тестів з детальним виводом
python tests/run_tests.py --verbose
```

## Внесок

Ми вітаємо внески у тестування MOVA SDK! Будь ласка, дотримуйтесь наступних правил:

1. Додавайте тести для нової функціональності.
2. Оновлюйте існуючі тести при зміні API.
3. Переконайтеся, що всі тести проходять перед створенням pull request.
4. Підтримуйте покриття коду тестами на високому рівні.

## Ліцензія

Тести поширюються під тією ж ліцензією, що й сам MOVA SDK.