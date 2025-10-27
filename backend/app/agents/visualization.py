"""
Visualization Agent - создание графиков и диаграмм
"""
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend без GUI
import matplotlib.pyplot as plt
import uuid
from datetime import datetime

from app.config import settings
from app.tools.file_manager import file_manager
from app.models.schemas import AgentResponse, IntentType, VisualizationMetadata


# Системный промпт для Visualization Agent
VISUALIZATION_SYSTEM_PROMPT = """Ты - эксперт по визуализации данных с использованием matplotlib и pandas.

Твоя задача - создавать графики на основе запросов пользователя.

Доступные типы графиков:
1. line - линейный график (для временных рядов, трендов)
2. bar - столбчатая диаграмма (для сравнения категорий)
3. scatter - точечная диаграмма (для корреляций)
4. pie - круговая диаграмма (для долей)
5. hist - гистограмма (для распределений)
6. box - box plot (для статистики)

Примеры запросов:
- "Построй график продаж по месяцам" → line chart
- "Покажи столбчатую диаграмму по регионам" → bar chart
- "Круговая диаграмма долей товаров" → pie chart
- "Гистограмма распределения цен" → histogram

Инструменты:
- get_column_names: список столбцов
- get_numeric_columns: числовые столбцы
- get_categorical_columns: категориальные столбцы
- preview_data: первые строки данных

Формат ответа:
{
    "chart_type": "line",
    "x_column": "дата",
    "y_column": "продажи",
    "title": "График продаж по времени",
    "description": "Визуализация динамики продаж"
}
"""


class VisualizationDependencies(BaseModel):
    """Зависимости для Visualization Agent"""
    session_id: str
    user_message: str


class VisualizationSpec(BaseModel):
    """Спецификация визуализации"""
    chart_type: str = Field(description="Тип графика: line, bar, scatter, pie, hist, box")
    x_column: Optional[str] = Field(default=None, description="Столбец для оси X")
    y_column: Optional[str] = Field(default=None, description="Столбец для оси Y")
    title: str = Field(description="Заголовок графика")
    description: str = Field(description="Описание визуализации")
    group_by: Optional[str] = Field(default=None, description="Столбец для группировки")


# Создаём Visualization Agent
# Определяем модель в зависимости от провайдера
_model_string = (
    f"{settings.LLM_PROVIDER}:{settings.LLM_MODEL}"
    if settings.LLM_PROVIDER == "openai"
    else f"ollama:{settings.LLM_MODEL}"
)

visualization_agent = Agent[VisualizationDependencies, VisualizationSpec](
    model=_model_string,
    deps_type=VisualizationDependencies,
    system_prompt=VISUALIZATION_SYSTEM_PROMPT,
    retries=2,
)


@visualization_agent.tool
def get_column_names(ctx: RunContext[VisualizationDependencies]) -> List[str]:
    """Получить список всех столбцов"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    return df.columns.tolist()


@visualization_agent.tool
def get_numeric_columns(ctx: RunContext[VisualizationDependencies]) -> List[str]:
    """Получить список числовых столбцов"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    return df.select_dtypes(include=['number']).columns.tolist()


@visualization_agent.tool
def get_categorical_columns(ctx: RunContext[VisualizationDependencies]) -> List[str]:
    """Получить список категориальных столбцов"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


@visualization_agent.tool
def preview_data(
    ctx: RunContext[VisualizationDependencies],
    rows: int = 5
) -> List[Dict[str, Any]]:
    """Предпросмотр данных"""
    df = file_manager.load_dataframe(ctx.deps.session_id)
    return df.head(rows).to_dict('records')


def create_line_chart(df: pd.DataFrame, spec: VisualizationSpec):
    """Создать линейный график"""
    fig, ax = plt.subplots(figsize=settings.MAX_PLOT_SIZE)

    if spec.x_column and spec.y_column:
        ax.plot(df[spec.x_column], df[spec.y_column], marker='o')
        ax.set_xlabel(spec.x_column)
        ax.set_ylabel(spec.y_column)
    else:
        # Если не указаны столбцы, строим по индексу
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols[:3]:  # Максимум 3 линии
            ax.plot(df.index, df[col], marker='o', label=col)
        ax.legend()

    ax.set_title(spec.title)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def create_bar_chart(df: pd.DataFrame, spec: VisualizationSpec):
    """Создать столбчатую диаграмму"""
    fig, ax = plt.subplots(figsize=settings.MAX_PLOT_SIZE)

    if spec.group_by:
        # Группировка и агрегация
        if spec.y_column:
            grouped = df.groupby(spec.group_by)[spec.y_column].sum()
        else:
            grouped = df[spec.group_by].value_counts()

        grouped.plot(kind='bar', ax=ax)
    elif spec.x_column and spec.y_column:
        df.plot(x=spec.x_column, y=spec.y_column, kind='bar', ax=ax)
    else:
        # По умолчанию - первые 10 строк
        numeric_col = df.select_dtypes(include=['number']).columns[0]
        df[numeric_col].head(10).plot(kind='bar', ax=ax)

    ax.set_title(spec.title)
    ax.set_xlabel(spec.x_column or '')
    ax.set_ylabel(spec.y_column or 'Значение')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def create_scatter_chart(df: pd.DataFrame, spec: VisualizationSpec):
    """Создать точечную диаграмму"""
    fig, ax = plt.subplots(figsize=settings.MAX_PLOT_SIZE)

    if spec.x_column and spec.y_column:
        ax.scatter(df[spec.x_column], df[spec.y_column], alpha=0.6)
        ax.set_xlabel(spec.x_column)
        ax.set_ylabel(spec.y_column)

    ax.set_title(spec.title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig


def create_pie_chart(df: pd.DataFrame, spec: VisualizationSpec):
    """Создать круговую диаграмму"""
    fig, ax = plt.subplots(figsize=(10, 8))

    if spec.x_column:
        # Подсчёт значений
        value_counts = df[spec.x_column].value_counts().head(10)
        ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')

    ax.set_title(spec.title)
    plt.tight_layout()

    return fig


def create_histogram(df: pd.DataFrame, spec: VisualizationSpec):
    """Создать гистограмму"""
    fig, ax = plt.subplots(figsize=settings.MAX_PLOT_SIZE)

    if spec.x_column:
        df[spec.x_column].hist(ax=ax, bins=30, edgecolor='black')
        ax.set_xlabel(spec.x_column)
    else:
        numeric_col = df.select_dtypes(include=['number']).columns[0]
        df[numeric_col].hist(ax=ax, bins=30, edgecolor='black')
        ax.set_xlabel(numeric_col)

    ax.set_ylabel('Частота')
    ax.set_title(spec.title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig


def create_box_plot(df: pd.DataFrame, spec: VisualizationSpec):
    """Создать box plot"""
    fig, ax = plt.subplots(figsize=settings.MAX_PLOT_SIZE)

    if spec.y_column:
        if spec.group_by:
            df.boxplot(column=spec.y_column, by=spec.group_by, ax=ax)
        else:
            df[spec.y_column].plot(kind='box', ax=ax)

    ax.set_title(spec.title)
    plt.tight_layout()

    return fig


async def create_visualization(
    session_id: str,
    user_message: str
) -> AgentResponse:
    """
    Создать визуализацию на основе запроса пользователя

    Args:
        session_id: ID сессии
        user_message: Сообщение пользователя

    Returns:
        AgentResponse с метаданными визуализации
    """
    try:
        # Проверяем наличие файла
        if not file_manager.session_exists(session_id):
            return AgentResponse(
                success=False,
                message="Сессия не найдена",
                error="Session not found"
            )

        # Загружаем DataFrame
        df = file_manager.load_dataframe(session_id)

        # Запускаем агента для генерации спецификации
        deps = VisualizationDependencies(
            session_id=session_id,
            user_message=user_message
        )

        result = await visualization_agent.run(user_message, deps=deps)
        spec: VisualizationSpec = result.data

        # Создаём график в зависимости от типа
        chart_creators = {
            'line': create_line_chart,
            'bar': create_bar_chart,
            'scatter': create_scatter_chart,
            'pie': create_pie_chart,
            'hist': create_histogram,
            'box': create_box_plot,
        }

        creator = chart_creators.get(spec.chart_type, create_line_chart)
        fig = creator(df, spec)

        # Сохраняем визуализацию
        viz_id = str(uuid.uuid4())
        viz_path = file_manager.save_visualization(session_id, viz_id, fig)
        plt.close(fig)

        # Создаём метаданные
        metadata = VisualizationMetadata(
            viz_id=viz_id,
            chart_type=spec.chart_type,
            description=spec.description,
            file_path=str(viz_path),
            created_at=datetime.now(),
            width=int(settings.MAX_PLOT_SIZE[0] * settings.MATPLOTLIB_DPI),
            height=int(settings.MAX_PLOT_SIZE[1] * settings.MATPLOTLIB_DPI)
        )

        return AgentResponse(
            success=True,
            message=f"✅ График создан!\n\n{spec.title}\n{spec.description}",
            intent=IntentType.VISUALIZE,
            data={
                "visualization": metadata.model_dump(mode='json'),
                "spec": spec.model_dump()
            },
            visualization_ids=[viz_id]
        )

    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Ошибка при создании визуализации: {str(e)}",
            intent=IntentType.VISUALIZE,
            error=str(e)
        )
