"""LLM provider router for Domain 2: AI Classification."""

from typing import Dict, Any
from abc import ABC, abstractmethod
from backend.shared.config import Config, LLMProvider as LLMProviderEnum
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


class CerebasProvider(BaseLLMProvider):
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
        try:
            from cerebras.cloud.sdk import Cerebras

            # 1. Initialize Cerebras client with API key
            client = Cerebras(api_key=Config.CEREBRAS_API_KEY)

            # 2. Call Llama 3.1 8B model
            response = client.messages.create(
                model="llama-3.1-8b",
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )

            # 3. Parse JSON response
            content = response.content[0].text if response.content else ""

            logger.debug(f"Cerebras response: {content[:200]}...")

            # 4. Validate response format (should be JSON)
            # The response should be JSON, but we'll validate in the service layer

            # 5. Return JSON string
            return content

        except ImportError:
            raise LLMProviderError(
                "Cerebras SDK not installed. Install with: pip install cerebras-sdk"
            )
        except Exception as e:
            logger.error(f"Cerebras API error: {str(e)}")
            raise LLMProviderError(f"Cerebras API call failed: {str(e)}")


class GroqProvider(BaseLLMProvider):
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
        try:
            from groq import Groq

            # 1. Initialize Groq client with API key
            client = Groq(api_key=Config.GROQ_API_KEY)

            # 2. Call LLM model
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                temperature=0.3,
            )

            # 3. Parse JSON response
            content = response.choices[0].message.content if response.choices else ""

            logger.debug(f"Groq response: {content[:200]}...")

            # 4. Validate response format (should be JSON)
            # The response should be JSON, but we'll validate in the service layer

            # 5. Return JSON string
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

    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """
        TODO: Implement Google Gemini API call.

        1. Initialize Gemini client with API key
        2. Call Gemini model
        3. Parse JSON response
        4. Validate response format
        5. Return JSON string
        """
        try:
            import google.generativeai as genai

            # 1. Initialize Gemini client with API key
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-pro", system_instruction=system_prompt)

            # 2. Call Gemini model
            response = model.generate_content(user_prompt)

            # 3. Parse JSON response
            content = response.text if response else ""

            logger.debug(f"Gemini response: {content[:200]}...")

            # 4. Validate response format (should be JSON)
            # The response should be JSON, but we'll validate in the service layer

            # 5. Return JSON string
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
            ConfigurationError: If provider is not supported
        """
        if self.provider_name == LLMProviderEnum.CEREBRAS:
            logger.info("Using Cerebras provider")
            return CerebasProvider()
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
