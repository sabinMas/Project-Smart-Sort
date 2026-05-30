"""LLM provider router for Domain 2: AI Classification."""

import asyncio
from abc import ABC, abstractmethod
from backend.shared.config import Config
from backend.shared.config import LLMProvider as LLMProviderEnum
from backend.shared.logging import get_logger
from backend.shared.errors import LLMProviderError

logger = get_logger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM with the given prompts.

        Args:
            system_prompt: System-level instructions for the LLM
            user_prompt: User message/question

        Returns:
            str: The LLM response text

        Raises:
            LLMProviderError: If the API call fails
        """
        raise NotImplementedError()


class CerebrasProvider(BaseLLMProvider):
    """Cerebras provider using OpenAI-compatible chat completions API."""

    # gpt-oss-120b is the production model on Cerebras as of May 2026
    MODEL = "gpt-oss-120b"

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Cerebras inference API using the OpenAI-compatible SDK.

        Uses client.chat.completions.create() with messages array.
        """
        try:
            from cerebras.cloud.sdk import Cerebras

            client = Cerebras(api_key=Config.CEREBRAS_API_KEY)

            # Cerebras uses OpenAI-compatible chat completions API
            response = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=2048,
            )

            content = response.choices[0].message.content if response.choices else ""

            logger.debug(f"Cerebras response: {content[:200]}...")

            return content

        except ImportError:
            raise LLMProviderError(
                "Cerebras SDK not installed. Install with: pip install cerebras_cloud_sdk"
            )
        except Exception as e:
            logger.error(f"Cerebras API error: {str(e)}")
            raise LLMProviderError(f"Cerebras API call failed: {str(e)}")


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider (fallback)."""

    MODEL = "llama-3.1-70b-versatile"

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Groq API using their Python SDK.

        Uses OpenAI-compatible chat completions with system message in messages array.
        """
        try:
            from groq import Groq

            client = Groq(api_key=Config.GROQ_API_KEY)

            response = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=2048,
            )

            content = response.choices[0].message.content if response.choices else ""

            logger.debug(f"Groq response: {content[:200]}...")

            return content

        except ImportError:
            raise LLMProviderError(
                "Groq SDK not installed. Install with: pip install groq"
            )
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise LLMProviderError(f"Groq API call failed: {str(e)}")


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider (fallback)."""

    MODEL = "gemini-pro"

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Google Gemini API.
        """
        try:
            import google.generativeai as genai

            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel(self.MODEL, system_instruction=system_prompt)

            response = model.generate_content(user_prompt)

            content = response.text if response else ""

            logger.debug(f"Gemini response: {content[:200]}...")

            return content

        except ImportError:
            raise LLMProviderError(
                "Google Generative AI SDK not installed. Install with: pip install google-generativeai"
            )
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise LLMProviderError(f"Gemini API call failed: {str(e)}")


class LLMRouter:
    """Router to select appropriate LLM provider based on configuration."""

    def __init__(self):
        """Initialize router and select provider based on LLM_PROVIDER env var."""
        self.provider_name = Config.LLM_PROVIDER
        self.provider = self._get_provider()

    def _get_provider(self) -> BaseLLMProvider:
        """
        Get LLM provider instance based on configuration.

        Returns:
            BaseLLMProvider: The selected provider

        Raises:
            ValueError: If provider is not supported
        """
        if self.provider_name == LLMProviderEnum.CEREBRAS:
            logger.info("Using Cerebras provider")
            return CerebrasProvider()
        elif self.provider_name == LLMProviderEnum.GROQ:
            logger.info("Using Groq provider")
            return GroqProvider()
        elif self.provider_name == LLMProviderEnum.GEMINI:
            logger.info("Using Gemini provider")
            return GeminiProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider_name}")

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Route LLM call to the selected provider with retry logic.

        Args:
            system_prompt: System-level instructions
            user_prompt: User message

        Returns:
            str: The LLM response

        Raises:
            LLMProviderError: If the API call fails after retries
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await self.provider.call(system_prompt, user_prompt)
            except LLMProviderError:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"LLM call failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
