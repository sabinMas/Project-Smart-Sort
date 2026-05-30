"""LLM provider router for Domain 2: AI Classification."""

from typing import Dict, Any
from abc import ABC, abstractmethod
from backend.shared.config import Config, LLMProvider
from backend.shared.logging import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
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


class CerebasProvider(LLMProvider):
    """Cerebras Llama 3.1 8B provider."""

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO: Implement Cerebras API call.

        1. Initialize Cerebras client with API key
        2. Call Llama 3.1 8B model
        3. Parse JSON response
        4. Validate response format
        5. Return JSON string

        Use model: "llama-3.1-8b"
        """
        raise NotImplementedError("TODO: Implement Cerebras provider")


class GroqProvider(LLMProvider):
    """Groq LLM provider (fallback)."""

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO: Implement Groq API call.

        1. Initialize Groq client with API key
        2. Call LLM model (e.g., mixtral)
        3. Parse JSON response
        4. Validate response format
        5. Return JSON string
        """
        raise NotImplementedError("TODO: Implement Groq provider")


class GeminiProvider(LLMProvider):
    """Google Gemini provider (fallback)."""

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO: Implement Google Gemini API call.

        1. Initialize Gemini client with API key
        2. Call Gemini model
        3. Parse JSON response
        4. Validate response format
        5. Return JSON string
        """
        raise NotImplementedError("TODO: Implement Gemini provider")


class LLMRouter:
    """Router to select appropriate LLM provider based on configuration."""

    def __init__(self):
        """Initialize router and select provider based on LLM_PROVIDER env var."""
        self.provider_name = Config.LLM_PROVIDER
        self.provider = self._get_provider()

    def _get_provider(self) -> LLMProvider:
        """
        Get LLM provider instance based on configuration.

        Returns:
            LLMProvider: The selected provider

        Raises:
            ConfigurationError: If provider is not supported
        """
        if self.provider_name == LLMProvider.CEREBRAS:
            logger.info("Using Cerebras provider")
            return CerebasProvider()
        elif self.provider_name == LLMProvider.GROQ:
            logger.info("Using Groq provider")
            return GroqProvider()
        elif self.provider_name == LLMProvider.GEMINI:
            logger.info("Using Gemini provider")
            return GeminiProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider_name}")

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        Route LLM call to the selected provider.

        Args:
            system_prompt: System-level instructions
            user_prompt: User message

        Returns:
            str: The LLM response

        Raises:
            LLMProviderError: If the API call fails
        """
        return await self.provider.call(system_prompt, user_prompt)
