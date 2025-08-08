# MOVA Web Interface - Гід по інтеграції

## Огляд

Цей документ описує повну інтеграцію бекенда (FastAPI) та фронтенда (React) для MOVA Web Interface 2.2.

## Архітектура

```
MOVA Web Interface
├── Backend (FastAPI + Python)
│   ├── API Endpoints (/api/*)
│   ├── MOVA SDK Integration
│   ├── WebSocket Support
│   ├── File Management
│   └── Authentication
├── Frontend (React + TypeScript)
│   ├── Dashboard
│   ├── Editor
│   ├── Monitor
│   └── Settings
└── Integration Layer
    ├── CORS Configuration
    ├── API Client
    └── WebSocket Client
```

## Швидкий старт

### 1. Запуск через скрипт (рекомендовано)

```bash
# З кореневої директорії проекту
python start_web_interface.py
```

Цей скрипт автоматично:
- Перевірить залежності
- Встановить пакети
- Запустить бекенд і фронтенд
- Налаштує інтеграцію

### 2. Ручний запуск

#### Backend
```bash
cd web_interface/backend
pip install -r requirements.txt
python main.py
```

#### Frontend
```bash
cd web_interface/frontend
npm install
npm run dev
```

## Конфігурація

### Backend Configuration

Файл: `web_interface/backend/app/core/config.py`

```python
class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
```

### Frontend Configuration

Файл: `web_interface/frontend/vite.config.ts`

```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

## API Endpoints

### System Endpoints
- `GET /health` - Health check
- `GET /api/system/status` - System status
- `GET /api/system/health` - API health

### CLI Endpoints
- `GET /api/cli/status` - CLI status
- `POST /api/cli/execute` - Execute CLI command
- `GET /api/cli/history` - Command history

### ML Endpoints
- `GET /api/ml/status` - ML status
- `POST /api/ml/train` - Train model
- `GET /api/ml/models` - List models

### File Endpoints
- `GET /api/files/list` - List files
- `POST /api/files/upload` - Upload file
- `GET /api/files/download/{filename}` - Download file

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `POST /api/auth/logout` - Logout

## Інтеграція з MOVA SDK

### Backend Integration

```python
# web_interface/backend/app/services/mova_service.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from mova import MovaEngine, MovaConfig

class MovaService:
    def __init__(self):
        self.engine = MovaEngine()
        self.config = MovaConfig()
```

### Frontend Integration

```typescript
// web_interface/frontend/src/services/api.ts
export const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## CORS Configuration

### Backend CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### Frontend CORS

Vite автоматично налаштовує проксі для API запитів.

## WebSocket Integration

### Backend WebSocket

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        pass
```

### Frontend WebSocket

```typescript
// web_interface/frontend/src/hooks/useWebSocket.ts
export const useWebSocket = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    setSocket(ws);
    
    return () => ws.close();
  }, []);
  
  return socket;
};
```

## Тестування інтеграції

### Запуск тестів

```bash
python test_integration.py
```

### Тести включають:
- Health check бекенда
- API endpoints
- Frontend доступність
- CORS налаштування
- MOVA SDK інтеграцію
- Файлові операції
- WebSocket з'єднання

## Розв'язання проблем

### Проблема: Backend не запускається

**Рішення:**
1. Перевірте Python версію (потрібен 3.8+)
2. Встановіть залежності: `pip install -r requirements.txt`
3. Перевірте шлях до MOVA SDK

### Проблема: Frontend не підключається до Backend

**Рішення:**
1. Перевірте CORS налаштування
2. Переконайтеся що бекенд запущений на порту 8000
3. Перевірте проксі налаштування в vite.config.ts

### Проблема: MOVA SDK не імпортується

**Рішення:**
1. Перевірте шлях до src директорії
2. Встановіть MOVA SDK: `pip install -e .`
3. Перевірте PYTHONPATH

### Проблема: WebSocket не працює

**Рішення:**
1. Перевірте WebSocket endpoint в бекенді
2. Перевірте URL в фронтенді
3. Перевірте CORS для WebSocket

## Моніторинг

### Backend Logs

```bash
# Включення детального логування
export LOG_LEVEL=DEBUG
python main.py
```

### Frontend Logs

```bash
# В браузері
F12 -> Console
```

### System Status

```bash
# Health check
curl http://localhost:8000/health

# API status
curl http://localhost:8000/api/system/status
```

## Розгортання

### Development

```bash
# Запуск в режимі розробки
python start_web_interface.py
```

### Production

```bash
# Backend
cd web_interface/backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd web_interface/frontend
npm run build
npm run preview
```

## Структура файлів

```
MOVA 2.2/
├── start_web_interface.py          # Лаунчер
├── test_integration.py             # Тести інтеграції
├── INTEGRATION_GUIDE.md            # Цей файл
├── web_interface/
│   ├── backend/
│   │   ├── main.py                 # Точка входу бекенда
│   │   ├── app/
│   │   │   ├── api/                # API endpoints
│   │   │   ├── core/               # Конфігурація
│   │   │   ├── services/           # Бізнес-логіка
│   │   │   └── models/             # Pydantic моделі
│   │   └── requirements.txt        # Python залежності
│   └── frontend/
│       ├── src/
│       │   ├── components/         # React компоненти
│       │   ├── pages/              # Сторінки
│       │   ├── services/           # API клієнт
│       │   └── hooks/              # React hooks
│       ├── package.json            # Node.js залежності
│       └── vite.config.ts          # Vite конфігурація
└── src/
    └── mova/                       # MOVA SDK
```

## Контакти та підтримка

Якщо у вас є питання або проблеми з інтеграцією:

1. Перевірте логи в консолі
2. Запустіть тести інтеграції
3. Перевірте конфігурацію
4. Створіть issue в репозиторії

---

**Версія:** 2.2.0  
**Останнє оновлення:** 2024-08-07  
**Автор:** Leryk1981 