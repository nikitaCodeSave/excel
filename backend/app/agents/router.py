"""
Router Agent - классификация намерений пользователя
"""
from pydantic_ai import Agent, RunContext
from typing import Optional
import json

from app.models.schemas import IntentType
from app.config import settings


# Системный промпт для роутера
ROUTER_SYSTEM_PROMPT = """Ты - классификатор намерений пользователя для системы работы с Excel/CSV файлами.

Твоя задача - определить, к какой категории относится запрос пользователя:

1. ANALYSIS - Анализ и вопросы о данных:
   - "Сколько строк в файле?"
   - "Какие столбцы есть?"
   - "Какие товары самые популярные?"
   - "Покажи первые 10 строк"
   - "Какая средняя цена?"

2. TRANSFORM - Изменение и обработка данных:
   - "Добавь столбец 'Общая сумма'"
   - "Удали строки где количество = 0"
   - "Отсортируй по дате"
   - "Сгруппируй по регионам"
   - "Переведи названия в верхний регистр"

3. VISUALIZE - Создание графиков и диаграмм:
   - "Построй график продаж"
   - "Покажи столбчатую диаграмму"
   - "Создай дашборд"
   - "Визуализируй распределение"

4. EXPORT - Экспорт и сохранение файлов:
   - "Сохрани файл"
   - "Экспортируй в CSV"
   - "Создай Excel файл с отчётом"
   - "Скачать результат"
   - "Конвертируй в Excel"

5. GENERAL - Общие вопросы и приветствия:
   - "Привет"
   - "Что ты умеешь?"
   - "Помоги мне"

Ответь ТОЛЬКО названием категории (ANALYSIS, TRANSFORM, VISUALIZE, EXPORT или GENERAL).
Ничего больше не добавляй.
"""


class RouterDependencies:
    """Зависимости для Router Agent"""
    pass


# Создаём Router Agent
router_agent = Agent(
    model=f"ollama:{settings.LLM_MODEL}",
    deps_type=RouterDependencies,
    system_prompt=ROUTER_SYSTEM_PROMPT,
)


async def classify_intent(user_message: str) -> IntentType:
    """
    Классифицировать намерение пользователя

    Args:
        user_message: Сообщение пользователя

    Returns:
        IntentType
    """
    try:
        # Получаем ответ от агента
        result = await router_agent.run(user_message)
        response_text = result.data.strip().upper()

        # Маппинг ответа в IntentType
        intent_mapping = {
            "ANALYSIS": IntentType.ANALYSIS,
            "TRANSFORM": IntentType.TRANSFORM,
            "VISUALIZE": IntentType.VISUALIZE,
            "EXPORT": IntentType.EXPORT,
            "GENERAL": IntentType.GENERAL,
        }

        # Ищем первое совпадение
        for key, intent in intent_mapping.items():
            if key in response_text:
                return intent

        # По умолчанию - GENERAL
        return IntentType.GENERAL

    except Exception as e:
        print(f"Error in intent classification: {str(e)}")
        # В случае ошибки - безопасный fallback
        return IntentType.GENERAL


async def route_message(user_message: str) -> tuple[IntentType, str]:
    """
    Маршрутизация сообщения пользователя

    Returns:
        Tuple[intent, explanation]
    """
    intent = await classify_intent(user_message)

    explanations = {
        IntentType.ANALYSIS: "Анализирую данные...",
        IntentType.TRANSFORM: "Трансформирую данные...",
        IntentType.VISUALIZE: "Создаю визуализацию...",
        IntentType.EXPORT: "Готовлю файл для экспорта...",
        IntentType.GENERAL: "Обрабатываю запрос...",
    }

    return intent, explanations.get(intent, "Обрабатываю...")
