"""
Pydantic схемы для API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Типы намерений пользователя"""
    ANALYSIS = "analysis"
    TRANSFORM = "transform"
    VISUALIZE = "visualize"
    EXPORT = "export"
    GENERAL = "general"


class FileMetadata(BaseModel):
    """Метаданные загруженного файла"""
    file_id: str
    original_filename: str
    file_size: int
    upload_timestamp: datetime
    rows: Optional[int] = None
    columns: Optional[int] = None
    column_names: Optional[List[str]] = None
    column_types: Optional[Dict[str, str]] = None


class SessionCreate(BaseModel):
    """Создание новой сессии"""
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    """Ответ при создании сессии"""
    session_id: str
    created_at: datetime


class ChatMessage(BaseModel):
    """Сообщение в чате"""
    session_id: str
    message: str
    file_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Ответ от агента"""
    success: bool
    message: str
    intent: Optional[IntentType] = None
    data: Optional[Dict[str, Any]] = None
    preview: Optional[List[Dict[str, Any]]] = None
    visualization_ids: Optional[List[str]] = None
    file_id: Optional[str] = None
    error: Optional[str] = None


class DataPreviewRequest(BaseModel):
    """Запрос на preview данных"""
    session_id: str
    rows: int = Field(default=10, ge=1, le=100)


class DataPreviewResponse(BaseModel):
    """Preview данных"""
    data: List[Dict[str, Any]]
    total_rows: int
    total_columns: int
    columns: List[str]


class VisualizationRequest(BaseModel):
    """Запрос на создание визуализации"""
    session_id: str
    description: str
    chart_type: Optional[str] = None  # line, bar, scatter, pie, etc.


class ExportRequest(BaseModel):
    """Запрос на экспорт файла"""
    session_id: str
    format: str = Field(default="xlsx")  # xlsx, csv
    filename: Optional[str] = None


class ExportResponse(BaseModel):
    """Ответ на экспорт"""
    file_id: str
    filename: str
    download_url: str
    file_size: int


# Модели для работы агентов

class TransformOperation(BaseModel):
    """Операция трансформации данных"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    operation_type: str  # add_column, filter, sort, aggregate, etc.
    pandas_code: str
    description: str
    affected_columns: Optional[List[str]] = None
    validation_passed: bool = False


class AnalysisResult(BaseModel):
    """Результат анализа данных"""
    query: str
    result: Any
    explanation: str
    data_sample: Optional[List[Dict[str, Any]]] = None


class VisualizationMetadata(BaseModel):
    """Метаданные визуализации"""
    viz_id: str
    chart_type: str
    description: str
    file_path: str
    created_at: datetime
    width: int
    height: int


class CodeValidationResult(BaseModel):
    """Результат валидации кода"""
    is_valid: bool
    pandas_code: str
    warnings: List[str] = []
    errors: List[str] = []
    safe_operations: List[str] = []
    unsafe_patterns: List[str] = []
