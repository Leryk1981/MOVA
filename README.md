# MOVA SDK / MOVA SDK

## Українська / Ukrainian

MOVA SDK — це потужний інструмент для запуску завдань через CLI або Python API, що забезпечує гнучкість та легкість інтеграції у ваші проєкти.

### 🔧 Встановлення / Installation

```bash
pip install .
```

або напряму з GitHub / or directly from GitHub:

```bash
pip install git+https://github.com/Leryk1981/MOVA.git@release-v0.1.0
```

### 🚀 Використання / Usage

#### Через CLI / Via CLI

```bash
mova-cli run '{"action": "ping"}'
```

#### Через Python API / Via Python API

```python
from mova_sdk.api import MovaAPI

api = MovaAPI()
result = api.run_task({"action": "ping"})
print(result)
```

### 📚 Документація / Documentation

- � Приклад використання / Usage example: `examples/quickstart.py`
- 📖 Повна документація / Full documentation: `docs/`
- 🔧 Конфігурація / Configuration: `examples/config.yaml`

### 🛠️ Функції / Features

- ✅ CLI інтерфейс з командами: `run`, `status`, `version`
- ✅ Python API для інтеграції з вашими проєктами
- ✅ Підтримка різних типів завдань
- ✅ Механізм валідації вхідних даних
- ✅ Розширені можливості налаштування
- ✅ Підтримка асинхронних операцій
- ✅ Інтеграція з ML моделями для розпізнавання намірів
- ✅ Веб-інтерфейс для зручного використання

### 🧪 Тестування / Testing

```bash
# Запуск тестів / Run tests
pytest

# Запуск тестів з покриттям / Run tests with coverage
pytest --cov=mova_sdk
```

### 🤝 Contributing

Ми вітаємо внески від спільноти! Будь ласка, прочитайте [`CONTRIBUTING.md`](CONTRIBUTING.md) для отримання детальної інформації про те, як взяти участь у розвитку проєкту.

We welcome contributions from the community! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for details on how to contribute to the project.

---

## English / English

MOVA SDK is a powerful tool for running tasks via CLI or Python API, providing flexibility and ease of integration into your projects.

### 🔧 Installation / Встановлення

```bash
pip install .
```

or directly from GitHub / або напряму з GitHub:

```bash
pip install git+https://github.com/Leryk1981/MOVA.git@release-v0.1.0
```

### 🚀 Usage / Використання

#### Via CLI / Через CLI

```bash
mova-cli run '{"action": "ping"}'
```

#### Via Python API / Через Python API

```python
from mova_sdk.api import MovaAPI

api = MovaAPI()
result = api.run_task({"action": "ping"})
print(result)
```

### 📚 Documentation / Документація

- 📁 Usage example / Приклад використання: `examples/quickstart.py`
- 📖 Full documentation / Повна документація: `docs/`
- 🔧 Configuration / Конфігурація: `examples/config.yaml`

### 🛠️ Features / Функції

- ✅ CLI interface with commands: `run`, `status`, `version`
- ✅ Python API for integration with your projects
- ✅ Support for various task types
- ✅ Input data validation mechanism
- ✅ Advanced configuration options
- ✅ Support for asynchronous operations
- ✅ Integration with ML models for intent recognition
- ✅ Web interface for convenient usage

### 🧪 Testing / Тестування

```bash
# Run tests / Запуск тестів
pytest

# Run tests with coverage / Запуск тестів з покриттям
pytest --cov=mova_sdk
```

### 🤝 Contributing

We welcome contributions from the community! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for details on how to contribute to the project.

Ми вітаємо внески від спільноти! Будь ласка, прочитайте [`CONTRIBUTING.md`](CONTRIBUTING.md) для отримання детальної інформації про те, як взяти участь у розвитку проєкту.