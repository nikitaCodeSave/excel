"""
Безопасное выполнение pandas кода
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
import traceback
import signal
from contextlib import contextmanager

from app.config import settings
from app.tools.code_validator import code_validator


class TimeoutException(Exception):
    """Исключение при превышении времени выполнения"""
    pass


@contextmanager
def timeout(seconds: int):
    """Контекстный менеджер для ограничения времени выполнения"""
    def timeout_handler(signum, frame):
        raise TimeoutException("Code execution timeout")

    # Устанавливаем обработчик
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


class PandasExecutor:
    """Безопасное выполнение pandas операций"""

    def __init__(self):
        self.timeout_seconds = settings.PANDAS_TIMEOUT
        self.dry_run_sample_size = settings.DRY_RUN_SAMPLE_SIZE

    def execute(
        self,
        df: pd.DataFrame,
        code: str,
        dry_run: bool = True
    ) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Выполнить pandas код

        Args:
            df: Исходный DataFrame
            code: Код для выполнения
            dry_run: Выполнить на sample данных сначала

        Returns:
            Tuple[success, result_df, message]
        """
        # 1. Валидация кода
        validation = code_validator.validate(code)

        if not validation.is_valid:
            error_msg = "Code validation failed:\n"
            error_msg += "\n".join(validation.errors)
            return False, None, error_msg

        # 2. Dry run на sample данных
        if dry_run and len(df) > self.dry_run_sample_size:
            success, _, message = self._execute_safe(
                df.head(self.dry_run_sample_size).copy(),
                code
            )

            if not success:
                return False, None, f"Dry run failed: {message}"

        # 3. Выполнение на полных данных
        success, result_df, message = self._execute_safe(df.copy(), code)

        if not success:
            return False, None, message

        # 4. Проверка результата
        if result_df is None or not isinstance(result_df, pd.DataFrame):
            return False, None, "Result is not a valid DataFrame"

        # 5. Базовые проверки результата
        if len(result_df) == 0:
            return False, None, "Result DataFrame is empty"

        return True, result_df, "Execution successful"

    def _execute_safe(
        self,
        df: pd.DataFrame,
        code: str
    ) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Безопасное выполнение кода с timeout
        """
        try:
            # Создаём изолированное пространство имён
            namespace = {
                'df': df,
                'pd': pd,
                'np': np,
                'datetime': datetime,
                'timedelta': timedelta,
            }

            # Выполняем с timeout
            with timeout(self.timeout_seconds):
                exec(code, namespace)

            # Получаем результат
            result_df = namespace.get('df', None)

            if result_df is None:
                # Пытаемся найти другие DataFrame в namespace
                for key, value in namespace.items():
                    if isinstance(value, pd.DataFrame) and key != '__builtins__':
                        result_df = value
                        break

            return True, result_df, "Success"

        except TimeoutException:
            return False, None, f"Execution timeout ({self.timeout_seconds}s exceeded)"

        except Exception as e:
            error_msg = f"Execution error: {str(e)}\n"
            error_msg += traceback.format_exc()
            return False, None, error_msg

    def preview_changes(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        max_rows: int = 5
    ) -> Dict[str, Any]:
        """
        Предпросмотр изменений между DataFrame

        Returns:
            Dict с информацией об изменениях
        """
        changes = {
            "rows_before": len(df_before),
            "rows_after": len(df_after),
            "columns_before": len(df_before.columns),
            "columns_after": len(df_after.columns),
            "new_columns": [],
            "removed_columns": [],
            "modified_columns": [],
            "sample_before": df_before.head(max_rows).to_dict('records'),
            "sample_after": df_after.head(max_rows).to_dict('records'),
        }

        # Найти новые и удалённые столбцы
        cols_before = set(df_before.columns)
        cols_after = set(df_after.columns)

        changes["new_columns"] = list(cols_after - cols_before)
        changes["removed_columns"] = list(cols_before - cols_after)

        # Найти изменённые столбцы
        common_cols = cols_before & cols_after
        for col in common_cols:
            if not df_before[col].equals(df_after[col]):
                changes["modified_columns"].append(col)

        return changes

    def validate_result(
        self,
        original_df: pd.DataFrame,
        result_df: pd.DataFrame
    ) -> Tuple[bool, str]:
        """
        Проверить результат выполнения

        Returns:
            Tuple[is_valid, message]
        """
        issues = []

        # 1. Проверка типа
        if not isinstance(result_df, pd.DataFrame):
            return False, "Result is not a DataFrame"

        # 2. Проверка пустоты
        if len(result_df) == 0:
            issues.append("Result DataFrame is empty")

        # 3. Проверка на NaN в критичных местах
        if result_df.isna().all().any():
            issues.append("Some columns are completely null")

        # 4. Проверка на дубликаты индексов
        if result_df.index.duplicated().any():
            issues.append("Duplicate indices detected")

        # 5. Проверка разумности размера
        if len(result_df) > len(original_df) * 10:
            issues.append(
                f"Result is suspiciously large "
                f"({len(result_df)} vs {len(original_df)} rows)"
            )

        if issues:
            return False, "Validation issues:\n" + "\n".join(issues)

        return True, "Validation passed"

    def get_operation_summary(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame
    ) -> str:
        """Получить краткое описание выполненной операции"""
        changes = self.preview_changes(df_before, df_after, max_rows=0)

        summary_parts = []

        if changes["rows_before"] != changes["rows_after"]:
            summary_parts.append(
                f"Rows: {changes['rows_before']} → {changes['rows_after']}"
            )

        if changes["new_columns"]:
            summary_parts.append(
                f"Added columns: {', '.join(changes['new_columns'])}"
            )

        if changes["removed_columns"]:
            summary_parts.append(
                f"Removed columns: {', '.join(changes['removed_columns'])}"
            )

        if changes["modified_columns"]:
            summary_parts.append(
                f"Modified {len(changes['modified_columns'])} columns"
            )

        if not summary_parts:
            summary_parts.append("Data modified in place")

        return "; ".join(summary_parts)


# Singleton instance
pandas_executor = PandasExecutor()
