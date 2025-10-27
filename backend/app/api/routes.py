"""
FastAPI routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Optional
import os

from app.models.schemas import (
    SessionCreate, SessionResponse, ChatMessage, AgentResponse,
    DataPreviewRequest, DataPreviewResponse, ExportRequest, IntentType
)
from app.tools.file_manager import file_manager
from app.agents.router import route_message
from app.agents.analysis import analyze_data
from app.agents.transform import transform_data, create_template
from app.agents.visualization import create_visualization
from app.agents.export import export_file


router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """Создать новую сессию"""
    try:
        session_id = file_manager.create_session()

        return SessionResponse(
            session_id=session_id,
            created_at=file_manager.get_session_path(session_id).stat().st_ctime
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_file(
    session_id: str,
    file: UploadFile = File(...)
):
    """Загрузить файл"""
    try:
        # Проверяем сессию
        if not file_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        # Проверяем расширение
        filename = file.filename
        if not any(filename.endswith(ext) for ext in ['.xlsx', '.xls', '.csv']):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Only .xlsx, .xls, .csv are allowed"
            )

        # Читаем содержимое
        content = await file.read()

        # Сохраняем файл
        file_id, metadata = file_manager.save_uploaded_file(
            session_id,
            content,
            filename
        )

        return {
            "success": True,
            "file_id": file_id,
            "metadata": metadata.model_dump(mode='json')
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=AgentResponse)
async def chat(message: ChatMessage):
    """Отправить сообщение в чат"""
    try:
        session_id = message.session_id
        user_message = message.message

        # Проверяем сессию
        if not file_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        # Классифицируем намерение
        intent, _ = await route_message(user_message)

        # Маршрутизируем к нужному агенту
        if intent == IntentType.ANALYSIS:
            response = await analyze_data(session_id, user_message)

        elif intent == IntentType.TRANSFORM:
            # Проверяем, не запрос ли это на создание шаблона
            if any(word in user_message.lower() for word in ['шаблон', 'template', 'создай файл с нуля']):
                response = await create_template(session_id, user_message)
            else:
                response = await transform_data(session_id, user_message)

        elif intent == IntentType.VISUALIZE:
            response = await create_visualization(session_id, user_message)

        elif intent == IntentType.EXPORT:
            # Определяем формат
            format_type = "xlsx"
            if "csv" in user_message.lower():
                format_type = "csv"

            response = await export_file(session_id, format_type)

        else:  # GENERAL
            response = AgentResponse(
                success=True,
                message="Привет! Я помогу вам работать с Excel/CSV файлами. Вы можете:\n\n"
                        "📊 Анализировать данные\n"
                        "✏️ Изменять и обрабатывать данные\n"
                        "📈 Создавать графики и визуализации\n"
                        "💾 Экспортировать результаты\n\n"
                        "Загрузите файл и задайте вопрос!",
                intent=IntentType.GENERAL
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{session_id}", response_model=DataPreviewResponse)
async def get_preview(session_id: str, rows: int = 10):
    """Получить preview данных"""
    try:
        if not file_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        df = file_manager.load_dataframe(session_id)

        # Получаем preview
        preview_data = df.head(rows).to_dict('records')

        # Очистка от NaN
        import pandas as pd
        cleaned_data = []
        for record in preview_data:
            clean_record = {}
            for key, value in record.items():
                if pd.isna(value):
                    clean_record[key] = None
                else:
                    clean_record[key] = value
            cleaned_data.append(clean_record)

        return DataPreviewResponse(
            data=cleaned_data,
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=df.columns.tolist()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Скачать файл"""
    try:
        file_path = file_manager.export_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualizations/{session_id}/{viz_id}")
async def get_visualization(session_id: str, viz_id: str):
    """Получить визуализацию"""
    try:
        if not file_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        viz_path = file_manager.get_session_path(session_id) / "visualizations" / f"{viz_id}.png"

        if not viz_path.exists():
            raise HTTPException(status_code=404, detail="Visualization not found")

        return FileResponse(
            path=viz_path,
            media_type='image/png'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Удалить сессию"""
    try:
        if not file_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

        file_manager.cleanup_session(session_id)

        return {"success": True, "message": "Session deleted"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "excel-ai-processor"}
