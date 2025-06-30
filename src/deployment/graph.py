"""
LangGraph application entry point for airline chatbot system.

This module defines the graph that can be deployed to LangGraph Platform.
"""

import os

import openai
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

from src.agents import AirlineAssistant, RedTeamUser
from src.config import get_config
from src.orchestration import ChatSimulator


def create_airline_assistant_graph(config=None):
    """
    Create the airline assistant graph for deployment.
    
    Args:
        config: RunnableConfig provided by LangGraph
        
    Returns:
        Compiled StateGraph ready for deployment
    """
    # Get centralized configuration
    app_config = get_config()

    # Initialize OpenAI client
    openai_client = openai.Client(
        api_key=app_config.openai_api_key or os.getenv("OPENAI_API_KEY")
    )

    # Create the assistant with config defaults
    assistant = AirlineAssistant(
        openai_client=openai_client,
        model=app_config.assistant_model,
        system_prompt=None  # Use default from assistant
    )

    # For deployment, we return just the assistant wrapped in a simple graph
    # The graph accepts messages and returns the assistant's response
    from src.simulation_utils import (
        SimulationState,
        _coerce_to_message,
        _fetch_messages,
    )

    graph_builder = StateGraph(SimulationState)

    # Add a single node for the assistant
    graph_builder.add_node(
        "assistant",
        _fetch_messages | assistant | _coerce_to_message
    )

    # Direct flow from start to assistant to end
    graph_builder.add_edge("__start__", "assistant")
    graph_builder.add_edge("assistant", "__end__")

    return graph_builder.compile()


def create_red_team_simulation_graph(config=None):
    """
    Create the full red team simulation graph.
    
    Args:
        config: RunnableConfig provided by LangGraph
        
    Returns:
        Compiled StateGraph with both agents
    """
    # Get centralized configuration
    app_config = get_config()

    # Initialize clients
    openai_client = openai.Client(
        api_key=app_config.openai_api_key or os.getenv("OPENAI_API_KEY")
    )

    # Create agents using config defaults
    assistant = AirlineAssistant(
        openai_client=openai_client,
        model=app_config.assistant_model
    )

    red_team_user = RedTeamUser(
        llm=ChatOpenAI(
            model=app_config.red_team_model,
            temperature=app_config.temperature,
            max_tokens=app_config.max_tokens
        )
    )

    # Create simulator with config settings
    simulator = ChatSimulator(
        assistant=assistant,
        red_team_user=red_team_user,
        max_turns=app_config.max_turns,
        input_key=app_config.input_key
    )

    # Return the compiled graph
    return simulator.simulator


# Export the graphs with standard names for LangGraph deployment
assistant_graph = create_airline_assistant_graph
simulation_graph = create_red_team_simulation_graph
