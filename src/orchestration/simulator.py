"""Chat simulator for orchestrating conversations between agents."""

from typing import Any, Callable, List, TypedDict, Union

from langchain_core.messages import AnyMessage

from ..agents import AirlineAssistant, RedTeamUser
from ..simulation_utils import SimulationState
from ..simulation_utils import create_chat_simulator as _create_chat_simulator


class SimulatorInputs(TypedDict):
    """Input parameters for simulator."""
    input: str
    instructions: str


class ChatSimulator:
    """Orchestrates chat simulations between assistant and red team user."""

    def __init__(
        self,
        assistant: Union[AirlineAssistant, Callable[[List[AnyMessage]], str]],
        red_team_user: RedTeamUser,
        max_turns: int = 10,
        input_key: str = "input"
    ):
        """
        Initialize the chat simulator.

        Args:
            assistant: The assistant to test
            red_team_user: The red team user
            max_turns: Maximum conversation turns
            input_key: Key for initial input
        """
        self.assistant = assistant
        self.red_team_user = red_team_user
        self.max_turns = max_turns
        self.input_key = input_key

        # Create the simulation graph
        self.simulator = self._create_simulator()

    def _create_simulator(self) -> Any:
        """Create the LangGraph simulator."""
        # Get the assistant callable
        assistant_callable = (
            self.assistant if callable(self.assistant)
            else self.assistant.__call__
        )

        # Get the red team user runnable
        simulated_user = self.red_team_user.get_runnable()

        return _create_chat_simulator(
            assistant=assistant_callable,
            simulated_user=simulated_user,
            input_key=self.input_key,
            max_turns=self.max_turns,
        )

    def stream(self, inputs: SimulatorInputs) -> Any:
        """
        Stream the simulation.

        Args:
            inputs: Input dictionary with 'input' and 'instructions'

        Yields:
            Events from the simulation
        """
        return self.simulator.stream(inputs)

    def invoke(self, inputs: SimulatorInputs) -> SimulationState:
        """
        Run the simulation.

        Args:
            inputs: Input dictionary with 'input' and 'instructions'

        Returns:
            Final state of the simulation
        """
        result = self.simulator.invoke(inputs)
        return dict(result) if result else {}

