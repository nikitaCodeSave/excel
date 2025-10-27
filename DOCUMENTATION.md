# Excel AI Processor - Полная документация

## 📑 Содержание

1. [Описание проекта](#описание-проекта)
2. [Архитектура](#архитектура)
3. [Установка и настройка](#установка-и-настройка)
4. [API Документация](#api-документация)
5. [Использование](#использование)
6. [AI Агенты](#ai-агенты)
7. [Конфигурация](#конфигурация)
8. [Troubleshooting](#troubleshooting)

---

## Описание проекта

**Excel AI Processor** - интеллектуальная система обработки Excel/CSV файлов с использованием AI агентов на базе PydanticAI и OpenAI API.

### ✨ Основные возможности:

- 📊 **Анализ данных**: Автоматический анализ структуры, статистики, ответы на вопросы
- ✏️ **Трансформация**: Изменение данных через естественный язык (pandas под капотом)
- 📈 **Визуализация**: Создание графиков и диаграмм (matplotlib)
- 💾 **Экспорт**: Сохранение в Excel/CSV с форматированием

### 🔧 Технологии:

- **Backend**: FastAPI 0.120.0, Python 3.11+
- **AI**: PydanticAI 1.6.0, OpenAI API (gpt-4o-mini)
- **Data Processing**: Pandas 2.3.0, NumPy 2.3.4
- **Visualization**: Matplotlib 3.10.7
- **Frontend**: React 19.2, Vite 7, Tailwind CSS v4

---

## Архитектура

### Общая схема

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│                  (http://localhost:5173)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│                  (http://localhost:8000)                 │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │          Router Agent (Intent Classifier)        │   │
│  └────────────────────┬────────────────────────────┘   │
│                       │                                  │
│       ┌───────────────┼───────────────┐                 │
│       ▼               ▼               ▼                  │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐             │
│  │Analysis │   │Transform │   │Visualize │   Export     │
│  │ Agent   │   │ Agent    │   │ Agent    │   Agent      │
│  └─────────┘   └──────────┘   └──────────┘             │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Tools & Utilities                     │  │
│  │  • FileManager  • PandasExecutor  • CodeValidator │  │
│  └───────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │   OpenAI API / Ollama  │
          │   (gpt-4o-mini)        │
          └────────────────────────┘
```

### Компоненты Backend

#### 1. **Router Agent**
- Классифицирует намерения пользователя
- Определяет какой агент должен обработать запрос
- Типы намерений: `ANALYSIS`, `TRANSFORM`, `VISUALIZE`, `EXPORT`, `GENERAL`

#### 2. **Analysis Agent**
- Анализирует данные из загруженных файлов
- Отвечает на вопросы о структуре и содержимом
- Инструменты:
  - `get_dataframe_info` - общая информация о DataFrame
  - `get_column_statistics` - статистика по столбцам
  - `query_data` - запросы к данным (топ-N, фильтрация)

#### 3. **Transform Agent**
- Генерирует и выполняет pandas код для трансформации
- Валидирует код перед выполнением (AST parsing, whitelist операций)
- Инструменты:
  - `get_column_names` - список столбцов
  - `preview_data` - предпросмотр данных
  - `get_dataframe_shape` - размеры DataFrame

#### 4. **Visualization Agent**
- Создает графики на основе данных
- Поддерживает типы: line, bar, scatter, pie, histogram, boxplot
- Инструменты:
  - `get_column_names` - все столбцы
  - `get_numeric_columns` - числовые столбцы
  - `get_categorical_columns` - категориальные столбцы

#### 5. **Export Agent**
- Экспортирует данные в Excel/CSV
- Поддерживает конвертацию форматов

### Безопасность

Система использует многоуровневую валидацию для безопасного выполнения кода:

1. **AST парсинг** - проверка синтаксиса и структуры
2. **Whitelist операций** - только разрешённые pandas функции
3. **Dry-run** - тестирование на sample данных
4. **Timeout** - ограничение времени выполнения (60 сек)
5. **Result validation** - проверка корректности результата

---

## Установка и настройка

### Системные требования

- **Python**: 3.11+ (3.12+ рекомендуется)
- **Node.js**: 20.19+ или 22.12+
- **ОС**: Linux, macOS, Windows

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/excel-ai-processor.git
cd excel-ai-processor
```

### 2. Backend Setup

#### Установка Python зависимостей

```bash
cd backend

# Создание виртуального окружения (рекомендуется)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

#### Настройка .env файла

```bash
cp .env.example .env
nano .env
```

Обязательные параметры:

```ini
# OpenAI Settings (ОБЯЗАТЕЛЬНО)
OPENAI_API_KEY=sk-...your-key-here...

# LLM Settings
LLM_MODEL=gpt-4o-mini
LLM_PROVIDER=openai  # или ollama для локальной LLM

# API Settings
API_V1_PREFIX=/api
PROJECT_NAME=Excel AI Processor

# CORS (для фронтенда)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Получение OpenAI API ключа

1. Зайдите на https://platform.openai.com/api-keys
2. Создайте новый API ключ
3. **Важно**: Добавьте платежную информацию в аккаунт OpenAI
4. Скопируйте ключ в `.env` файл

### 3. Frontend Setup

```bash
cd frontend

# Установка зависимостей
npm install
# или
yarn install
```

### 4. Запуск приложения

#### Запуск Backend

```bash
cd backend

# Экспорт API ключа (если не в .env)
export OPENAI_API_KEY="sk-..."

# Запуск сервера
python3 -m app.main

# Или через uvicorn с hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на **http://localhost:8000**

API документация: **http://localhost:8000/docs**

#### Запуск Frontend

```bash
cd frontend

npm run dev
```

Фронтенд запустится на **http://localhost:5173**

---

## API Документация

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### 1. Создание сессии

**POST** `/sessions`

Создает новую сессию для работы с файлами.

**Request:**
```json
{}
```

**Response:**
```json
{
  "session_id": "uuid-v4",
  "created_at": "2025-10-27T12:00:00Z"
}
```

#### 2. Загрузка файла

**POST** `/upload?session_id={session_id}`

Загружает Excel или CSV файл.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: файл (CSV/XLSX/XLS)

**Response:**
```json
{
  "success": true,
  "file_id": "uuid-v4",
  "metadata": {
    "file_id": "uuid-v4",
    "original_filename": "data.csv",
    "file_size": 1234,
    "upload_timestamp": "2025-10-27T12:00:00",
    "rows": 100,
    "columns": 5,
    "column_names": ["А", "Б", "В", "Г", "Д"],
    "column_types": {
      "А": "object",
      "Б": "int64",
      ...
    }
  }
}
```

#### 3. Chat с AI агентом

**POST** `/chat`

Отправляет сообщение AI агенту для обработки.

**Request:**
```json
{
  "session_id": "uuid-v4",
  "message": "Сколько строк в файле?"
}
```

**Response:**
```json
{
  "success": true,
  "message": "В файле 100 строк",
  "intent": "analysis",
  "data": {
    "analysis_result": "..."
  },
  "preview": [...],
  "visualization_ids": null,
  "file_id": null,
  "error": null
}
```

#### 4. Предпросмотр данных

**GET** `/preview/{session_id}?limit=10`

Получить предпросмотр загруженных данных.

**Response:**
```json
{
  "data": [
    {"столбец1": "значение1", ...},
    ...
  ],
  "total_rows": 100,
  "total_columns": 5,
  "columns": ["столбец1", "столбец2", ...]
}
```

#### 5. Скачать файл

**GET** `/download/{file_id}`

Скачать экспортированный файл.

**Response:**
- Файл в формате Excel или CSV

#### 6. Получить визуализацию

**GET** `/visualizations/{viz_id}`

Получить созданный график.

**Response:**
- Изображение в формате PNG

#### 7. Удалить сессию

**DELETE** `/sessions/{session_id}`

Удалить сессию и все связанные файлы.

**Response:**
```json
{
  "success": true,
  "message": "Session deleted"
}
```

---

## Использование

### Примеры запросов

#### Анализ данных

```bash
# 1. Создать сессию
SESSION_ID=$(curl -X POST http://localhost:8000/api/sessions | jq -r '.session_id')

# 2. Загрузить файл
curl -X POST "http://localhost:8000/api/upload?session_id=$SESSION_ID" \
  -F "file=@data.csv"

# 3. Задать вопросы
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Сколько строк в файле и какие столбцы есть?\"
  }"

curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Какая средняя цена?\"
  }"
```

#### Трансформация данных

```bash
# Добавить новый столбец
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Добавь столбец 'Общая сумма' = количество * цена\"
  }"

# Фильтрация данных
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Удали строки где цена меньше 50\"
  }"
```

#### Визуализация

```bash
# Создать график
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Построй столбчатую диаграмму продаж по регионам\"
  }"
```

#### Экспорт

```bash
# Экспортировать в Excel
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Сохрани в Excel\"
  }"
```

---

## AI Агенты

### Router Agent

**Назначение:** Классификация намерений пользователя

**Модель:** `gpt-4o-mini`

**Промпт:**
```
Ты - классификатор намерений пользователя для системы работы с Excel/CSV файлами.
Определи категорию запроса: ANALYSIS, TRANSFORM, VISUALIZE, EXPORT или GENERAL.
```

**Примеры:**
- "Сколько строк?" → `ANALYSIS`
- "Добавь столбец" → `TRANSFORM`
- "Построй график" → `VISUALIZE`
- "Сохрани файл" → `EXPORT`

### Analysis Agent

**Назначение:** Анализ данных и ответы на вопросы

**Инструменты:**
- `get_dataframe_info()` - общая информация
- `get_column_statistics(column_name)` - статистика по столбцу
- `query_data(query_type, column_name, limit)` - запросы к данным

**Примеры запросов:**
- "Сколько строк и столбцов?"
- "Покажи первые 10 строк"
- "Какая средняя цена?"
- "Топ-5 товаров по количеству"
- "Какие уникальные значения в столбце Регион?"

### Transform Agent

**Назначение:** Трансформация данных через pandas

**Особенности:**
- Генерирует безопасный pandas код
- Валидирует код перед выполнением
- Тестирует на sample данных (dry-run)

**Примеры операций:**
```python
# Добавить столбец
df['Общая_Сумма'] = df['количество'] * df['цена']

# Фильтрация
df = df[df['количество'] > 0]

# Сортировка
df = df.sort_values('дата', ascending=False)

# Группировка
df = df.groupby('регион')['продажи'].sum().reset_index()
```

### Visualization Agent

**Назначение:** Создание графиков и диаграмм

**Типы графиков:**
- `line` - линейный график
- `bar` - столбчатая диаграмма
- `scatter` - точечная диаграмма
- `pie` - круговая диаграмма
- `hist` - гистограмма
- `box` - box plot

**Примеры:**
- "Построй график продаж по месяцам"
- "Столбчатая диаграмма по регионам"
- "Круговая диаграмма долей"
- "Гистограмма распределения цен"

---

## Конфигурация

### app/config.py

```python
class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Excel AI Processor"
    VERSION: str = "1.0.0"

    # LLM Settings
    LLM_MODEL: str = "gpt-4o-mini"  # или "llama3.2:latest" для Ollama
    LLM_PROVIDER: str = "openai"    # "openai" или "ollama"
    LLM_BASE_URL: str = "http://localhost:11434"  # Для Ollama
    LLM_TIMEOUT: int = 300  # 5 минут
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # File Storage
    UPLOAD_DIR: Path = Path("/tmp/excel_processor/sessions")
    EXPORT_DIR: Path = Path("/tmp/excel_processor/exports")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {".xlsx", ".xls", ".csv"}

    # Security
    ALLOWED_PANDAS_OPERATIONS: set = {
        "assign", "drop", "rename", "sort_values", "groupby",
        "merge", "fillna", "dropna", "apply", "map", "filter",
        "query", "loc", "iloc", "head", "tail", "sample",
        "sum", "mean", "median", "count", "min", "max", "std", "var",
        "upper", "lower", "strip", "replace", "contains", "split",
    }

    FORBIDDEN_CODE_PATTERNS: list = [
        "eval", "exec", "compile", "__import__", "open", "file",
        "input", "raw_input", "subprocess", "os.system", "commands",
        "pickle", "shelve", "socket", "urllib", "requests"
    ]

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
```

### Переменные окружения (.env)

```ini
# ОБЯЗАТЕЛЬНЫЕ
OPENAI_API_KEY=sk-...

# Опциональные
LLM_MODEL=gpt-4o-mini
LLM_PROVIDER=openai
API_V1_PREFIX=/api
PROJECT_NAME=Excel AI Processor

# Хранилище файлов
UPLOAD_DIR=/tmp/excel_processor/sessions
EXPORT_DIR=/tmp/excel_processor/exports

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Troubleshooting

### 1. Ошибка "403 Access denied" от OpenAI

**Причина:** Недействительный API ключ

**Решение:**
1. Проверьте ключ на https://platform.openai.com/api-keys
2. Убедитесь что добавлена платежная информация
3. Проверьте квоты: https://platform.openai.com/usage
4. Создайте новый API ключ
5. Обновите `.env` файл и перезапустите сервер

**Тест ключа:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 2. Использование Ollama (локальная LLM)

Если у вас нет OpenAI API ключа, используйте Ollama:

```bash
# 1. Установите Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Загрузите модель
ollama pull llama3.2:latest

# 3. Обновите .env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:latest
LLM_BASE_URL=http://localhost:11434

# 4. Запустите сервер
python3 -m app.main
```

### 3. Ошибка "ModuleNotFoundError"

**Решение:**
```bash
cd backend
pip install -r requirements.txt
```

### 4. Ошибка при загрузке файла

**Проблема:** "Session not found"

**Решение:**
- Убедитесь что сначала создали сессию через `/api/sessions`
- Используйте полученный `session_id` в запросе на загрузку

### 5. CORS ошибки

**Решение:**
Добавьте URL фронтенда в `.env`:
```ini
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://yourdomain.com
```

### 6. Timeout при выполнении операций

**Решение:**
Увеличьте таймауты в `config.py`:
```python
LLM_TIMEOUT: int = 600  # 10 минут
PANDAS_TIMEOUT: int = 120  # 2 минуты
```

---

## Примеры использования

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Создать сессию
response = requests.post(f"{BASE_URL}/sessions", json={})
session_id = response.json()["session_id"]

# 2. Загрузить файл
with open("data.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/upload",
        params={"session_id": session_id},
        files=files
    )
print(response.json())

# 3. Задать вопрос
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "session_id": session_id,
        "message": "Покажи первые 5 строк"
    }
)
print(response.json()["message"])

# 4. Трансформация
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "session_id": session_id,
        "message": "Добавь столбец 'Сумма' = количество * цена"
    }
)

# 5. Визуализация
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "session_id": session_id,
        "message": "Построй столбчатую диаграмму продаж"
    }
)
viz_id = response.json()["visualization_ids"][0]

# 6. Скачать график
response = requests.get(f"{BASE_URL}/visualizations/{viz_id}")
with open("chart.png", "wb") as f:
    f.write(response.content)
```

---

## Лицензия

MIT License

---

## Контакты

Для вопросов и предложений создайте issue в репозитории.

**Документация обновлена:** 2025-10-27
