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
    skip_example: bool = False
    
    # Execution mode settings
    evaluation_mode: str = "local"  # "local" or "remote"
    langgraph_deployment_url: Optional[str] = None
    langgraph_api_key: Optional[str] = None

    # API keys (loaded from environment)
    openai_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None

    def __post_init__(self) -> None:
        """Load configuration from environment variables."""
        # API Keys
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.langsmith_api_key = os.environ.get("LANGSMITH_API_KEY")
        self.langsmith_project = os.environ.get("LANGSMITH_PROJECT")
        
        # Execution mode
        self.evaluation_mode = os.environ.get("EVALUATION_MODE", "local").lower()
        self.langgraph_deployment_url = os.environ.get("LANGGRAPH_DEPLOYMENT_URL")
        self.langgraph_api_key = os.environ.get("LANGGRAPH_API_KEY")
        
        # Dataset
        self.dataset_name = os.environ.get("DATASET_NAME", self.dataset_name)
        self.dataset_url = os.environ.get("DATASET_URL", self.dataset_url)
        
        # Models
        self.assistant_model = os.environ.get("ASSISTANT_MODEL", self.assistant_model)
        self.red_team_model = os.environ.get("RED_TEAM_MODEL", self.red_team_model)
        self.evaluator_model = os.environ.get("EVALUATOR_MODEL", self.evaluator_model)
        
        # Evaluation settings
        num_examples_env = os.environ.get("NUM_EXAMPLES")
        if num_examples_env:
            self.num_examples = int(num_examples_env)
        
        self.skip_example = os.environ.get("SKIP_EXAMPLE", "false").lower() == "true"
        self.max_turns = int(os.environ.get("MAX_TURNS", str(self.max_turns)))

    def validate(self) -> None:
        """Validate required configuration."""
        # Always required
        required_vars = [("LANGSMITH_API_KEY", self.langsmith_api_key)]
        
        # Mode-specific requirements
        if self.evaluation_mode == "local":
            required_vars.append(("OPENAI_API_KEY", self.openai_api_key))
        else:  # remote
            required_vars.extend([
                ("LANGGRAPH_DEPLOYMENT_URL", self.langgraph_deployment_url),
                ("LANGGRAPH_API_KEY", self.langgraph_api_key)
            ])

        missing = [var for var, value in required_vars if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables for {self.evaluation_mode} mode: "
                f"{', '.join(missing)}. Please set them in your .env file."
            )

