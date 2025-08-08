# MOVA SDK MVP Execution Plan v0.1.0

Пріоритетна мета: стабілізація CLI та інтеграція з MVP Engine; далі API wrappers, DTO, packaging, CI/CD та реліз.

## Загальний підхід
- Реалізація MVP CLI з інтеграцією MVP Engine та базовими API wrappers.
- Поетапне документування та реліз MVP.

## Набір задач з пріоритетами

1) Уточнення та стабілізація CLI-модуля mova_sdk/cli/main.py (першочергово)
- Файли: mova_sdk/cli/main.py, tests/cli/test_main.py
- Дії:
  - Доопрацювати CLI: support команди init, run, status, version, config
  - Інтеграція з MVP Engine: запуск через Engine.run, отримання стану через Engine.status
  - Додати обробку помилок та кольорове форматування виводу
  - Створити/оновити інтеграційні тести CLI (tests/cli/test_main.py)
- Критерій приймання:
  - CLI стабільний, інтегрований з MVP Engine; тести проходять.

2) Розширення API wrappers mova_sdk/api/__init__.py
- Файли: mova_sdk/api/__init__.py; tests/api/test_wrappers.py
- Дії:
  - Замінити заглушки на обгортки навколо Engine, LLMClient, Validator
  - Експорт через __all__
  - Додати базові unit-тести для wrappers
- Критерій приймання:
  - Коректні імпорти, обгортки та тести.

3) DTO-моделі mova_sdk/models
- Файли: mova_sdk/models/__init__.py; tests/models/test_dtos.py
- Дії:
  - Створити базові DTO (TaskDTO тощо) з dataclass
  - Використати DTO у API wrappers та тестах
- Критерій приймання:
  - DTO готові до використання в MVP.

4) Документація та архітектура
- Файли: PLAN.md, PLAN_SDK_ARCHITECTURE.md
- Дії:
  - Оновити відповідні розділи з деталями взаємодій CLI-Engine-API wrappers
  - Додати Mermaid-діаграми
- Критерій приймання:
  - Документація узгоджена з реалізацією.

5) Пакетування та CI/CD
- Файли: pyproject.toml, .github/workflows/ci.yml
- Дії:
  - Налаштувати мінімальне пакування
  - Додати CI/CD для тести, lint та type-check

6) Quickstart та приклади використання
- Файли: examples/sdk_usage.py, README
- Дії:
  - Додати Quickstart та приклади використання CLI та SDK
- Критерій приймання:
  - Гайд доступний.

7) Реліз MVP
- Дії:
  - Підготувати реліз MVP 0.1.0 та тег
  - Оновити CHANGELOG
- Критерій приймання:
  - Реліз готовий до публікації.

Посилання на файли для швидкого доступу
- mova_sdk/cli/main.py: [`mova_sdk/cli/main.py:1`]
- tests/cli/test_main.py: [`tests/cli/test_main.py:1`]
- mova_sdk/api/__init__.py: [`mova_sdk/api/__init__.py:1`]
- tests/api/test_wrappers.py: [`tests/api/test_wrappers.py:1`]
- mova_sdk/models/__init__.py: [`mova_sdk/models/__init__.py:1`]
- tests/models/test_dtos.py: [`tests/models/test_dtos.py:1`]
- PLAN.md: [`PLAN.md:1`]
- PLAN_SDK_ARCHITECTURE.md: [`PLAN_SDK_ARCHITECTURE.md:1`]
- pyproject.toml: [`pyproject.toml:1`]
- examples/sdk_usage.py: [`examples/sdk_usage.py:1`]

Готов приступить до кроку 1 (CLI стабільна версія) після вашого підтвердження. Можу також паралельно взяти на себе наступні кроки за пріоритетом.<update_todo_list>
<todos>
[-] Complete CLI module mova_sdk/cli/main.py stable version (замінити на стабільний MVP-CLI)
[-] Add CLI integration tests: tests/cli/test_main.py
[-] Implement API wrappers in mova_sdk/api/__init__.py and add tests: tests/api/test_wrappers.py
[-] Create DTOs for MVP: mova_sdk/models/__init__.py and tests/models/test_dtos.py
[-] Setup minimal packaging: pyproject.toml
[-] Configure CI/CD skeleton (GitHub Actions) for MVP
[-] Update PLAN.md with MVP execution details
[-] Update PLAN_SDK_ARCHITECTURE.md with current MVP architecture diagrams
[-] Add Quickstart and usage examples: examples/sdk_usage.py
</todos>
</update_todo_list>