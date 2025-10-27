"""
Клиент для работы с локальной LLM (Ollama)
"""
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings


class OllamaClient:
    """Клиент для Ollama API"""

    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Генерация текста через Ollama

        Args:
            prompt: Пользовательский запрос
            system_prompt: Системный промпт
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов

        Returns:
            Сгенерированный текст
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                return result.get("response", "")

            except httpx.HTTPError as e:
                raise Exception(f"LLM API error: {str(e)}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """
        Чат через Ollama

        Args:
            messages: Список сообщений [{"role": "user", "content": "..."}]
            temperature: Температура генерации

        Returns:
            Ответ ассистента
        """
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                message = result.get("message", {})
                return message.get("content", "")

            except httpx.HTTPError as e:
                raise Exception(f"LLM API error: {str(e)}")

    async def is_available(self) -> bool:
        """Проверить доступность Ollama"""
        url = f"{self.base_url}/api/tags"

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                return response.status_code == 200
        except:
            return False


# Singleton instance
ollama_client = OllamaClient()
