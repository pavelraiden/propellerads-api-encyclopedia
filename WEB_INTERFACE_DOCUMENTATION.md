# 🌐 PropellerAds Web Interface

## 📋 Обзор

Веб-интерфейс PropellerAds - это современное веб-приложение, которое предоставляет удобный графический интерфейс для управления PropellerAds API и взаимодействия с Claude AI.

## ✨ Возможности

### 🎯 Основные функции
- **Дашборд в реальном времени** - мониторинг баланса, кампаний и статистики
- **Интеграция с Claude AI** - чат-интерфейс для получения советов и анализа
- **Управление кампаниями** - просмотр и управление рекламными кампаниями
- **Статистика и аналитика** - детальные отчеты по производительности
- **WebSocket поддержка** - обновления в реальном времени

### 🛠 Технологии
- **Backend**: Flask + SocketIO
- **Frontend**: Bootstrap 5 + HTMX + Alpine.js
- **Real-time**: WebSocket connections
- **API Integration**: PropellerAds API + Claude AI

## 🚀 Быстрый запуск

### Установка зависимостей
```bash
cd web_interface
pip install -r requirements.txt
```

### Настройка переменных окружения
```bash
export MainAPI="your-propellerads-api-key"
export ANTHROPIC_API_KEY="your-claude-api-key"  # Опционально
export FLASK_SECRET_KEY="your-secret-key"       # Для production
```

### Запуск в режиме разработки
```bash
python app.py
```

### Запуск в production режиме
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:application
```

## 📁 Структура проекта

```
web_interface/
├── app.py                 # Основное Flask приложение
├── wsgi.py               # WSGI entry point для production
├── requirements.txt      # Python зависимости
├── templates/           # HTML шаблоны
│   ├── base.html        # Базовый шаблон
│   ├── dashboard.html   # Главная страница дашборда
│   └── chat.html        # Интерфейс чата с Claude
└── static/             # Статические файлы
    ├── css/
    │   └── custom.css   # Пользовательские стили
    └── js/
        └── app.js       # JavaScript функциональность
```

## 🎨 Интерфейс

### Дашборд (`/`)
- **Метрики в реальном времени**: баланс аккаунта, количество кампаний
- **Статус API**: индикаторы подключения к PropellerAds и Claude
- **Быстрые действия**: обновление баланса, загрузка кампаний
- **Таблица кампаний**: список активных кампаний с основной информацией

### Чат с Claude (`/chat`)
- **Интерактивный чат**: общение с Claude AI на естественном языке
- **Быстрые вопросы**: предустановленные запросы для частых задач
- **История чата**: сохранение переписки в localStorage
- **Статус индикатор**: показывает доступность Claude AI

## 🔌 API Endpoints

### Статус и мониторинг
- `GET /api/status` - Проверка статуса подключений
- `GET /api/balance` - Получение баланса аккаунта
- `GET /api/campaigns` - Список кампаний
- `GET /api/statistics` - Статистика по кампаниям

### Claude AI интеграция
- `POST /api/chat` - Отправка сообщения Claude AI

### WebSocket события
- `connect` - Подключение клиента
- `get_live_stats` - Запрос статистики в реальном времени
- `live_stats` - Получение обновленной статистики

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `MainAPI` | API ключ PropellerAds | ✅ |
| `ANTHROPIC_API_KEY` | API ключ Claude AI | ❌ |
| `FLASK_SECRET_KEY` | Секретный ключ Flask | ❌ (для production) |
| `FLASK_DEBUG` | Режим отладки | ❌ |
| `HOST` | Хост для запуска | ❌ (по умолчанию 127.0.0.1) |
| `PORT` | Порт для запуска | ❌ (по умолчанию 5000) |

### Конфигурация Flask
```python
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
```

## 🔒 Безопасность

### Рекомендации для production
1. **Установите надежный SECRET_KEY**
2. **Отключите DEBUG режим**
3. **Используйте HTTPS**
4. **Настройте CORS правильно**
5. **Ограничьте доступ к API endpoints**

### Обработка ошибок
- Централизованная обработка ошибок Flask
- Логирование всех API запросов
- Graceful handling недоступности внешних API

## 📊 Мониторинг

### Логирование
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Метрики
- Статус подключения к PropellerAds API
- Статус подключения к Claude AI
- Время последнего обновления данных
- Количество активных WebSocket соединений

## 🚀 Деплой

### Локальный деплой
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python app.py
```

### Production деплой с Gunicorn
```bash
# Установка Gunicorn
pip install gunicorn[eventlet]

# Запуск с WebSocket поддержкой
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:application
```

### Docker деплой
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "wsgi:application"]
```

## 🐛 Устранение неполадок

### Частые проблемы

1. **"PropellerAds client not initialized"**
   - Проверьте переменную окружения `MainAPI`
   - Убедитесь, что API ключ корректный

2. **"Claude interface not available"**
   - Установите переменную `ANTHROPIC_API_KEY`
   - Проверьте доступность Anthropic API

3. **WebSocket соединение не работает**
   - Убедитесь, что используете eventlet worker
   - Проверьте настройки CORS

### Логи и отладка
```bash
# Включить подробные логи
export FLASK_DEBUG=true

# Запуск с логированием
python app.py 2>&1 | tee app.log
```

## 📈 Производительность

### Оптимизации
- Кэширование API ответов
- Асинхронные запросы к внешним API
- Минификация статических файлов
- Gzip сжатие

### Рекомендации
- Используйте CDN для статических файлов
- Настройте кэширование на уровне веб-сервера
- Мониторьте использование памяти

## 🔄 Обновления

### Версионирование
Веб-интерфейс следует семантическому версионированию основного проекта.

### Миграции
При обновлении проверьте:
- Совместимость с новыми версиями API
- Изменения в структуре данных
- Обновления зависимостей

## 🤝 Вклад в разработку

### Разработка
1. Форкните репозиторий
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

### Стиль кода
- Следуйте PEP 8 для Python
- Используйте ESLint для JavaScript
- Документируйте все функции

---

**Версия**: 1.0.0  
**Последнее обновление**: Октябрь 2025  
**Поддержка**: [GitHub Issues](https://github.com/pavelraiden/propellerads-api-encyclopedia/issues)
