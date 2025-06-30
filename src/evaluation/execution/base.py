"""Base classes and interfaces for execution modules."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from langsmith import Client


class ExecutionMode(Enum):
    """Execution mode for evaluation."""
    LOCAL = "local"
    REMOTE = "remote"


class ExampleResult(TypedDict):
    """Result from running a single example."""
    conversation: List[Dict[str, str]]
    success: bool
    error: Optional[str]


class EvaluationSummary(TypedDict, total=False):
    """Summary statistics for evaluation results."""
    total_examples: int
    successful_examples: int
    failed_examples: int
    average_turns: float
    success_rate: float


@dataclass
class EvaluationResult:
    """Result of an evaluation run."""
    experiment_url: str
    num_examples: int
    mode: ExecutionMode
    summary: Optional[EvaluationSummary] = None


class Executor(ABC):
    """Abstract base class for evaluation executors."""

    def __init__(self, langsmith_client: Client):
        """
        Initialize executor.
        
        Args:
            langsmith_client: LangSmith client for tracking evaluations
        """
        self.langsmith_client = langsmith_client

    @abstractmethod
    def create_target(self) -> Any:
        """
        Create the target system to evaluate.
        
        Returns:
            Target that can be evaluated by LangSmith
        """
        pass

    @abstractmethod
    def run_example(self, instructions: str, input_text: str) -> ExampleResult:
        """
        Run a single example for demonstration.
        
        Args:
            instructions: Red team instructions
            input_text: Initial user input
            
        Returns:
            Result dictionary with conversation
        """
        pass

    def evaluate(
        self,
        dataset_name: str,
        evaluators: List[Any],
        num_examples: Optional[int] = None,
        **kwargs
    ) -> EvaluationResult:
        """
        Run evaluation on dataset.
        
        Args:
            dataset_name: Name of LangSmith dataset
            evaluators: List of evaluator functions
            num_examples: Number of examples to run (None for all)
            **kwargs: Additional arguments for evaluate()
            
        Returns:
            EvaluationResult with experiment details
        """
        target = self.create_target()

        if num_examples:
            # Get limited examples
            dataset = self.langsmith_client.read_dataset(dataset_name=dataset_name)
            examples = list(
                self.langsmith_client.list_examples(
                    dataset_id=dataset.id,
                    limit=num_examples
                )
            )
            data = examples
        else:
            # Use full dataset
            data = dataset_name

        # Run evaluation
        result = self.langsmith_client.evaluate(
            target,
            data=data,
            evaluators=evaluators,
            **kwargs
        )

        return EvaluationResult(
            experiment_url=str(result),
            num_examples=num_examples or -1,  # -1 indicates full dataset
            mode=self.get_mode()
        )

    @abstractmethod
    def get_mode(self) -> ExecutionMode:
        """Get the execution mode."""
        pass
