"""
Analysis Agent - анализ данных из Excel/CSV
"""
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import json

from app.config import settings
from app.tools.file_manager import file_manager
from app.models.schemas import AgentResponse, IntentType


# Системный промпт для Analysis Agent
ANALYSIS_SYSTEM_PROMPT = """Ты - эксперт по анализу данных из Excel/CSV файлов.

Твоя задача - анализировать данные и отвечать на вопросы пользователя.

Доступные инструменты:
- get_dataframe_info: получить общую информацию о DataFrame (размер, столбцы, типы)
- get_column_statistics: получить статистику по конкретному столбцу
- query_data: выполнить запрос к данным (топ-N, поиск, фильтрация)

Примеры вопросов:
- "Сколько строк в файле?"
- "Какие столбцы есть?"
- "Покажи первые 10 строк"
- "Какие товары самые популярные?"
- "Какая средняя цена?"

Отвечай чётко и по делу, используя данные из инструментов.
"""


class AnalysisDependencies(BaseModel):
    """Зависимости для Analysis Agent"""
    session_id: str
    user_message: str


class DataFrameInfo(BaseModel):
    """Информация о DataFrame"""
    rows: int
    columns: int
    column_names: List[str]
    column_types: Dict[str, str]
    memory_usage: str
    sample_data: List[Dict[str, Any]]


class ColumnStatistics(BaseModel):
    """Статистика по столбцу"""
    column_name: str
    count: int
    unique: Optional[int] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    top_values: Optional[List[tuple]] = None


# Создаём Analysis Agent
analysis_agent = Agent(
    model=f"ollama:{settings.LLM_MODEL}",
    deps_type=AnalysisDependencies,
    system_prompt=ANALYSIS_SYSTEM_PROMPT,
    retries=2,
)


@analysis_agent.tool_plain
def get_dataframe_info(ctx: RunContext[AnalysisDependencies]) -> DataFrameInfo:
    """Получить общую информацию о DataFrame"""
    df = file_manager.load_dataframe(ctx.deps.session_id)

    # Получаем sample данных
    sample = df.head(10).to_dict('records')

    # Конвертируем типы в строки для JSON
    for record in sample:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
                record[key] = str(value)

    return DataFrameInfo(
        rows=len(df),
        columns=len(df.columns),
        column_names=df.columns.tolist(),
        column_types={col: str(dtype) for col, dtype in df.dtypes.items()},
        memory_usage=f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
        sample_data=sample
    )


@analysis_agent.tool_plain
def get_column_statistics(
    ctx: RunContext[AnalysisDependencies],
    column_name: str
) -> ColumnStatistics:
    """Получить статистику по конкретному столбцу"""
    df = file_manager.load_dataframe(ctx.deps.session_id)

    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found")

    col = df[column_name]

    stats = ColumnStatistics(
        column_name=column_name,
        count=int(col.count()),
        unique=int(col.nunique()) if col.dtype == 'object' or pd.api.types.is_categorical_dtype(col) else None
    )

    # Числовая статистика
    if pd.api.types.is_numeric_dtype(col):
        stats.mean = float(col.mean()) if not pd.isna(col.mean()) else None
        stats.std = float(col.std()) if not pd.isna(col.std()) else None
        stats.min = float(col.min()) if not pd.isna(col.min()) else None
        stats.max = float(col.max()) if not pd.isna(col.max()) else None
    else:
        # Для нечисловых - топ значения
        value_counts = col.value_counts().head(10)
        stats.top_values = [
            (str(val), int(count))
            for val, count in value_counts.items()
        ]

    return stats


@analysis_agent.tool_plain
def query_data(
    ctx: RunContext[AnalysisDependencies],
    query_type: str,
    column_name: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Выполнить запрос к данным

    Args:
        query_type: Тип запроса (top_values, first_rows, last_rows, random_sample)
        column_name: Имя столбца (для top_values)
        limit: Количество записей
    """
    df = file_manager.load_dataframe(ctx.deps.session_id)

    result = {"query_type": query_type}

    if query_type == "top_values" and column_name:
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found")

        value_counts = df[column_name].value_counts().head(limit)
        result["data"] = [
            {"value": str(val), "count": int(count)}
            for val, count in value_counts.items()
        ]

    elif query_type == "first_rows":
        sample = df.head(limit).to_dict('records')
        result["data"] = _clean_records(sample)

    elif query_type == "last_rows":
        sample = df.tail(limit).to_dict('records')
        result["data"] = _clean_records(sample)

    elif query_type == "random_sample":
        sample = df.sample(min(limit, len(df))).to_dict('records')
        result["data"] = _clean_records(sample)

    else:
        raise ValueError(f"Unknown query_type: {query_type}")

    return result


def _clean_records(records: List[Dict]) -> List[Dict]:
    """Очистить записи от NaN и специальных типов"""
    cleaned = []
    for record in records:
        clean_record = {}
        for key, value in record.items():
            if pd.isna(value):
                clean_record[key] = None
            elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
                clean_record[key] = str(value)
            else:
                clean_record[key] = value
        cleaned.append(clean_record)
    return cleaned


async def analyze_data(
    session_id: str,
    user_message: str
) -> AgentResponse:
    """
    Анализировать данные на основе запроса пользователя

    Args:
        session_id: ID сессии
        user_message: Сообщение пользователя

    Returns:
        AgentResponse с результатами анализа
    """
    try:
        # Проверяем наличие файла
        if not file_manager.session_exists(session_id):
            return AgentResponse(
                success=False,
                message="Сессия не найдена",
                error="Session not found"
            )

        # Запускаем агента
        deps = AnalysisDependencies(
            session_id=session_id,
            user_message=user_message
        )

        result = await analysis_agent.run(user_message, deps=deps)

        # Формируем ответ
        return AgentResponse(
            success=True,
            message=result.data,
            intent=IntentType.ANALYSIS,
            data={
                "analysis_result": result.data
            }
        )

    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Ошибка при анализе: {str(e)}",
            intent=IntentType.ANALYSIS,
            error=str(e)
        )
