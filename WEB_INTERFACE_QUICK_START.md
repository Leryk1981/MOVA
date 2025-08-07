# 🚀 MOVA Web Interface - Quick Start
# Швидкий старт веб-інтерфейсу MOVA

## 📋 Швидкий запуск

### Варіант 1: З кореневої директорії (рекомендовано)
```bash
python start_web_interface.py
```

### Варіант 2: Прямий запуск backend
```bash
cd web_interface/backend
python run.py
```

### Варіант 3: Через uvicorn
```bash
cd web_interface/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Доступні URL

Після запуску backend буде доступний за адресами:

- **🏠 Головна сторінка**: http://localhost:8000
- **📚 API документація (Swagger)**: http://localhost:8000/api/docs
- **📖 ReDoc документація**: http://localhost:8000/api/redoc
- **🏥 Health check**: http://localhost:8000/health
- **📊 Статус системи**: http://localhost:8000/api/system/status

## 🧪 Тестування

### Запуск тестів
```bash
cd web_interface/backend
python test_backend.py
```

### Тестування API
```bash
# Health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/api/system/status

# List files
curl http://localhost:8000/api/files/list
```

## 📁 Структура проекту

```
web_interface/
├── backend/              # Backend (FastAPI)
│   ├── app/
│   │   ├── api/         # API роути (44 endpoints)
│   │   ├── core/        # Основні компоненти
│   │   ├── models/      # Моделі даних
│   │   └── services/    # Сервіси
│   ├── main.py          # Головний файл
│   ├── run.py           # Скрипт запуску
│   └── test_backend.py  # Тести
└── README.md            # Документація
```

## 🔧 API Endpoints

### CLI Commands (15 endpoints)
- `POST /api/cli/execute` - виконання CLI команд
- `POST /api/cli/parse` - парсинг файлів
- `POST /api/cli/validate` - валідація файлів
- `POST /api/cli/run` - запуск протоколів
- `POST /api/cli/analyze` - аналіз файлів
- `POST /api/cli/diagnose` - діагностика помилок

### File Management (10 endpoints)
- `POST /api/files/upload` - завантаження файлів
- `GET /api/files/list` - список файлів
- `GET /api/files/read/{filename}` - читання файлу
- `POST /api/files/write/{filename}` - запис файлу

### System Monitoring (6 endpoints)
- `GET /api/system/status` - статус системи
- `GET /api/system/info` - інформація про систему
- `GET /api/system/metrics` - системні метрики
- `POST /api/system/cleanup` - очищення системи

### ML Integration (12 endpoints)
- `GET /api/ml/status` - статус ML системи
- `GET /api/ml/models` - список моделей
- `POST /api/ml/analyze/intent` - аналіз намірів
- `POST /api/ml/recommendations/generate` - генерація рекомендацій

## 🛠️ Troubleshooting

### Проблема: "No such file or directory"
**Рішення**: Запускайте з правильної директорії або використовуйте `start_web_interface.py`

### Проблема: "Port already in use"
**Рішення**: Змініть порт або зупиніть інший сервер
```bash
uvicorn main:app --reload --port 8001
```

### Проблема: "MOVA SDK not available"
**Рішення**: Переконайтеся, що MOVA SDK встановлений та доступний

### Проблема: "Redis connection failed"
**Рішення**: Redis не обов'язковий, система працюватиме без нього

## 📈 Наступні кроки

1. **Frontend Development** - створення React інтерфейсу
2. **Authentication** - додавання авторизації
3. **Real-time Updates** - WebSocket інтеграція
4. **Production Deployment** - Docker та CI/CD

## 🎯 Статус

- ✅ **Backend**: Готовий до використання
- ✅ **API**: 44 endpoints працюють
- ✅ **MOVA SDK**: Повна інтеграція
- ✅ **Testing**: Тести пройдені
- 📋 **Frontend**: В розробці

---

**Версія**: 2.2.0  
**Дата**: 2024-12-19  
**Автор**: MOVA Development Team 