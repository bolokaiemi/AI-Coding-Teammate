"""
AI Client
=========

Provider client for the AI Coding Teammate.

Responsibilities:
- Read AI provider configuration
- Connect to the OpenAI API
- Send single prompts
- Send conversation history
- Return normalized response dictionaries
- Provide safe fallback behavior when no API key is configured

This module deliberately does not import AIEngine at module level.
That helps prevent circular imports.
"""

import os
import time

from openai import OpenAI


class AIClient:
    """OpenAI provider client for the AI Coding Teammate."""

    def __init__(
        self,
        engine=None,
        api_key=None,
        model=None,
    ):
        """
        Initialize the AI client.

        Args:
            engine:
                Optional AIEngine instance.

            api_key:
                Optional OpenAI API key.
                Defaults to OPENAI_API_KEY.

            model:
                Optional model name.
                Defaults to OPENAI_MODEL.
        """

        self.engine = engine

        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        self.model = (
            model
            or os.getenv(
                "OPENAI_MODEL",
                "gpt-5.6",
            )
        )

        self.client = None

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key
            )

    # =========================================================
    # PROVIDER STATUS
    # =========================================================

    def _provider_status(self):
        """
        Return provider configuration status.
        """

        return {
            "configured": bool(self.api_key),
            "provider": "openai",
            "model": self.model,
        }

    def status(self):
        """
        Return AI provider status.

        This method does not delegate to AIEngine because doing
        so could create an:

            AIEngine -> AIClient -> AIEngine

        recursion loop.
        """

        return self._provider_status()

    # =========================================================
    # SINGLE PROMPT
    # =========================================================

    def ask(self, prompt: str):
        """
        Send a single prompt to the AI provider.

        Returns:
            {
                "success": bool,
                "content": str,
                "model": str,
                "model_name": str,
                "processing_time": float,
                "error": str | None
            }
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Prompt must be supplied as a string."
            )

        prompt = prompt.strip()

        if not prompt:
            return {
                "success": False,
                "content": "",
                "model": self.model,
                "model_name": self.model,
                "processing_time": 0,
                "error": "Prompt cannot be empty.",
            }

        # -----------------------------------------------------
        # DEVELOPMENT FALLBACK
        # -----------------------------------------------------

        if not self.client:
            return {
                "success": True,
                "content": (
                    "[Development mode] "
                    "No OpenAI API key is configured."
                ),
                "model": self.model,
                "model_name": self.model,
                "processing_time": 0,
                "development_mode": True,
                "error": None,
            }

        # -----------------------------------------------------
        # OPENAI REQUEST
        # -----------------------------------------------------

        started_at = time.perf_counter()

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
            )

            processing_time = (
                time.perf_counter()
                - started_at
            )

            content = (
                response.output_text
                or ""
            )

            return {
                "success": True,
                "content": content,
                "model": self.model,
                "model_name": self.model,
                "processing_time": processing_time,
                "error": None,
            }

        except Exception as error:
            processing_time = (
                time.perf_counter()
                - started_at
            )

            return {
                "success": False,
                "content": "",
                "model": self.model,
                "model_name": self.model,
                "processing_time": processing_time,
                "error": str(error),
            }

    # =========================================================
    # CHAT / CONVERSATION
    # =========================================================

    def chat(self, messages):
        """
        Send conversation history to the AI provider.

        Expected input:

        [
            {
                "role": "system",
                "content": "You are an AI coding teammate."
            },
            {
                "role": "user",
                "content": "Explain this code."
            },
            {
                "role": "assistant",
                "content": "..."
            }
        ]
        """

        if not isinstance(messages, list):
            raise TypeError(
                "Messages must be supplied as a list."
            )

        if not messages:
            return {
                "success": False,
                "content": "",
                "model": self.model,
                "model_name": self.model,
                "processing_time": 0,
                "error": (
                    "Conversation history is empty."
                ),
            }

        # -----------------------------------------------------
        # VALIDATE / NORMALIZE MESSAGES
        # -----------------------------------------------------

        normalized_messages = []

        allowed_roles = {
            "system",
            "user",
            "assistant",
            "developer",
        }

        for message in messages:

            if not isinstance(message, dict):
                continue

            role = message.get(
                "role",
                "user",
            )

            content = message.get(
                "content",
                "",
            )

            if role not in allowed_roles:
                role = "user"

            if content is None:
                continue

            content = str(content).strip()

            if not content:
                continue

            normalized_messages.append({
                "role": role,
                "content": content,
            })

        if not normalized_messages:
            return {
                "success": False,
                "content": "",
                "model": self.model,
                "model_name": self.model,
                "processing_time": 0,
                "error": (
                    "No valid conversation messages "
                    "were supplied."
                ),
            }

        # -----------------------------------------------------
        # DEVELOPMENT FALLBACK
        # -----------------------------------------------------

        if not self.client:
            return {
                "success": True,
                "content": (
                    "[Development mode] "
                    "No OpenAI API key is configured."
                ),
                "model": self.model,
                "model_name": self.model,
                "processing_time": 0,
                "development_mode": True,
                "error": None,
            }

        # -----------------------------------------------------
        # OPENAI REQUEST
        # -----------------------------------------------------

        started_at = time.perf_counter()

        try:
            response = self.client.responses.create(
                model=self.model,
                input=normalized_messages,
            )

            processing_time = (
                time.perf_counter()
                - started_at
            )

            content = (
                response.output_text
                or ""
            )

            return {
                "success": True,
                "content": content,
                "model": self.model,
                "model_name": self.model,
                "processing_time": processing_time,
                "error": None,
            }

        except Exception as error:
            processing_time = (
                time.perf_counter()
                - started_at
            )

            return {
                "success": False,
                "content": "",
                "model": self.model,
                "model_name": self.model,
                "processing_time": processing_time,
                "error": str(error),
            }

    # =========================================================
    # AI ENGINE CONVENIENCE METHODS
    # =========================================================

    def analyze(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Delegate code analysis to AIEngine.
        """

        self._require_engine()

        return self.engine.analyze_code(
            code=code,
            language=language,
            filename=filename,
        )

    def correct(
        self,
        code,
        error=None,
        language="text",
        filename="untitled",
    ):
        """
        Delegate code correction to AIEngine.
        """

        self._require_engine()

        problems = None

        if error:
            problems = [error]

        return self.engine.correct_code(
            code=code,
            language=language,
            filename=filename,
            problems=problems,
        )

    def explain(
        self,
        code,
        language="text",
        filename="untitled",
    ):
        """
        Delegate code explanation to AIEngine.
        """

        self._require_engine()

        return self.engine.explain_code(
            code=code,
            language=language,
            filename=filename,
        )

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    def _require_engine(self):
        """
        Ensure an AIEngine instance is available before using
        engine convenience methods.
        """

        if self.engine is None:
            raise RuntimeError(
                "AIEngine is not attached to AIClient. "
                "Use CodeAnalyzer, CodeCorrector, or "
                "CodeExplainer directly, or initialize "
                "AIClient with an engine."
            )