"""Local execution of red team evaluation."""

import os
from typing import Any

import openai
from langchain_openai import ChatOpenAI
from langsmith import Client

from ...agents import AirlineAssistant, RedTeamUser
from ...orchestration import ChatSimulator
from .base import ExampleResult, ExecutionMode, Executor


class LocalExecutor(Executor):
    """Execute evaluations locally using in-process agents."""

    def __init__(
        self,
        langsmith_client: Client,
        assistant_model: str,
        red_team_model: str,
        max_turns: int,
        openai_api_key: str = None
    ):
        """
        Initialize local executor.
        
        Args:
            langsmith_client: LangSmith client
            assistant_model: Model for assistant
            red_team_model: Model for red team user
            max_turns: Maximum conversation turns
            openai_api_key: OpenAI API key (optional, uses env var if not provided)
        """
        super().__init__(langsmith_client)
        self.assistant_model = assistant_model
        self.red_team_model = red_team_model
        self.max_turns = max_turns

        # Initialize OpenAI client
        self.openai_client = openai.Client(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )

        # Create agents
        self.assistant = AirlineAssistant(
            openai_client=self.openai_client,
            model=self.assistant_model
        )

        self.red_team_user = RedTeamUser(
            llm=ChatOpenAI(model=self.red_team_model)
        )

        # Create simulator
        self.simulator = ChatSimulator(
            assistant=self.assistant,
            red_team_user=self.red_team_user,
            max_turns=self.max_turns,
            input_key="input"
        )

    def create_target(self) -> Any:
        """Create the local simulation target."""
        return self.simulator.simulator

    def run_example(self, instructions: str, input_text: str) -> ExampleResult:
        """Run a single example locally."""
        events = list(self.simulator.stream({
            "input": input_text,
            "instructions": instructions
        }))

        # Extract messages from events
        messages = []
        for event in events:
            if "__end__" in event:
                break
            role, state = next(iter(event.items()))
            if "messages" in state and state["messages"]:
                last_message = state["messages"][-1]
                messages.append({
                    "role": role,
                    "content": last_message.content
                })

        try:
            return ExampleResult(
                conversation=messages,
                success=True,
                error=None
            )
        except Exception as e:
            return ExampleResult(
                conversation=[],
                success=False,
                error=str(e)
            )

    def get_mode(self) -> ExecutionMode:
        """Get execution mode."""
        return ExecutionMode.LOCAL
