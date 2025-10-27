# Excel AI Processor с PydanticAI

> Интеллектуальная система обработки Excel/CSV файлов с использованием локальной LLM и PydanticAI

## 🎯 Возможности

- **📊 Анализ данных**: Автоматический анализ структуры, статистики, ответы на вопросы
- **✏️ Трансформация**: Изменение данных через естественный язык (pandas под капотом)
- **📈 Визуализация**: Создание графиков и диаграмм (matplotlib)
- **💾 Экспорт**: Сохранение в Excel/CSV с форматированием

## 🏗️ Архитектура

```
┌─────────────────┐
│  React Frontend │
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│  FastAPI Backend│
│                 │
│  Router Agent   │ ← Классификация намерений
│       ↓         │
│  ┌─────────┐   │
│  │Analysis │   │ ← Анализ данных
│  │Transform│   │ ← Трансформация (pandas)
│  │Visualize│   │ ← Графики (matplotlib)
│  │ Export  │   │ ← Экспорт файлов
│  └─────────┘   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Local LLM      │
│  (Ollama)       │
└─────────────────┘
```

## 🚀 Быстрый старт

### 1. Установка Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Или скачать с https://ollama.com/download
```

### 2. Загрузка модели

```bash
# Рекомендуется llama3.2 или llama3.1
ollama pull llama3.2:latest

# Или другая модель
ollama pull mistral:latest
```

### 3. Установка Python зависимостей

```bash
cd backend
python -m pip install -r requirements.txt

# Или с помощью poetry/uv
uv pip install -r requirements.txt
```

### 4. Настройка конфигурации

```bash
# Скопировать .env.example
cd backend
cp .env.example .env

# Отредактировать при необходимости
nano .env
```

### 5. Запуск бэкенда

```bash
cd backend
python -m app.main

# Или через uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на `http://localhost:8000`

API документация доступна на `http://localhost:8000/docs`

### 6. Установка фронтенда

```bash
cd frontend

# Установить зависимости
npm install
# или
yarn install
```

### 7. Запуск фронтенда

```bash
cd frontend
npm run dev
```

Фронтенд запустится на `http://localhost:5173`

## 📋 Примеры использования

### Анализ данных
```
"Сколько строк в файле?"
"Какие столбцы есть?"
"Покажи топ-10 товаров по количеству"
"Какая средняя цена?"
```

### Трансформация
```
"Добавь столбец Общая_Сумма = количество * цена"
"Удали строки где количество = 0"
"Отсортируй по дате по убыванию"
"Сгруппируй по регионам и посчитай сумму"
```

### Визуализация
```
"Построй график продаж по месяцам"
"Покажи столбчатую диаграмму по регионам"
"Круговая диаграмма долей товаров"
```

### Экспорт
```
"Сохрани в Excel"
"Экспортируй в CSV"
```

## 🛠️ Структура проекта

```
excel-ai-processor/
├── backend/
│   ├── app/
│   │   ├── agents/              # PydanticAI агенты
│   │   ├── tools/               # Инструменты
│   │   ├── models/              # Pydantic модели
│   │   ├── api/                 # API endpoints
│   │   └── utils/               # Утилиты
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   └── App.tsx
│   └── package.json
│
└── README.md
```

## 🔒 Безопасность

Система использует многоуровневую валидацию для безопасного выполнения кода:

1. **AST парсинг** - проверка синтаксиса и структуры
2. **Whitelist операций** - только разрешённые pandas функции
3. **Dry-run** - тестирование на sample данных
4. **Timeout** - ограничение времени выполнения
5. **Результат валидация** - проверка корректности результата

## 📝 API Endpoints

```
POST   /api/sessions              # Создать новую сессию
POST   /api/upload                # Загрузить файл
POST   /api/chat                  # Отправить сообщение
GET    /api/preview/{session_id}  # Получить preview данных
GET    /api/download/{file_id}    # Скачать файл
DELETE /api/sessions/{session_id} # Удалить сессию
GET    /api/visualizations/{viz_id} # Получить график
```

## 🧪 Тестирование

```bash
# Установка dev зависимостей
pip install -e ".[dev]"

# Запуск тестов
pytest

# С покрытием
pytest --cov=app
```

## 🔧 Конфигурация

### Настройки LLM

```python
# backend/app/config.py
LLM_MODEL = "llama3.2:latest"  # Модель Ollama
LLM_BASE_URL = "http://localhost:11434"  # URL Ollama
LLM_TIMEOUT = 300  # Таймаут в секундах
```

### Настройки файлов

```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}
```

## 📚 Документация

Полная документация доступна в директории `docs/`:

- [Quickstart Guide](docs/QUICKSTART.md) - быстрый старт
- [Architecture](docs/ARCHITECTURE.md) - детальная архитектура
- [Implementation Plan](docs/IMPLEMENTATION.md) - план реализации

## 🤝 Contributing

Pull requests приветствуются!

## 📄 License

MIT

## 🙋 FAQ

**Q: Какие модели LLM поддерживаются?**
A: Любые модели Ollama. Рекомендуется llama3.2, llama3.1, mistral.

**Q: Можно ли использовать OpenAI API?**
A: Да, нужно изменить клиент в `utils/llm_client.py`.

**Q: Какой размер файлов поддерживается?**
A: По умолчанию до 100MB, можно увеличить в config.py.

**Q: Безопасно ли выполнять сгенерированный код?**
A: Да, код проходит валидацию через AST и whitelist операций.

## 📧 Контакты

Для вопросов и предложений создайте issue в репозитории.
