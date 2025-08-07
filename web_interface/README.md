# MOVA Web Interface
# Веб-інтерфейс MOVA

## Overview / Огляд

Веб-інтерфейс для MOVA 2.2, що надає зручний спосіб управління протоколами, моніторингу та редагування конфігурацій через браузер.

## Architecture / Архітектура

```
MOVA Web Interface
├── Backend (FastAPI)
│   ├── API endpoints для CLI команд
│   ├── WebSocket для real-time оновлень
│   ├── File management (upload/download)
│   └── Session management
├── Frontend (React + TypeScript)
│   ├── Dashboard - головна панель
│   ├── Editor - візуальний редактор MOVA файлів
│   ├── Monitor - моніторинг та метрики
│   └── Settings - налаштування системи
└── Shared
    ├── Types - TypeScript типи
    ├── API client - HTTP клієнт
    └── Utils - утиліти
```

## Features / Функціональність

### 🎯 Core Features / Основні функції
- **Dashboard** - огляд системи та швидкі дії
- **Visual Editor** - редагування MOVA файлів з підсвічуванням синтаксису
- **Protocol Management** - управління протоколами
- **Real-time Monitoring** - моніторинг в реальному часі
- **ML Integration** - управління ML моделями та рекомендаціями

### 🔧 Management Features / Функції управління
- **Redis Management** - керування сесіями Redis
- **Cache Management** - моніторинг та очищення кешу
- **Webhook Management** - налаштування webhook endpoints
- **System Status** - статус всіх компонентів

### 📊 Analytics Features / Аналітичні функції
- **Performance Metrics** - метрики продуктивності
- **ML Metrics** - метрики машинного навчання
- **Error Tracking** - відстеження помилок
- **Usage Analytics** - аналітика використання

## Technology Stack / Технологічний стек

### Backend
- **FastAPI** - асинхронний веб-фреймворк
- **Pydantic** - валідація даних
- **WebSockets** - real-time комунікація
- **Uvicorn** - ASGI сервер

### Frontend
- **React 18** - UI бібліотека
- **TypeScript** - типізація
- **Tailwind CSS** - стилізація
- **Monaco Editor** - код редактор
- **React Query** - управління станом
- **React Router** - маршрутизація

### Development Tools
- **Vite** - збірка фронтенду
- **ESLint + Prettier** - код стиль
- **Jest + Testing Library** - тестування
- **Docker** - контейнеризація

## Project Structure / Структура проекту

```
web_interface/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── public/
│   └── package.json
├── shared/
│   └── types/
└── docker/
```

## Development Plan / План розробки

### Phase 1: Backend API (Week 1)
- [ ] FastAPI setup
- [ ] CLI command API endpoints
- [ ] File upload/download
- [ ] WebSocket support
- [ ] Authentication

### Phase 2: Frontend Foundation (Week 2)
- [ ] React + TypeScript setup
- [ ] Basic routing
- [ ] API client
- [ ] Component library
- [ ] Basic layout

### Phase 3: Core Features (Week 3)
- [ ] Dashboard
- [ ] File editor
- [ ] Protocol management
- [ ] System monitoring

### Phase 4: Advanced Features (Week 4)
- [ ] ML integration
- [ ] Real-time updates
- [ ] Advanced analytics
- [ ] Settings management

### Phase 5: Polish & Deploy (Week 5)
- [ ] Testing
- [ ] Documentation
- [ ] Docker setup
- [ ] Production deployment

## Getting Started / Початок роботи

### Prerequisites / Вимоги
- Python 3.8+
- Node.js 18+
- Redis (опціонально)
- MOVA 2.2 SDK

### Installation / Встановлення

```bash
# Backend
cd web_interface/backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd web_interface/frontend
npm install
npm run dev
```

### Development / Розробка

```bash
# Backend development
cd backend
uvicorn main:app --reload --port 8000

# Frontend development
cd frontend
npm run dev

# Testing
npm run test
```

## API Documentation / Документація API

API документація буде доступна за адресою: `http://localhost:8000/docs`

## Contributing / Внесок

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License / Ліцензія

GPL v3 - така ж як і основний проект MOVA 