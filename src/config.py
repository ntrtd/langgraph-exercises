"""Configuration settings for the airline chatbot evaluation.

This module provides centralized configuration management for the entire application.
All environment variables and settings should be accessed through the Config class.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Optional, TypedDict

logger = logging.getLogger(__name__)


class ModelConfig(TypedDict):
    """Type definition for model configuration."""
    model: str
    temperature: float
    max_tokens: Optional[int]


class ConfigDict(TypedDict, total=False):
    """Type definition for configuration dictionary (excluding sensitive data)."""
    langsmith_project: Optional[str]
    langgraph_deployment_url: Optional[str]
    default_model: str
    assistant_model: str
    red_team_model: str
    evaluator_model: str
    temperature: float
    max_tokens: Optional[int]
    dataset_url: str
    dataset_name: str
    max_turns: int
    input_key: str
    instructions_key: str
    num_examples: Optional[int]
    skip_example: bool
    evaluation_mode: str
    log_level: str
    log_format: str
    debug: bool
    trace: bool


@dataclass
class Config:
    """Centralized configuration for the airline chatbot evaluation system.
    
    This class serves as the single source of truth for all configuration settings.
    It loads values from environment variables with sensible defaults.
    """

    # ===== API Configuration =====
    # API keys are loaded from environment for security
    openai_api_key: Optional[str] = field(default=None, repr=False)
    langsmith_api_key: Optional[str] = field(default=None, repr=False)
    langgraph_api_key: Optional[str] = field(default=None, repr=False)

    # API endpoints and projects
    langsmith_project: Optional[str] = None
    langgraph_deployment_url: Optional[str] = None

    # ===== Model Configuration =====
    # Default model for all components (ensures consistency)
    default_model: str = "gpt-4o"

    # Component-specific models (default to default_model)
    assistant_model: str = field(default="")
    red_team_model: str = field(default="")
    evaluator_model: str = field(default="")

    # Model parameters
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # ===== Dataset Configuration =====
    dataset_url: str = "https://smith.langchain.com/public/c232f4e0-0fc0-42b6-8f1f-b1fbd30cc339/d"
    dataset_name: str = "Airline Red Teaming"

    # ===== Simulation Configuration =====
    max_turns: int = 10
    input_key: str = "input"
    instructions_key: str = "instructions"

    # ===== Evaluation Configuration =====
    num_examples: Optional[int] = None  # None means run all examples
    skip_example: bool = False
    evaluation_mode: str = "local"  # "local" or "remote"

    # ===== Logging Configuration =====
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ===== System Configuration =====
    # Python version requirement (for validation)
    required_python_version: str = "3.12"

    # Environment name (dev, staging, prod)
    environment: str = "development"

    def __post_init__(self) -> None:
        """Load configuration from environment variables with validation."""
        # ===== API Keys =====
        self.openai_api_key = self._get_env("OPENAI_API_KEY")
        self.langsmith_api_key = self._get_env("LANGSMITH_API_KEY")
        self.langgraph_api_key = self._get_env("LANGGRAPH_API_KEY")

        # ===== API Configuration =====
        self.langsmith_project = self._get_env("LANGSMITH_PROJECT", self.langsmith_project)
        self.langgraph_deployment_url = self._get_env("LANGGRAPH_DEPLOYMENT_URL")

        # ===== Model Configuration =====
        # Allow override of default model
        self.default_model = self._get_env("DEFAULT_MODEL", self.default_model)

        # Component models default to the default_model if not specified
        self.assistant_model = self._get_env("ASSISTANT_MODEL", self.default_model)
        self.red_team_model = self._get_env("RED_TEAM_MODEL", self.default_model)
        self.evaluator_model = self._get_env("EVALUATOR_MODEL", self.default_model)

        # Model parameters
        self.temperature = float(self._get_env("MODEL_TEMPERATURE", str(self.temperature)))
        max_tokens = self._get_env("MODEL_MAX_TOKENS")
        self.max_tokens = int(max_tokens) if max_tokens else None

        # ===== Dataset Configuration =====
        self.dataset_name = self._get_env("DATASET_NAME", self.dataset_name)
        self.dataset_url = self._get_env("DATASET_URL", self.dataset_url)

        # ===== Simulation Configuration =====
        self.max_turns = int(self._get_env("MAX_TURNS", str(self.max_turns)))
        self.input_key = self._get_env("INPUT_KEY", self.input_key)
        self.instructions_key = self._get_env("INSTRUCTIONS_KEY", self.instructions_key)

        # ===== Evaluation Configuration =====
        self.evaluation_mode = self._get_env("EVALUATION_MODE", self.evaluation_mode).lower()
        num_examples_env = self._get_env("NUM_EXAMPLES")
        if num_examples_env:
            self.num_examples = int(num_examples_env)

        self.skip_example = self._get_bool_env("SKIP_EXAMPLE", self.skip_example)

        # ===== Logging Configuration =====
        self.log_level = self._get_env("LOG_LEVEL", self.log_level).upper()
        self.log_format = self._get_env("LOG_FORMAT", self.log_format)

        # ===== System Configuration =====
        self.environment = self._get_env("ENVIRONMENT", self.environment).lower()

        # Log configuration loading
        logger.debug(f"Loaded configuration for {self.environment} environment")

    def validate(self) -> None:
        """Validate required configuration based on execution mode.
        
        Raises:
            ValueError: If required configuration is missing or invalid.
        """
        errors = []

        # Always required
        if not self.langsmith_api_key:
            errors.append("LANGSMITH_API_KEY is required for evaluation tracking")

        # Mode-specific requirements
        if self.evaluation_mode == "local":
            if not self.openai_api_key:
                errors.append("OPENAI_API_KEY is required for local execution")
        elif self.evaluation_mode == "remote":
            if not self.langgraph_deployment_url:
                errors.append("LANGGRAPH_DEPLOYMENT_URL is required for remote execution")
            if not self.langgraph_api_key:
                errors.append("LANGGRAPH_API_KEY is required for remote execution")
        else:
            errors.append(f"Invalid EVALUATION_MODE: {self.evaluation_mode}. Must be 'local' or 'remote'")

        # Validate numeric values
        if self.max_turns <= 0:
            errors.append(f"MAX_TURNS must be positive, got {self.max_turns}")

        if self.temperature < 0 or self.temperature > 2:
            errors.append(f"MODEL_TEMPERATURE must be between 0 and 2, got {self.temperature}")

        if self.num_examples is not None and self.num_examples <= 0:
            errors.append(f"NUM_EXAMPLES must be positive, got {self.num_examples}")

        # Raise all errors at once
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            error_message += "\n\nPlease check your .env file and environment variables."
            raise ValueError(error_message)

        logger.info(f"Configuration validated successfully for {self.evaluation_mode} mode")

    @staticmethod
    def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default."""
        return os.environ.get(key, default)

    @staticmethod
    def _get_bool_env(key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.environ.get(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    def to_dict(self) -> ConfigDict:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return ConfigDict(
            **{k: v for k, v in self.__dict__.items()
               if not k.endswith("_key") or v is None}  # Exclude API keys
        )

    def get_model_config(self, component: str = "default") -> ModelConfig:
        """Get model configuration for a specific component.
        
        Args:
            component: Component name ("assistant", "red_team", "evaluator", or "default")
            
        Returns:
            Dictionary with model configuration
        """
        model_map = {
            "assistant": self.assistant_model,
            "red_team": self.red_team_model,
            "evaluator": self.evaluator_model,
            "default": self.default_model
        }

        return ModelConfig(
            model=model_map.get(component, self.default_model),
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the singleton configuration instance.
    
    This ensures we only load configuration once and reuse it throughout
    the application lifecycle.
    
    Returns:
        The configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
