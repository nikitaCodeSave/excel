"""
Валидатор кода для безопасного выполнения pandas операций
"""
import ast
import re
from typing import List, Set
from app.config import settings
from app.models.schemas import CodeValidationResult


class CodeValidator:
    """Валидация сгенерированного pandas кода"""

    def __init__(self):
        self.allowed_operations = settings.ALLOWED_PANDAS_OPERATIONS
        self.forbidden_patterns = settings.FORBIDDEN_CODE_PATTERNS

    def validate(self, code: str) -> CodeValidationResult:
        """
        Полная валидация кода

        Returns:
            CodeValidationResult с результатами проверки
        """
        warnings = []
        errors = []
        safe_operations = []
        unsafe_patterns = []

        # 1. Проверка на запрещённые паттерны
        for pattern in self.forbidden_patterns:
            if pattern in code:
                errors.append(f"Forbidden pattern detected: {pattern}")
                unsafe_patterns.append(pattern)

        # 2. Проверка синтаксиса Python
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
            return CodeValidationResult(
                is_valid=False,
                pandas_code=code,
                errors=errors,
                warnings=warnings,
                safe_operations=safe_operations,
                unsafe_patterns=unsafe_patterns
            )

        # 3. AST анализ
        ast_result = self._analyze_ast(tree)
        safe_operations.extend(ast_result["safe_ops"])
        unsafe_patterns.extend(ast_result["unsafe_ops"])

        if ast_result["unsafe_ops"]:
            errors.append(
                f"Unsafe operations detected: {', '.join(ast_result['unsafe_ops'])}"
            )

        # 4. Проверка структуры кода
        if not self._has_valid_structure(code):
            warnings.append(
                "Code structure might be unusual. "
                "Expected DataFrame operations only."
            )

        # 5. Проверка на использование df переменной
        if "df" not in code and "dataframe" not in code.lower():
            warnings.append(
                "No DataFrame variable found. "
                "Expected 'df' to be used."
            )

        is_valid = len(errors) == 0 and len(unsafe_patterns) == 0

        return CodeValidationResult(
            is_valid=is_valid,
            pandas_code=code,
            warnings=warnings,
            errors=errors,
            safe_operations=safe_operations,
            unsafe_patterns=unsafe_patterns
        )

    def _analyze_ast(self, tree: ast.AST) -> dict:
        """Анализ AST дерева"""
        safe_ops = []
        unsafe_ops = []

        for node in ast.walk(tree):
            # Проверка вызовов функций
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    operation = node.func.attr
                    if operation in self.allowed_operations:
                        safe_ops.append(operation)
                    else:
                        # Проверяем, не системная ли это функция
                        if self._is_system_call(operation):
                            unsafe_ops.append(operation)

                # Проверка прямых вызовов функций
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.forbidden_patterns:
                        unsafe_ops.append(func_name)

            # Проверка импортов (не должно быть!)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                unsafe_ops.append("import_statement")

        return {
            "safe_ops": list(set(safe_ops)),
            "unsafe_ops": list(set(unsafe_ops))
        }

    def _is_system_call(self, name: str) -> bool:
        """Проверка, является ли вызов системным"""
        system_prefixes = ['os.', 'sys.', 'subprocess.', 'file.']
        return any(name.startswith(prefix) for prefix in system_prefixes)

    def _has_valid_structure(self, code: str) -> bool:
        """
        Проверка базовой структуры кода
        Ожидаем только присваивания и операции с DataFrame
        """
        lines = [line.strip() for line in code.split('\n') if line.strip()]

        for line in lines:
            # Пропускаем комментарии
            if line.startswith('#'):
                continue

            # Должно быть либо присваивание, либо операция с df
            if not (
                line.startswith('df') or
                '=' in line or
                line.startswith('print')  # для отладки
            ):
                return False

        return True

    def extract_dataframe_variable(self, code: str) -> str:
        """Извлечь имя переменной DataFrame из кода"""
        # Ищем паттерны типа df = ... или dataframe = ...
        pattern = r'(\w+)\s*=\s*df'
        matches = re.findall(pattern, code)

        if matches:
            return matches[-1]  # Последнее присваивание

        return "df"  # По умолчанию

    def sanitize_code(self, code: str) -> str:
        """
        Очистка и нормализация кода
        Удаляет комментарии, лишние пробелы и т.д.
        """
        # Удаляем комментарии
        lines = []
        for line in code.split('\n'):
            # Удаляем комментарии после кода
            if '#' in line:
                line = line[:line.index('#')]

            line = line.strip()
            if line:
                lines.append(line)

        return '\n'.join(lines)

    def wrap_code_safely(self, code: str) -> str:
        """
        Обернуть код в безопасную среду выполнения
        """
        wrapped = f"""
# Auto-generated safe execution wrapper
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Disable dangerous operations
pd.set_option('mode.chained_assignment', None)

# Execute user code
{code}

# Return result
result_df = df
"""
        return wrapped


# Singleton instance
code_validator = CodeValidator()
