# 🚀 Excel AI Processor - Быстрый старт

## За 5 минут до запуска

### Шаг 1: Установка Backend

```bash
cd backend
pip install -r requirements.txt
```

### Шаг 2: Настройка OpenAI API ключа

**Получите ключ:**
1. Зайдите на https://platform.openai.com/api-keys
2. Создайте новый API ключ
3. Добавьте платежную информацию в аккаунт

**Создайте .env файл:**
```bash
cd backend
cp .env.example .env
nano .env
```

**Добавьте ваш ключ:**
```ini
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_PROVIDER=openai
```

### Шаг 3: Запуск

**Backend:**
```bash
cd backend
export OPENAI_API_KEY="sk-your-key-here"
python3 -m app.main
```

Сервер запустится на **http://localhost:8000**

**Frontend (опционально):**
```bash
cd frontend
npm install
npm run dev
```

Фронтенд запустится на **http://localhost:5173**

### Шаг 4: Тестирование

**Откройте API документацию:**
```
http://localhost:8000/docs
```

**Или используйте curl:**

```bash
# 1. Создать сессию
SESSION_ID=$(curl -s -X POST http://localhost:8000/api/sessions | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# 2. Загрузить CSV файл
curl -X POST "http://localhost:8000/api/upload?session_id=$SESSION_ID" \
  -F "file=@your-file.csv"

# 3. Задать вопрос AI
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"Сколько строк в файле?\"
  }"
```

## 📋 Примеры запросов к AI

### Анализ
```
"Сколько строк и столбцов в файле?"
"Покажи первые 10 строк"
"Какая средняя цена?"
"Топ-5 товаров по количеству"
```

### Трансформация
```
"Добавь столбец 'Сумма' = количество * цена"
"Удали строки где цена < 100"
"Отсортируй по дате по убыванию"
"Сгруппируй по регионам и посчитай сумму"
```

### Визуализация
```
"Построй график продаж по месяцам"
"Столбчатая диаграмма по категориям"
"Круговая диаграмма долей товаров"
```

### Экспорт
```
"Сохрани в Excel"
"Экспортируй в CSV"
```

## ⚠️ Troubleshooting

### Ошибка 403 Access denied

**Проблема:** OpenAI API ключ недействителен

**Решение:**
1. Проверьте ключ: https://platform.openai.com/api-keys
2. Добавьте платежную информацию
3. Создайте новый ключ
4. Проверьте квоты: https://platform.openai.com/usage

**Альтернатива - используйте Ollama (бесплатно):**
```bash
# Установка Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Загрузка модели
ollama pull llama3.2:latest

# Обновите .env
echo "LLM_PROVIDER=ollama" >> backend/.env
echo "LLM_MODEL=llama3.2:latest" >> backend/.env

# Перезапустите сервер
```

### Port уже занят

```bash
# Найти процесс на порту 8000
lsof -ti:8000 | xargs kill -9

# Или используйте другой порт
uvicorn app.main:app --port 8001
```

## 📚 Документация

- **Полная документация**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **Отчет о тестировании**: [TEST_REPORT.md](TEST_REPORT.md)
- **API Docs**: http://localhost:8000/docs
- **README**: [README.md](README.md)

## 🎯 Что дальше?

1. Изучите полную документацию
2. Попробуйте разные типы запросов
3. Интегрируйте с вашими системами
4. Настройте под ваши нужды

**Готово! Теперь вы можете анализировать Excel файлы с помощью AI! 🎉**
