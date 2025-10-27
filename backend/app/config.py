"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    """Настройки приложения"""

    # API Settings
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Excel AI Processor"
    VERSION: str = "1.0.0"

    # LLM Settings
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")  # OpenAI model
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai or ollama
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")  # For Ollama
    LLM_TIMEOUT: int = 300  # 5 минут
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # OpenAI API key

    # File Storage
    UPLOAD_DIR: Path = Path("/tmp/excel_processor/sessions")
    EXPORT_DIR: Path = Path("/tmp/excel_processor/exports")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB для MVP
    ALLOWED_EXTENSIONS: set = {".xlsx", ".xls", ".csv"}

    # Session Management
    SESSION_TIMEOUT: int = 3600  # 1 час
    CLEANUP_INTERVAL: int = 300  # 5 минут

    # Security
    ALLOWED_PANDAS_OPERATIONS: set = {
        # DataFrame operations
        "assign", "drop", "rename", "sort_values", "groupby",
        "merge", "fillna", "dropna", "apply", "map", "filter",
        "query", "loc", "iloc", "head", "tail", "sample",
        # Aggregation
        "sum", "mean", "median", "count", "min", "max", "std", "var",
        # String operations
        "upper", "lower", "strip", "replace", "contains", "split",
    }

    FORBIDDEN_CODE_PATTERNS: list = [
        "eval", "exec", "compile", "__import__", "open", "file",
        "input", "raw_input", "subprocess", "os.system", "commands",
        "pickle", "shelve", "socket", "urllib", "requests"
    ]

    # Pandas Execution
    PANDAS_TIMEOUT: int = 60  # 1 минута на операцию
    DRY_RUN_SAMPLE_SIZE: int = 100  # Строк для dry-run

    # Visualization
    MATPLOTLIB_DPI: int = 150
    VISUALIZATION_FORMAT: str = "png"
    MAX_PLOT_SIZE: tuple = (12, 8)  # inches

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаём директории при импорте
settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
