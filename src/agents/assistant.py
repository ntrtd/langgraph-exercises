"""Airline customer support assistant implementation."""

from typing import List, Optional

import openai
from langchain_core.messages import BaseMessage

from ..utils.message_converters import langchain_to_openai_messages


class AirlineAssistant:
    """Customer support assistant for an airline."""

    def __init__(
        self,
        openai_client: openai.Client,
        model: str = "gpt-3.5-turbo",
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the airline assistant.

        Args:
            openai_client: OpenAI client instance
            model: Model to use for the assistant
            system_prompt: Optional custom system prompt
        """
        self.client = openai_client
        self.model = model
        self.system_prompt = system_prompt or (
            "You are a customer support agent for an airline. "
            "Be as helpful as possible, but don't invent any unknown information."
        )

    def __call__(self, messages: List[BaseMessage]) -> str:
        """
        Process messages and return assistant's response.

        Args:
            messages: List of conversation messages

        Returns:
            str: The assistant's response
        """
        oai_messages = langchain_to_openai_messages(messages)
        system_message = {
            "role": "system",
            "content": self.system_prompt,
        }

        all_messages = [system_message] + oai_messages

        completion = self.client.chat.completions.create(
            messages=all_messages,
            model=self.model
        )

        content = completion.choices[0].message.content
        return content if content else ""

