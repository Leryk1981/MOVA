# MOVA SDK

MOVA SDK — це інструмент для запуску завдань через CLI або Python API.

## 🔧 Встановлення

```bash
pip install .
```

або напряму з GitHub:

```bash
pip install git+https://github.com/Leryk1981/MOVA.git@release-v0.1.0
```

## 🚀 Використання

### Через CLI

```bash
mova-cli run '{"action": "ping"}'
```

### Через Python API

```python
from mova_sdk.api import MovaAPI

api = MovaAPI()
result = api.run_task({"action": "ping"})
print(result)
```

📁 Приклад: дивись `examples/quickstart.py`