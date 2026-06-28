from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings


class LLMManager:
    def __init__(self):
        self.claude = self._get_claude()
        self.gemini = self._get_gemini()

        self.model_capabilities = {
            "claude": {
                "max_tokens": 4096,
                "best_for": "reasoning, writing, complex tasks",
                "cost": "medium",
            },
            "gpt4": {
                "max_tokens": 8192,
                "best_for": "structured output, json, code",
                "cost": "high",
            },
            "groq": {
                "max_tokens": 2048,
                "best_for": "fast responses, simple tasks",
                "cost": "low",
            },
        }

    def _get_claude(self) -> ChatAnthropic:
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model="claude-haikus-4-sonnet-20260315",
        )

    def _get_gemini(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            api_key=settings.google_api_key,
            model="gemini-2.5-flash",
        )

    def get_model(self, model_name: Literal["claude", "gemini"]) -> BaseChatModel:
        if model_name == "claude":
            return self._get_claude()
        elif model_name == "gemini":
            return self._get_gemini()
        else:
            raise ValueError(f"Invalid model name: {model_name}")

    def get_model_capabilities(self, model_name: Literal["claude", "gemini"]) -> dict:
        return self.model_capabilities[model_name]


llm_manager = LLMManager()
