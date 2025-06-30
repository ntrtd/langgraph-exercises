"""
LangGraph application entry point for airline chatbot system.

This module defines the graph that can be deployed to LangGraph Platform.
"""

import os
from typing import Optional

import openai
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

from src.agents import AirlineAssistant, RedTeamUser
from src.orchestration import ChatSimulator
from src.simulation_utils import create_chat_simulator


def create_airline_assistant_graph(config=None):
    """
    Create the airline assistant graph for deployment.
    
    Args:
        config: RunnableConfig provided by LangGraph
        
    Returns:
        Compiled StateGraph ready for deployment
    """
    model = None
    system_prompt = None
    # Get configuration from environment
    model = model or os.getenv("ASSISTANT_MODEL", "gpt-3.5-turbo")
    
    # Initialize OpenAI client
    openai_client = openai.Client(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create the assistant
    assistant = AirlineAssistant(
        openai_client=openai_client,
        model=model,
        system_prompt=system_prompt
    )
    
    # For deployment, we return just the assistant wrapped in a simple graph
    # The graph accepts messages and returns the assistant's response
    from src.simulation_utils import SimulationState, _coerce_to_message, _fetch_messages
    
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
    assistant_model = None
    red_team_model = None
    max_turns = None
    # Get configuration
    assistant_model = assistant_model or os.getenv("ASSISTANT_MODEL", "gpt-3.5-turbo")
    red_team_model = red_team_model or os.getenv("RED_TEAM_MODEL", "gpt-3.5-turbo")
    max_turns = max_turns or int(os.getenv("MAX_TURNS", "10"))
    
    # Initialize clients
    openai_client = openai.Client(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create agents
    assistant = AirlineAssistant(
        openai_client=openai_client,
        model=assistant_model
    )
    
    red_team_user = RedTeamUser(
        llm=ChatOpenAI(model=red_team_model)
    )
    
    # Create simulator
    simulator = ChatSimulator(
        assistant=assistant,
        red_team_user=red_team_user,
        max_turns=max_turns,
        input_key="input"
    )
    
    # Return the compiled graph
    return simulator.simulator


# Export the graphs with standard names for LangGraph deployment
assistant_graph = create_airline_assistant_graph
simulation_graph = create_red_team_simulation_graph
