"""
Export Agent - экспорт файлов
"""
from pydantic import BaseModel
from typing import Optional
import os

from app.tools.file_manager import file_manager
from app.models.schemas import AgentResponse, IntentType, ExportResponse


async def export_file(
    session_id: str,
    format: str = "xlsx",
    filename: Optional[str] = None
) -> AgentResponse:
    """
    Экспортировать файл

    Args:
        session_id: ID сессии
        format: Формат файла (xlsx, csv)
        filename: Имя файла (опционально)

    Returns:
        AgentResponse с информацией о файле
    """
    try:
        # Проверяем наличие файла
        if not file_manager.session_exists(session_id):
            return AgentResponse(
                success=False,
                message="Сессия не найдена",
                error="Session not found"
            )

        # Экспорт в зависимости от формата
        if format.lower() == "csv":
            export_id, file_path = file_manager.export_to_csv(session_id, filename)
        else:
            export_id, file_path = file_manager.export_to_excel(session_id, filename)

        # Получаем размер файла
        file_size = os.path.getsize(file_path)

        # Формируем URL для скачивания
        download_url = f"/api/download/{file_path.name}"

        export_response = ExportResponse(
            file_id=export_id,
            filename=file_path.name,
            download_url=download_url,
            file_size=file_size
        )

        return AgentResponse(
            success=True,
            message=f"✅ Файл готов к скачиванию!\n\nФормат: {format.upper()}\nРазмер: {file_size / 1024:.2f} KB",
            intent=IntentType.EXPORT,
            data={
                "export": export_response.model_dump()
            },
            file_id=export_id
        )

    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Ошибка при экспорте: {str(e)}",
            intent=IntentType.EXPORT,
            error=str(e)
        )


async def convert_format(
    session_id: str,
    source_format: str,
    target_format: str,
    filename: Optional[str] = None
) -> AgentResponse:
    """
    Конвертировать формат файла

    Args:
        session_id: ID сессии
        source_format: Исходный формат
        target_format: Целевой формат
        filename: Имя файла (опционально)

    Returns:
        AgentResponse с информацией о конвертированном файле
    """
    # Просто используем export с нужным форматом
    return await export_file(session_id, target_format, filename)
