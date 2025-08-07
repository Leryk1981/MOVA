# 🚀 Швидкий старт - Веб-інтерфейс MOVA 2.2

## ✅ Статус: Готово до використання!

Веб-інтерфейс MOVA 2.2 успішно запущений та функціональний.

## 🌐 Доступні URL

### Frontend (React)
- **Головна сторінка**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard
- **Editor**: http://localhost:3000/editor
- **ML Dashboard**: http://localhost:3000/ml
- **System Monitor**: http://localhost:3000/monitor
- **Files**: http://localhost:3000/files

### Backend (FastAPI)
- **API Documentation**: http://localhost:8000/api/docs
- **System Status**: http://localhost:8000/api/system/status
- **Health Check**: http://localhost:8000/api/system/health

## 🔧 Запуск серверів

### Backend (FastAPI)
```bash
cd web_interface/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)
```bash
cd web_interface/frontend
npm run dev
```

## 📱 Функціональність

### 🏠 Dashboard
- Реальний час статус системи
- Метрики продуктивності (CPU, Memory, Disk)
- Кількість активних протоколів
- Кількість ML моделей
- Швидкі дії

### 📝 Editor
- Monaco Editor з підсвіткою синтаксису
- Підтримка MOVA файлів
- Автодоповнення
- Збереження файлів

### 🤖 ML Dashboard
- Управління ML моделями
- Тренування моделей
- Аналіз тексту (Intent, Entities, Sentiment)
- Метрики ML
- Рекомендації

### 📊 System Monitor
- Графіки в реальному часі
- Моніторинг ресурсів
- Статус компонентів
- Системна інформація

### 📁 Files
- Управління файлами
- Завантаження/вивантаження
- Створення папок
- Пошук файлів

## 🎨 Дизайн

- **Адаптивний дизайн** - працює на всіх пристроях
- **Темна/світла тема** - автоматичне перемикання
- **Сучасний UI** - Tailwind CSS + Heroicons
- **Плавні анімації** - CSS transitions

## 🔌 API Інтеграція

### Доступні endpoints (44 total):
- **System**: 8 endpoints
- **Files**: 8 endpoints  
- **CLI**: 8 endpoints
- **ML**: 12 endpoints
- **Redis**: 4 endpoints
- **Cache**: 4 endpoints

### Приклад використання:
```typescript
// Отримання статусу системи
const status = await apiService.getSystemStatus();

// Отримання ML моделей
const models = await apiService.getMLModels();

// Отримання метрик
const metrics = await apiService.getSystemMetrics('1h');
```

## 🛠 Технології

### Frontend
- **React 18** - UI framework
- **TypeScript** - типізація
- **Vite** - build tool
- **Tailwind CSS** - стилізація
- **React Query** - кешування
- **Zustand** - state management
- **React Router** - маршрутизація
- **Monaco Editor** - код редактор
- **Recharts** - графіки

### Backend
- **FastAPI** - API framework
- **Pydantic** - валідація
- **Uvicorn** - ASGI server
- **WebSockets** - real-time
- **Redis** - кешування
- **SQLAlchemy** - ORM

## 🚨 Вирішення проблем

### Фронтенд не відображається
1. Перевірте, чи запущений сервер: `netstat -an | findstr :3000`
2. Перезапустіть: `cd web_interface/frontend && npm run dev`

### Бекенд не відповідає
1. Перевірте, чи запущений сервер: `netstat -an | findstr :8000`
2. Перезапустіть: `cd web_interface/backend && uvicorn main:app --reload`

### Помилки імпорту іконок
- Використовуйте правильні назви Heroicons
- Замініть `DatabaseIcon` на `CircleStackIcon`
- Замініть `SaveIcon` на `ArrowDownTrayIcon`

### CORS помилки
- Бекенд налаштований для localhost:3000
- Перевірте налаштування в `main.py`

## 📈 Моніторинг

### Реальний час метрики:
- CPU використання
- Використання пам'яті
- Дисковий простір
- Мережева активність
- MOVA метрики

### Автоматичне оновлення:
- Dashboard: кожні 30 секунд
- Monitor: кожні 5-10 секунд
- ML: кожні 15-60 секунд

## 🎯 Наступні кроки

1. **Відкрийте браузер** і перейдіть на http://localhost:3000
2. **Ознайомтеся з Dashboard** - перегляньте статус системи
3. **Спробуйте Editor** - створіть або відредагуйте MOVA файл
4. **Перевірте Monitor** - подивіться на метрики в реальному часі
5. **Тестуйте ML** - працюйте з машинним навчанням

## 🎉 Готово!

**Веб-інтерфейс MOVA 2.2 повністю функціональний та готовий до використання!**

Якщо виникають питання або проблеми, звертайтеся до документації або створюйте issues.

---
*Останнє оновлення: 7 серпня 2025* 