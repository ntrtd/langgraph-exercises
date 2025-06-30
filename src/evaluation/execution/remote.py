"""Remote execution via deployed LangGraph API."""

from typing import Any, Dict, List, Optional, TypedDict

import requests
from langsmith import Client

from .base import ExampleResult, ExecutionMode, Executor


class RemoteResponse(TypedDict):
    """Response from remote LangGraph API."""
    messages: List[Dict[str, str]]
    status: str
    error: Optional[str]


class RemoteSimulator:
    """Wrapper for remote LangGraph deployment."""

    def __init__(self, base_url: str, api_key: str, graph_name: str = "red_team_simulation"):
        """
        Initialize remote simulator.
        
        Args:
            base_url: Base URL of LangGraph deployment
            api_key: API key for authentication
            graph_name: Name of the graph to invoke
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.graph_name = graph_name

    def invoke(self, inputs: Dict[str, Any]) -> RemoteResponse:
        """
        Invoke the remote graph.
        
        Args:
            inputs: Input dictionary with 'input' and 'instructions'
            
        Returns:
            Response from the remote graph
        """
        url = f"{self.base_url}/assistants/{self.graph_name}/invoke"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=inputs, headers=headers)
        response.raise_for_status()

        return response.json()

    def stream(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Stream from the remote graph.
        
        Args:
            inputs: Input dictionary
            
        Returns:
            List of events (simulated streaming)
        """
        # For remote execution, we invoke and simulate streaming
        result = self.invoke(inputs)

        # Convert result to event stream format
        events = []
        if "messages" in result:
            for i, message in enumerate(result["messages"]):
                role = "assistant" if i % 2 == 0 else "user"
                events.append({
                    role: {
                        "messages": result["messages"][:i+1]
                    }
                })
        events.append({"__end__": {}})

        return events


class RemoteExecutor(Executor):
    """Execute evaluations using remote LangGraph deployment."""

    def __init__(
        self,
        langsmith_client: Client,
        deployment_url: str,
        deployment_api_key: str,
        graph_name: str = "red_team_simulation"
    ):
        """
        Initialize remote executor.
        
        Args:
            langsmith_client: LangSmith client
            deployment_url: URL of LangGraph deployment
            deployment_api_key: API key for deployment
            graph_name: Name of the graph to use
        """
        super().__init__(langsmith_client)
        self.deployment_url = deployment_url
        self.deployment_api_key = deployment_api_key
        self.graph_name = graph_name

        # Create remote simulator
        self.simulator = RemoteSimulator(
            base_url=deployment_url,
            api_key=deployment_api_key,
            graph_name=graph_name
        )

    def create_target(self) -> Any:
        """Create the remote target."""
        return self.simulator

    def run_example(self, instructions: str, input_text: str) -> ExampleResult:
        """Run a single example remotely."""
        try:
            result = self.simulator.invoke({
                "input": input_text,
                "instructions": instructions
            })

            # Extract messages from result
            messages = []
            if isinstance(result, dict) and "messages" in result:
                for msg in result["messages"]:
                    if isinstance(msg, dict):
                        messages.append({
                            "role": msg.get("type", "unknown"),
                            "content": msg.get("content", "")
                        })

            return ExampleResult(
                conversation=messages,
                success=True,
                error=None
            )

        except requests.exceptions.RequestException as e:
            return ExampleResult(
                conversation=[],
                success=False,
                error=str(e)
            )

    def get_mode(self) -> ExecutionMode:
        """Get execution mode."""
        return ExecutionMode.REMOTE
