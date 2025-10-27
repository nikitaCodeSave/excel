"""
Transform Agent - трансформация данных через pandas
"""
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd

from app.config import settings
from app.tools.file_manager import file_manager
from app.tools.code_validator import code_validator
from app.tools.pandas_executor import pandas_executor
from app.models.schemas import AgentResponse, IntentType, TransformOperation


# Системный промпт для Transform Agent
TRANSFORM_SYSTEM_PROMPT = """Ты - эксперт по pandas для трансформации данных.

Твоя задача - преобразовать запрос пользователя в pandas операции.

ВАЖНО: Всегда используй переменную 'df' для DataFrame. Код должен модифицировать df напрямую.

Примеры:

Запрос: "Добавь столбец 'Общая сумма' как произведение количества на цену"
Код: df['Общая сумма'] = df['количество'] * df['цена']

Запрос: "Удали строки где количество = 0"
Код: df = df[df['количество'] != 0]

Запрос: "Отсортируй по дате по убыванию"
Код: df = df.sort_values('дата', ascending=False)

Запрос: "Переведи названия товаров в верхний регистр"
Код: df['товар'] = df['товар'].str.upper()

Запрос: "Сгруппируй по регионам и посчитай сумму продаж"
Код: df = df.groupby('регион')['продажи'].sum().reset_index()

Запрос: "Заполни пустые значения в столбце 'цена' нулями"
Код: df['цена'] = df['цена'].fillna(0)

Правила:
1. Используй ТОЛЬКО pandas и numpy операции
2. НЕ используй eval, exec, import, open, file, os, subprocess
3. Код должен быть безопасным и эффективным
4. Всегда работай с переменной 'df'
5. Если операция изменяет df, обязательно присваивай результат обратно: df = ...

Инструменты:
- get_column_names: получить список столбцов
- preview_data: предпросмотр данных
"""


class TransformDependencies(BaseModel):
    """Зависимости для Transform Agent"""
    session_id: str
    user_message: str


class PandasCode(BaseModel):
    """Сгенерированный pandas код"""
    code: str = Field(description="Pandas код для выполнения")
    description: str = Field(description="Описание операции")
    affected_columns: List[str] = Field(
        default=[],
        description="Список столбцов, которые будут изменены"
    )


# Создаём Transform Agent
# Определяем модель в зависимости от провайдера
_model_string = (
    f"{settings.LLM_PROVIDER}:{settings.LLM_MODEL}"
    if settings.LLM_PROVIDER == "openai"
    else f"ollama:{settings.LLM_MODEL}"
)

transform_agent = Agent[TransformDependencies, PandasCode](
    model=_model_string,
    deps_type=TransformDependencies,
    system_prompt=TRANSFORM_SYSTEM_PROMPT,
    retries=3,
)


@transform_agent.tool
def get_column_names(ctx: RunContext[TransformDependencies]) -> List[str]:
    """Получить список столбцов DataFrame"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    return df.columns.tolist()


@transform_agent.tool
def preview_data(
    ctx: RunContext[TransformDependencies],
    rows: int = 5
) -> List[Dict[str, Any]]:
    """Предпросмотр данных"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    sample = df.head(rows).to_dict('records')

    # Очистка от NaN
    cleaned = []
    for record in sample:
        clean_record = {}
        for key, value in record.items():
            if pd.isna(value):
                clean_record[key] = None
            else:
                clean_record[key] = value
        cleaned.append(clean_record)

    return cleaned


@transform_agent.tool
def get_dataframe_shape(ctx: RunContext[TransformDependencies]) -> Dict[str, int]:
    """Получить размеры DataFrame"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    return {"rows": len(df), "columns": len(df.columns)}


async def transform_data(
    session_id: str,
    user_message: str
) -> AgentResponse:
    """
    Трансформировать данные на основе запроса пользователя

    Args:
        session_id: ID сессии
        user_message: Сообщение пользователя

    Returns:
        AgentResponse с результатами трансформации
    """
    try:
        # Проверяем наличие файла
        if not file_manager.session_exists(session_id):
            return AgentResponse(
                success=False,
                message="Сессия не найдена",
                error="Session not found"
            )

        # Загружаем текущий DataFrame
        df_original = file_manager.load_dataframe(session_id)

        # Запускаем агента для генерации кода
        deps = TransformDependencies(
            session_id=session_id,
            user_message=user_message
        )

        result = await transform_agent.run(user_message, deps=deps)
        pandas_code: PandasCode = result.data

        # Валидация кода
        validation = code_validator.validate(pandas_code.code)
        if not validation.is_valid:
            return AgentResponse(
                success=False,
                message="Сгенерированный код не прошёл валидацию",
                intent=IntentType.TRANSFORM,
                error="\n".join(validation.errors)
            )

        # Выполнение кода
        success, df_result, exec_message = pandas_executor.execute(
            df_original,
            pandas_code.code,
            dry_run=True
        )

        if not success:
            return AgentResponse(
                success=False,
                message=f"Ошибка при выполнении операции: {exec_message}",
                intent=IntentType.TRANSFORM,
                error=exec_message
            )

        # Валидация результата
        is_valid, validation_message = pandas_executor.validate_result(
            df_original,
            df_result
        )

        if not is_valid:
            return AgentResponse(
                success=False,
                message=f"Результат не прошёл валидацию: {validation_message}",
                intent=IntentType.TRANSFORM,
                error=validation_message
            )

        # Сохраняем результат
        file_manager.save_dataframe(session_id, df_result)

        # Получаем preview изменений
        changes = pandas_executor.preview_changes(df_original, df_result)
        summary = pandas_executor.get_operation_summary(df_original, df_result)

        return AgentResponse(
            success=True,
            message=f"✅ Операция выполнена успешно!\n\n{pandas_code.description}\n\n{summary}",
            intent=IntentType.TRANSFORM,
            data={
                "operation": {
                    "code": pandas_code.code,
                    "description": pandas_code.description,
                    "affected_columns": pandas_code.affected_columns,
                },
                "changes": changes,
                "summary": summary,
            },
            preview=changes.get("sample_after", [])
        )

    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Ошибка при трансформации: {str(e)}",
            intent=IntentType.TRANSFORM,
            error=str(e)
        )


async def create_template(
    session_id: str,
    template_description: str
) -> AgentResponse:
    """
    Создать шаблон файла на основе описания

    Args:
        session_id: ID сессии
        template_description: Описание шаблона

    Returns:
        AgentResponse с созданным шаблоном
    """
    try:
        # Специальный промпт для создания шаблона
        prompt = f"""Создай pandas DataFrame для шаблона со следующим описанием:

{template_description}

Требования:
1. Создай DataFrame с подходящими столбцами
2. Добавь 3-5 примеров записей для демонстрации
3. Используй подходящие типы данных

Пример кода:
```python
import pandas as pd

df = pd.DataFrame({{
    'Столбец1': [значение1, значение2, ...],
    'Столбец2': [значение1, значение2, ...],
}})
```

Верни ТОЛЬКО pandas код для создания DataFrame."""

        deps = TransformDependencies(
            session_id=session_id,
            user_message=prompt
        )

        result = await transform_agent.run(prompt, deps=deps)
        pandas_code: PandasCode = result.data

        # Выполняем код для создания DataFrame
        namespace = {
            'pd': pd,
            'df': pd.DataFrame()
        }

        exec(pandas_code.code, namespace)
        df = namespace['df']

        # Сохраняем как текущий DataFrame
        file_manager.save_dataframe(session_id, df)

        return AgentResponse(
            success=True,
            message=f"✅ Шаблон создан!\n\n{pandas_code.description}",
            intent=IntentType.TRANSFORM,
            data={
                "template": {
                    "code": pandas_code.code,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist(),
                }
            },
            preview=df.head(10).to_dict('records')
        )

    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Ошибка при создании шаблона: {str(e)}",
            intent=IntentType.TRANSFORM,
            error=str(e)
        )
