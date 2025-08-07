# MOVA - Machine-Operable Verbal Actions

[English](#english) | [Українська](#ukrainian)

## English

MOVA (Machine-Operable Verbal Actions) is a declarative language designed for interaction with Large Language Models (LLM). It provides a structured approach to managing conversations, automating business processes, and integrating AI capabilities into applications.

### Key Features

- **Declarative Language**: JSON-based syntax for describing LLM interactions
- **Modular Design**: Separation of concerns into distinct classes (intent, protocol, tool_api, etc.)
- **Multi-step Scenarios**: Support for complex workflows and branching logic
- **API Integration**: Built-in support for external API calls
- **Context Management**: Advanced session and profile management
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
```

### Project Structure

```
MOVA/
├── docs/                 # Documentation
├── src/mova/            # Source code
│   ├── core/           # Core language components
│   ├── parser/         # JSON/YAML parsers
│   ├── validator/      # Schema validation
│   └── cli/           # Command line interface
├── tests/              # Test suite
├── examples/           # Usage examples
└── schemas/           # JSON schemas
```

## Ukrainian

MOVA (Machine-Operable Verbal Actions) - це декларативна мова, розроблена для взаємодії з великими мовними моделями (LLM). Вона забезпечує структурований підхід до управління діалогами, автоматизації бізнес-процесів та інтеграції можливостей ШІ в додатки.

### Основні особливості

- **Декларативна мова**: JSON-синтаксис для опису взаємодій з LLM
- **Модульна архітектура**: Розділення відповідальності на окремі класи (intent, protocol, tool_api, тощо)
- **Багатоетапні сценарії**: Підтримка складних робочих процесів та логіки розгалуження
- **Інтеграція API**: Вбудована підтримка викликів зовнішніх API
- **Управління контекстом**: Розширене управління сесіями та профілями
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
```

### Структура проекту

```
MOVA/
├── docs/                 # Документація
├── src/mova/            # Вихідний код
│   ├── core/           # Основні компоненти мови
│   ├── parser/         # JSON/YAML парсери
│   ├── validator/      # Валідація схем
│   └── cli/           # Інтерфейс командного рядка
├── tests/              # Набір тестів
├── examples/           # Приклади використання
└── schemas/           # JSON схеми
```

## License / Ліцензія

GNU General Public License v3 (GPLv3) - see LICENSE file for details
GNU General Public License v3 (GPLv3) - дивіться файл LICENSE для деталей 