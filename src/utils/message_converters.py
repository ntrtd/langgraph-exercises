"""Message conversion utilities."""

from typing import Any, Dict, List, TypedDict, Union

from langchain_community.adapters.openai import convert_message_to_dict
from langchain_core.messages import BaseMessage


class OpenAIMessage(TypedDict):
    """OpenAI message format."""
    role: str
    content: str
    name: Union[str, None]  # Optional field


def langchain_to_openai_messages(messages: List[Union[BaseMessage, Dict[str, Any]]]) -> List[OpenAIMessage]:
    """
    Convert a list of langchain base messages to a list of openai messages.

    Parameters:
        messages: A list of langchain base messages or dictionaries.

    Returns:
        List[dict]: A list of openai messages with guaranteed 'role' field.
    """
    result = []
    for m in messages:
        if isinstance(m, BaseMessage):
            # Convert BaseMessage instances using the adapter
            result.append(convert_message_to_dict(m))
        elif isinstance(m, dict):
            # Ensure dict messages have a 'role' field
            msg_dict = m.copy()  # Don't modify the original

            if 'role' not in msg_dict:
                # Try to infer role from 'type' field if present
                if 'type' in msg_dict:
                    type_to_role = {
                        'human': 'user',
                        'ai': 'assistant',
                        'system': 'system',
                        'user': 'user',
                        'assistant': 'assistant'
                    }
                    msg_dict['role'] = type_to_role.get(msg_dict['type'], 'user')
                else:
                    # Default to 'user' if no type info
                    msg_dict['role'] = 'user'

            result.append(msg_dict)
        else:
            # Handle unexpected types by converting to string content
            result.append({
                'role': 'user',
                'content': str(m)
            })

    return result

