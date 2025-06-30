"""Message conversion utilities."""

from typing import Any, Dict, List

from langchain_community.adapters.openai import convert_message_to_dict
from langchain_core.messages import BaseMessage


def langchain_to_openai_messages(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """
    Convert a list of langchain base messages to a list of openai messages.

    Parameters:
        messages (List[BaseMessage]): A list of langchain base messages.

    Returns:
        List[dict]: A list of openai messages.
    """
    return [
        convert_message_to_dict(m) if isinstance(m, BaseMessage) else m
        for m in messages
    ]

