"""
Менеджер файлов для работы с Excel/CSV
"""
import pandas as pd
import pickle
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import uuid
import shutil

from app.config import settings
from app.models.schemas import FileMetadata


class FileManager:
    """Управление файлами и сессиями"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.export_dir = settings.EXPORT_DIR

    def create_session(self) -> str:
        """Создать новую сессию"""
        session_id = str(uuid.uuid4())
        session_path = self.upload_dir / session_id
        session_path.mkdir(parents=True, exist_ok=True)

        # Создаём подпапки
        (session_path / "visualizations").mkdir(exist_ok=True)

        # Метаданные сессии
        metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "file_id": None
        }

        with open(session_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return session_id

    def get_session_path(self, session_id: str) -> Path:
        """Получить путь к сессии"""
        return self.upload_dir / session_id

    def session_exists(self, session_id: str) -> bool:
        """Проверить существование сессии"""
        return self.get_session_path(session_id).exists()

    def save_uploaded_file(
        self,
        session_id: str,
        file_content: bytes,
        filename: str
    ) -> Tuple[str, FileMetadata]:
        """
        Сохранить загруженный файл и конвертировать в DataFrame

        Returns:
            Tuple[file_id, FileMetadata]
        """
        if not self.session_exists(session_id):
            raise ValueError(f"Session {session_id} does not exist")

        session_path = self.get_session_path(session_id)
        file_id = str(uuid.uuid4())

        # Сохраняем оригинальный файл
        original_path = session_path / "original.xlsx"
        with open(original_path, "wb") as f:
            f.write(file_content)

        # Читаем в DataFrame
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(original_path)
            else:
                df = pd.read_excel(original_path)
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")

        # Сохраняем DataFrame как pickle
        df_path = session_path / "current.pkl"
        with open(df_path, "wb") as f:
            pickle.dump(df, f)

        # Создаём метаданные
        metadata = FileMetadata(
            file_id=file_id,
            original_filename=filename,
            file_size=len(file_content),
            upload_timestamp=datetime.now(),
            rows=len(df),
            columns=len(df.columns),
            column_names=df.columns.tolist(),
            column_types={col: str(dtype) for col, dtype in df.dtypes.items()}
        )

        # Обновляем метаданные сессии
        with open(session_path / "metadata.json", "r") as f:
            session_metadata = json.load(f)

        session_metadata["file_id"] = file_id
        session_metadata["file_metadata"] = metadata.model_dump(mode='json')

        with open(session_path / "metadata.json", "w") as f:
            json.dump(session_metadata, f, indent=2)

        return file_id, metadata

    def load_dataframe(self, session_id: str) -> pd.DataFrame:
        """Загрузить текущий DataFrame"""
        session_path = self.get_session_path(session_id)
        df_path = session_path / "current.pkl"

        if not df_path.exists():
            raise FileNotFoundError(f"No DataFrame found for session {session_id}")

        with open(df_path, "rb") as f:
            return pickle.load(f)

    def save_dataframe(self, session_id: str, df: pd.DataFrame) -> None:
        """Сохранить обновлённый DataFrame"""
        session_path = self.get_session_path(session_id)
        df_path = session_path / "current.pkl"

        with open(df_path, "wb") as f:
            pickle.dump(df, f)

        # Обновляем метаданные
        with open(session_path / "metadata.json", "r") as f:
            metadata = json.load(f)

        if "file_metadata" in metadata:
            metadata["file_metadata"]["rows"] = len(df)
            metadata["file_metadata"]["columns"] = len(df.columns)
            metadata["file_metadata"]["column_names"] = df.columns.tolist()

        with open(session_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def get_file_metadata(self, session_id: str) -> Optional[FileMetadata]:
        """Получить метаданные файла"""
        session_path = self.get_session_path(session_id)
        metadata_path = session_path / "metadata.json"

        if not metadata_path.exists():
            return None

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if "file_metadata" not in metadata:
            return None

        return FileMetadata(**metadata["file_metadata"])

    def export_to_excel(
        self,
        session_id: str,
        filename: Optional[str] = None
    ) -> Tuple[str, Path]:
        """
        Экспортировать DataFrame в Excel

        Returns:
            Tuple[export_id, file_path]
        """
        df = self.load_dataframe(session_id)

        export_id = str(uuid.uuid4())
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        export_path = self.export_dir / f"{export_id}_{filename}"

        # Экспорт с форматированием
        with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')

            # Применяем базовое форматирование
            workbook = writer.book
            worksheet = writer.sheets['Data']

            # Автоширина столбцов
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[
                    worksheet.cell(1, idx).column_letter
                ].width = min(max_length + 2, 50)

        return export_id, export_path

    def export_to_csv(
        self,
        session_id: str,
        filename: Optional[str] = None
    ) -> Tuple[str, Path]:
        """
        Экспортировать DataFrame в CSV

        Returns:
            Tuple[export_id, file_path]
        """
        df = self.load_dataframe(session_id)

        export_id = str(uuid.uuid4())
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if not filename.endswith('.csv'):
            filename += '.csv'

        export_path = self.export_dir / f"{export_id}_{filename}"
        df.to_csv(export_path, index=False, encoding='utf-8-sig')

        return export_id, export_path

    def save_visualization(
        self,
        session_id: str,
        viz_id: str,
        figure
    ) -> Path:
        """Сохранить визуализацию"""
        session_path = self.get_session_path(session_id)
        viz_path = session_path / "visualizations" / f"{viz_id}.png"

        figure.savefig(
            viz_path,
            dpi=settings.MATPLOTLIB_DPI,
            bbox_inches='tight'
        )

        return viz_path

    def cleanup_session(self, session_id: str) -> None:
        """Удалить сессию и все связанные файлы"""
        session_path = self.get_session_path(session_id)
        if session_path.exists():
            shutil.rmtree(session_path)

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Очистить старые сессии

        Returns:
            Количество удалённых сессий
        """
        cleaned = 0
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        for session_path in self.upload_dir.iterdir():
            if session_path.is_dir():
                metadata_path = session_path / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    created_at = datetime.fromisoformat(
                        metadata["created_at"]
                    ).timestamp()

                    if created_at < cutoff_time:
                        shutil.rmtree(session_path)
                        cleaned += 1

        return cleaned


# Singleton instance
file_manager = FileManager()
