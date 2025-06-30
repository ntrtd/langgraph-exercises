"""Configuration settings for the airline chatbot evaluation."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for the airline chatbot evaluation system."""

    # Dataset settings
    dataset_url: str = "https://smith.langchain.com/public/c232f4e0-0fc0-42b6-8f1f-b1fbd30cc339/d"
    dataset_name: str = "Airline Red Teaming"

    # Model settings
    assistant_model: str = "gpt-4o"
    red_team_model: str = "gpt-4o"
    evaluator_model: str = "gpt-4o"

    # Simulation settings
    max_turns: int = 10
    input_key: str = "input"
    
    # Evaluation settings
    num_examples: Optional[int] = None  # None means run all examples

    # API keys (loaded from environment)
    openai_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None

    def __post_init__(self) -> None:
        """Load API keys from environment variables."""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.langsmith_api_key = os.environ.get("LANGSMITH_API_KEY")
        self.langsmith_project = os.environ.get("LANGSMITH_PROJECT")

    def validate(self) -> None:
        """Validate required configuration."""
        required_vars = [
            ("OPENAI_API_KEY", self.openai_api_key),
            ("LANGSMITH_API_KEY", self.langsmith_api_key)
        ]

        missing = [var for var, value in required_vars if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please set them in your .env file."
            )

