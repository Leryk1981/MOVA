# Changelog / Журнал змін

## v0.1.0 — Перший стабільний реліз / First Stable Release

### Нові функції / New Features
- ✅ Додано CLI з командами: `run`, `status`, `version` / Added CLI with commands: `run`, `status`, `version`
- ✅ Додано MovaAPI з інтеграцією `engine`, `llm`, `validator` / Added MovaAPI with `engine`, `llm`, `validator` integration
- ✅ Реалізовано підтримку асинхронних операцій / Implemented asynchronous operations support
- ✅ Додано веб-інтерфейс для зручного використання / Added web interface for convenient usage
- ✅ Інтеграція з ML моделями для розпізнавання намірів / Integration with ML models for intent recognition
- ✅ Додано механізм валідації вхідних даних / Added input data validation mechanism
- ✅ Реалізовано підтримку Redis для кешування / Implemented Redis support for caching
- ✅ Додано підтримку вебхуків / Added webhook support

### Покращення / Improvements
- ✅ Оптимізовано продуктивність LLM клієнта / Optimized LLM client performance
- ✅ Розширено налаштування конфігурації / Extended configuration settings
- ✅ Покращено обробку помилок / Improved error handling
- ✅ Додано логування операцій / Added operation logging
- ✅ Оптимізовано використання пам'яті / Optimized memory usage

### Документація / Documentation
- ✅ Додано детальну документацію на українській та англійській мовах / Added detailed documentation in Ukrainian and English
- ✅ Додано приклади використання в `examples/` / Added usage examples in `examples/`
- ✅ Додано опис API в `docs/` / Added API description in `docs/`
- ✅ Підготовлено до CI/CD з `.github/workflows/ci.yml` / Prepared for CI/CD with `.github/workflows/ci.yml`

### Тестування / Testing
- ✅ Покрито тести для CLI та API / Covered tests for CLI and API
- ✅ Додано інтеграційні тести / Added integration tests
- ✅ Додано тести для ML компонентів / Added tests for ML components
- ✅ Налаштовано тестування з покриттям коду / Configured testing with code coverage

### Вимоги / Requirements
- ✅ Python 3.8+ / Python 3.8+
- ✅ Додано всі необхідні залежності в `pyproject.toml` / Added all necessary dependencies in `pyproject.toml`
- ✅ Налаштовано віртуальні середовища для розробки / Configured virtual environments for development