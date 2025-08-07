# Redis Integration for MOVA SDK

## Огляд

MOVA SDK 2.2 підтримує інтеграцію з Redis для зберігання даних сесій. Це дозволяє:

- **Масштабованість**: Зберігання сесій в Redis замість оперативної пам'яті
- **Персистентність**: Дані сесій зберігаються між перезапусками
- **TTL підтримка**: Автоматичне видалення застарілих сесій
- **Кластеризація**: Підтримка Redis кластерів для високої доступності

## Встановлення

### Залежності

Додайте Redis до `requirements.txt`:

```txt
# Для Redis інтеграції
redis>=4.0.0
```

Встановіть залежності:

```bash
pip install redis
```

### Redis сервер

#### Локальна установка

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Завантажте Redis з [офіційного сайту](https://redis.io/download) або використовуйте Docker.

#### Docker

```bash
docker run -d -p 6379:6379 redis
```

## Використання

### Базове використання

```python
from src.mova.core.engine import MovaEngine

# Ініціалізація з Redis
engine = MovaEngine(redis_url="redis://localhost:6379")

# Створення сесії
session = engine.create_session("user123", ttl=3600)

# Оновлення даних сесії
engine.update_session_data(session.session_id, {
    "user_name": "John",
    "pizza_type": "Margherita"
})

# Отримання даних сесії
data = engine.get_session_data(session.session_id)
```

### CLI з Redis

```bash
# Запуск з Redis
python -c "from src.mova.cli.cli import main; main()" run examples/basic_example.json --redis-url redis://localhost:6379

# Валідація з Redis
python -c "from src.mova.cli.cli import main; main()" validate examples/basic_example.json --redis-url redis://localhost:6379
```

### Пряме використання Redis Manager

```python
from src.mova.redis_manager import MovaRedisManager

# Створення менеджера
redis_manager = MovaRedisManager("redis://localhost:6379")

# Створення сесії
session_data = {
    "user_id": "user123",
    "preferences": {"language": "uk", "theme": "dark"}
}
redis_manager.create_session("session_123", session_data, ttl=1800)

# Отримання даних
data = redis_manager.get_session_data("session_123")

# Оновлення даних
redis_manager.update_session_data("session_123", "new_key", "new_value")

# Отримання інформації про сесію
info = redis_manager.get_session_info("session_123")
print(f"TTL: {info['ttl']} seconds")
```

## API Документація

### MovaEngine

#### `__init__(redis_url: Optional[str] = None)`

Ініціалізує движок з опціональною підтримкою Redis.

**Параметри:**
- `redis_url`: URL підключення до Redis (наприклад, "redis://localhost:6379")

**Приклади:**
```python
# З Redis
engine = MovaEngine(redis_url="redis://localhost:6379")

# Без Redis (in-memory)
engine = MovaEngine()
```

#### `create_session(user_id: str, ttl: int = 3600) -> Session`

Створює нову сесію з підтримкою TTL.

**Параметри:**
- `user_id`: Ідентифікатор користувача
- `ttl`: Час життя сесії в секундах (за замовчуванням 3600)

**Повертає:**
- `Session`: Об'єкт сесії

#### `get_session_data(session_id: str) -> Optional[Dict[str, Any]]`

Отримує дані сесії з Redis або пам'яті.

**Параметри:**
- `session_id`: Ідентифікатор сесії

**Повертає:**
- `Optional[Dict[str, Any]]`: Дані сесії або None

#### `update_session_data(session_id: str, data: Dict[str, Any]) -> bool`

Оновлює дані сесії в Redis та пам'яті.

**Параметри:**
- `session_id`: Ідентифікатор сесії
- `data`: Дані для оновлення

**Повертає:**
- `bool`: Статус успіху

### MovaRedisManager

#### `__init__(redis_url: str, decode_responses: bool = True)`

Ініціалізує Redis менеджер.

**Параметри:**
- `redis_url`: URL підключення до Redis
- `decode_responses`: Декодувати відповіді як рядки

#### `create_session(session_id: str, data: Dict[str, Any], ttl: int) -> bool`

Створює нову сесію в Redis.

**Параметри:**
- `session_id`: Ідентифікатор сесії
- `data`: Початкові дані сесії
- `ttl`: Час життя в секундах

**Повертає:**
- `bool`: Статус успіху

#### `get_session_data(session_id: str) -> Optional[Dict[str, Any]]`

Отримує дані сесії з Redis.

#### `update_session_data(session_id: str, key: str, value: Any) -> bool`

Оновлює конкретне значення в сесії.

#### `update_session_data_batch(session_id: str, data: Dict[str, Any]) -> bool`

Оновлює кілька значень в сесії.

#### `delete_session(session_id: str) -> bool`

Видаляє сесію з Redis.

#### `get_session_ttl(session_id: str) -> Optional[int]`

Отримує TTL сесії.

#### `extend_session_ttl(session_id: str, ttl: int) -> bool`

Продовжує TTL сесії.

#### `list_sessions(pattern: str = "mova:session:*") -> list`

Отримує список всіх сесій.

#### `get_session_info(session_id: str) -> Optional[Dict[str, Any]]`

Отримує детальну інформацію про сесію.

## Конфігурація Redis

### URL формат

```
redis://[username:password@]host[:port][/database]
```

**Приклади:**
```python
# Локальний Redis
redis_url = "redis://localhost:6379"

# Redis з паролем
redis_url = "redis://username:password@localhost:6379"

# Redis з базою даних
redis_url = "redis://localhost:6379/1"

# Redis через SSL
redis_url = "rediss://localhost:6379"
```

### Налаштування

```python
from src.mova.redis_manager import MovaRedisManager

# Базові налаштування
manager = MovaRedisManager("redis://localhost:6379")

# З додатковими параметрами
manager = MovaRedisManager(
    redis_url="redis://localhost:6379",
    decode_responses=True
)
```

## Приклади використання

### Приклад 1: Чат-бот з Redis

```python
from src.mova.core.engine import MovaEngine
from src.mova.core.models import Intent, Protocol, ProtocolStep, ActionType

# Створення движка з Redis
engine = MovaEngine(redis_url="redis://localhost:6379")

# Додавання наміру
intent = Intent(
    name="greeting",
    patterns=["hello", "hi", "привіт"],
    intent_type="greeting"
)
engine.add_intent(intent)

# Створення протоколу
step = ProtocolStep(
    id="greet",
    action=ActionType.PROMPT,
    prompt="Привіт! Як справи?"
)

protocol = Protocol(
    name="greeting_protocol",
    steps=[step]
)
engine.add_protocol(protocol)

# Створення сесії
session = engine.create_session("user123", ttl=1800)

# Виконання протоколу
result = engine.execute_protocol("greeting_protocol", session.session_id)

# Отримання даних сесії
data = engine.get_session_data(session.session_id)
print(f"Session data: {data}")
```

### Приклад 2: E-commerce з Redis

```python
from src.mova.core.engine import MovaEngine

# Ініціалізація
engine = MovaEngine(redis_url="redis://localhost:6379")

# Створення сесії покупця
session = engine.create_session("customer_456", ttl=3600)

# Збереження даних покупця
engine.update_session_data(session.session_id, {
    "user_id": "customer_456",
    "cart": [],
    "preferences": {
        "language": "uk",
        "currency": "UAH"
    }
})

# Додавання товару до кошика
cart_data = engine.get_session_data(session.session_id)
cart = cart_data.get("cart", [])
cart.append({"product_id": "pizza_001", "quantity": 2})

engine.update_session_data(session.session_id, {"cart": cart})

# Перевірка кошика
updated_data = engine.get_session_data(session.session_id)
print(f"Cart: {updated_data['cart']}")
```

### Приклад 3: Моніторинг сесій

```python
from src.mova.redis_manager import MovaRedisManager

# Створення менеджера
manager = MovaRedisManager("redis://localhost:6379")

# Отримання списку всіх сесій
sessions = manager.list_sessions()
print(f"Total sessions: {len(sessions)}")

# Моніторинг конкретної сесії
for session_id in sessions[:5]:  # Перші 5 сесій
    info = manager.get_session_info(session_id)
    if info:
        print(f"Session {session_id}:")
        print(f"  TTL: {info.get('ttl')} seconds")
        print(f"  Created: {info.get('created_at')}")
        print(f"  Data keys: {info.get('data_keys', [])}")
```

## Тестування

### Запуск тестів

```bash
# Всі тести Redis
pytest tests/test_redis_integration.py -v

# Конкретний тест
pytest tests/test_redis_integration.py::TestRedisIntegration::test_create_session_with_redis -v
```

### Тестування з реальним Redis

```bash
# Запуск Redis через Docker
docker run -d -p 6379:6379 redis

# Запуск тестів
python examples/redis_example.py
```

## Troubleshooting

### Проблеми підключення

**Помилка: "Connection refused"**
```bash
# Перевірте, чи запущений Redis
redis-cli ping

# Запустіть Redis
sudo systemctl start redis-server
```

**Помилка: "Authentication failed"**
```python
# Використовуйте правильний URL з паролем
redis_url = "redis://username:password@localhost:6379"
```

### Проблеми продуктивності

**Високе використання пам'яті**
```python
# Встановіть TTL для сесій
session = engine.create_session("user123", ttl=1800)  # 30 хвилин

# Регулярно очищайте старі сесії
manager.clear_all_sessions()
```

**Повільні операції**
```python
# Використовуйте batch операції
manager.update_session_data_batch(session_id, {
    "key1": "value1",
    "key2": "value2"
})
```

## Безпека

### Рекомендації

1. **Використовуйте паролі** для Redis в продакшені
2. **Обмежте доступ** до Redis порту
3. **Використовуйте SSL** для з'єднань через мережу
4. **Регулярно оновлюйте** Redis до останньої версії

### Конфігурація безпеки

```bash
# redis.conf
requirepass your_strong_password
bind 127.0.0.1
protected-mode yes
```

## Моніторинг

### Метрики

```python
from src.mova.redis_manager import MovaRedisManager

manager = MovaRedisManager("redis://localhost:6379")

# Кількість активних сесій
sessions = manager.list_sessions()
print(f"Active sessions: {len(sessions)}")

# Середній TTL
total_ttl = 0
for session_id in sessions:
    ttl = manager.get_session_ttl(session_id)
    if ttl:
        total_ttl += ttl

avg_ttl = total_ttl / len(sessions) if sessions else 0
print(f"Average TTL: {avg_ttl} seconds")
```

### Логування

```python
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Логування операцій Redis
logger.info(f"Session {session_id} created with TTL {ttl}")
logger.warning(f"Session {session_id} expired")
logger.error(f"Redis connection failed: {error}")
```

## Висновок

Redis інтеграція в MOVA SDK 2.2 забезпечує:

- ✅ **Масштабованість** для великої кількості сесій
- ✅ **Персистентність** даних між перезапусками
- ✅ **TTL підтримку** для автоматичного очищення
- ✅ **Fallback до пам'яті** при недоступності Redis
- ✅ **Повну сумісність** з існуючим API

Для початку роботи просто передайте `redis_url` до `MovaEngine` та насолоджуйтесь перевагами Redis! 