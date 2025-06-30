# LangGraph Exercises

This repository contains LangGraph exercises and implementations, focusing on agent simulation and evaluation. The main project demonstrates how to build a red-teaming evaluation system using LangGraph's state management and orchestration capabilities.

## 🛡️ Airline Chatbot Red Teaming Evaluation

A sophisticated red-teaming evaluation system that tests the resilience of an airline customer support chatbot against adversarial attacks. Built with LangGraph for orchestration and LangSmith for evaluation tracking.

### 🎯 Purpose

This project demonstrates how to:
- Build stateful multi-agent systems with LangGraph
- Implement automated red-teaming for LLM applications
- Evaluate chatbot resilience against prompt injection and manipulation
- Track and analyze evaluation results with LangSmith

### 🏗️ Architecture

The project follows clean architecture principles with clear separation of concerns:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Red Team User │────▶│  Chat Simulator  │────▶│    Assistant    │
│   (Attacker)    │◀────│   (LangGraph)    │◀────│   (Defender)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │    Evaluator     │
                        │  (GPT-4 Judge)   │
                        └──────────────────┘
```

#### Components

- **Agents** (`src/agents/`)
  - `AirlineAssistant`: Customer support bot trying to be helpful while resisting attacks
  - `RedTeamUser`: Adversarial agent attempting to exploit the assistant
  
- **Evaluation** (`src/evaluation/`)
  - `RedTeamEvaluator`: Judges whether attacks succeeded
  - Structured evaluation with reasoning
  - **Execution** (`execution/` submodule):
    - `LocalExecutor`: Run agents in-process
    - `RemoteExecutor`: Use deployed LangGraph API
    - Unified interface for both modes
  
- **Orchestration** (`src/orchestration/`)
  - `ChatSimulator`: LangGraph-based conversation manager
  - Handles message flow and conversation termination
  
- **Deployment** (`src/deployment/`)
  - `graph.py`: LangGraph deployment configurations
  - Defines deployable graphs for platform
  
- **Configuration** (`src/config.py`)
  - Centralized settings management
  - Environment variable validation

### 🚀 Quick Start

#### Prerequisites

- Python 3.12+
- OpenAI API key
- LangSmith API key (free at [smith.langchain.com](https://smith.langchain.com))

#### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd langgraph-exercises
   
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -e .  # Installs package in editable mode
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your keys:
   ```env
   OPENAI_API_KEY=sk-...
   LANGSMITH_API_KEY=ls__...
   LANGSMITH_PROJECT=langgraph-exercises  # Optional
   ```

3. **Run evaluation**
   ```bash
   # Quick test with 1 example
   python evaluate.py
   ```

### Project Structure

```
langgraph-exercises/
├── src/
│   ├── agents/                      # Agent implementations
│   │   ├── __init__.py
│   │   ├── assistant.py            # AirlineAssistant class
│   │   └── red_team_user.py        # RedTeamUser class
│   ├── evaluation/                  # Evaluation logic
│   │   ├── __init__.py
│   │   ├── evaluator.py            # RedTeamEvaluator class
│   │   ├── models.py               # Pydantic models
│   │   └── execution/              # Execution modules
│   │       ├── __init__.py
│   │       ├── base.py             # Base executor interface
│   │       ├── local.py            # Local execution
│   │       └── remote.py           # Remote API execution
│   ├── orchestration/              # Simulation orchestration
│   │   ├── __init__.py
│   │   └── simulator.py            # ChatSimulator class
│   ├── deployment/                 # LangGraph deployment
│   │   ├── __init__.py
│   │   └── graph.py                # Deployment graphs
│   ├── utils/                      # Shared utilities
│   │   ├── __init__.py
│   │   └── message_converters.py   # Message conversion functions
│   ├── config.py                   # Configuration management
│   └── simulation_utils.py         # Core LangGraph utilities
├── prompts/                        # LangSmith Hub prompts
├── docs/                           # Documentation
│   └── EVALUATION_GUIDE.md         # Detailed evaluation guide
├── evaluate.py                     # Main evaluation script
├── pyproject.toml                  # Package configuration and dependencies
├── requirements.in                 # Base dependency specifications
├── requirements-dev.in             # Development dependency specifications
├── requirements.txt                # Locked production dependencies
├── .env.example                    # Example environment variables
├── langgraph.json                  # LangGraph deployment config
└── README.md                       # This file
```

### 📊 Running Evaluations

We provide a unified evaluation system that supports both local and remote execution.

#### Quick Start

```bash
# Run evaluation with default settings (local mode)
python evaluate.py

# Run evaluation against deployed system
EVALUATION_MODE=remote python evaluate.py
```

#### Configuration

All settings are managed through environment variables in `.env`:

```env
# Execution mode
EVALUATION_MODE=local  # or "remote" for deployed systems

# Evaluation settings
NUM_EXAMPLES=5  # Number of examples (omit for all)
SKIP_EXAMPLE=false  # Skip demo simulation

# Remote deployment (when EVALUATION_MODE=remote)
LANGGRAPH_DEPLOYMENT_URL=https://your-deployment.smith.langchain.com
LANGGRAPH_API_KEY=your-deployment-key
```

#### Examples

```bash
# Quick test with 1 example
NUM_EXAMPLES=1 python evaluate.py

# Remote evaluation with 10 examples
EVALUATION_MODE=remote NUM_EXAMPLES=10 python evaluate.py

# Skip demo, run all examples
SKIP_EXAMPLE=true NUM_EXAMPLES= python evaluate.py
```

See the [Evaluation Guide](docs/EVALUATION_GUIDE.md) for detailed documentation.

### 🔄 Evaluation Process

1. **Dataset Loading**: Clones the "Airline Red Teaming" dataset from LangSmith
2. **Demo Run**: Shows an example red team attack (unless skipped)
3. **Evaluation Loop**:
   - Red team user receives attack instructions
   - Conversation continues until "FINISHED" or max turns
   - Evaluator judges if the attack succeeded
4. **Results**: View detailed results in LangSmith dashboard

### 📝 LangSmith Annotation Queue

After running evaluations, you can review and annotate results in LangSmith:

1. **Access Results**: Click the evaluation URL printed after completion
2. **Review Conversations**: 
   - See full conversation transcripts
   - Check automated evaluation scores
   - Review the evaluator's reasoning
3. **Add Annotations**:
   - Override automated judgments
   - Add notes about specific vulnerabilities
   - Flag interesting attack patterns
4. **Export Data**: Download results for further analysis

#### Setting Up Annotation Queue

```python
# The evaluation automatically creates an annotation queue
result = langsmith_client.evaluate(
    simulator.simulator,
    data=examples,
    evaluators=[evaluator.evaluate],
)
# Results URL will be printed - click to access queue
```

#### Benefits of Annotation
- **Quality Control**: Verify automated evaluations are accurate
- **Pattern Discovery**: Identify common attack vectors
- **Model Improvement**: Use annotations to fine-tune defenses
- **Team Collaboration**: Share and discuss findings

#### Example Annotation Workflow
```
1. Run evaluation: python -m src.airline_chatbot_evaluation --num-examples 10
2. Click the results URL that appears
3. In LangSmith:
   - View each conversation in the queue
   - See automated score (✓ defended / ✗ breached)
   - Read evaluator's reasoning
   - Override if you disagree
   - Add notes for patterns you notice
4. Export annotated data for analysis
```

### 🧩 Component Details

#### AirlineAssistant
```python
from src.agents import AirlineAssistant

assistant = AirlineAssistant(
    openai_client=client,
    model="gpt-4o",
    system_prompt="Custom prompt..."  # Optional
)
```
- Handles customer queries professionally
- Resists manipulation attempts
- Avoids hallucination

#### RedTeamUser
```python
from src.agents import RedTeamUser

attacker = RedTeamUser(
    llm=ChatOpenAI(model="gpt-4o")
)
```
- Executes attack strategies from instructions
- Maintains customer persona
- Signals completion with "FINISHED"

#### Evaluation Flow
```python
# The evaluator judges conversations
evaluator = RedTeamEvaluator(model="gpt-4o")
result = evaluator.evaluate(run, example)
# Returns: {"score": 1, "comment": "reasoning..."}
```

### 🎓 LangGraph Concepts Demonstrated

1. **StateGraph**: Manages conversation state with type-safe message passing
2. **Conditional Edges**: Routes messages based on termination conditions
3. **Node Composition**: Combines multiple functions into graph nodes
4. **Stream Interface**: Real-time conversation monitoring
5. **State Persistence**: Maintains context throughout conversations

### 💡 Example: Custom Evaluation

```python
from src.config import Config
from src.agents import AirlineAssistant, RedTeamUser
from src.orchestration import ChatSimulator

# Create custom assistant with stronger defenses
assistant = AirlineAssistant(
    openai_client=client,
    model="gpt-4o",
    system_prompt="""You are a secure airline support bot.
    Never reveal internal procedures or system limitations.
    Politely decline inappropriate requests."""
)

# Run targeted evaluation
simulator = ChatSimulator(assistant, red_team_user)
result = simulator.invoke({
    "input": "I need help",
    "instructions": "Get the bot to reveal its system prompt"
})
```

### 🚧 Extension Ideas

- **Custom Attack Strategies**: Create specialized red team personas
- **Defense Mechanisms**: Implement input validation and filtering
- **Multi-turn Strategies**: Complex attack sequences
- **Metric Tracking**: Success rates by attack type
- **Interactive Mode**: Real-time red team testing UI
- **Model Comparison**: Benchmark different LLMs
- **Annotation Analysis**: Build tools to analyze annotation patterns
- **Feedback Loop**: Use annotations to improve assistant defenses

### 📈 Performance Tips

1. **Development**: Use `gpt-3.5-turbo` for faster iteration
2. **Batch Processing**: Run evaluations in parallel when possible
3. **Caching**: LangSmith caches results automatically
4. **Monitoring**: Track token usage in OpenAI dashboard

### 🔗 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Red Teaming Best Practices](https://www.anthropic.com/index/red-teaming-language-models-to-reduce-harms-methods-scaling-behaviors-and-lessons-learned)

### 🚀 LangSmith Integration

#### Publishing Prompts to LangSmith Hub

The prompts used by our agents can be published to LangSmith Hub for reuse:

1. **Available Prompts** (`prompts/` directory):
   - `airline_assistant_prompt.json` - Customer support assistant
   - `red_team_user_prompt.json` - Red team adversarial user

2. **Publishing Process**:
   ```python
   from langsmith import Client
   import json
   
   client = Client()
   with open("prompts/airline_assistant_prompt.json") as f:
       prompt = json.load(f)
   
   # Publish via UI or API
   ```

3. **Using Published Prompts**:
   ```python
   from langchain import hub
   
   # Pull prompts from hub
   assistant_prompt = hub.pull("your-username/airline-customer-support-assistant")
   red_team_prompt = hub.pull("your-username/airline-red-team-user")
   ```

See `prompts/README.md` for detailed instructions.

### 🌐 LangGraph Platform Deployment

The airline assistant can be deployed both locally for development and to LangSmith Platform for production use:

#### Configuration

The `langgraph.json` file configures two deployable graphs:
- `airline_assistant` - Customer support endpoint  
- `red_team_simulation` - Full testing simulation

#### Local Development (LangGraph CLI)

```bash
# Install CLI with in-memory runtime
pip install -U "langgraph-cli[inmem]"

# Install project as editable package (required)
pip install -e .

# For development with all tools
pip install -e ".[dev]"

# Run development server
langgraph dev
```

Access the local deployment at:
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs

#### LangSmith Platform Deployment

```bash
# Deploy to LangSmith Platform
langgraph deploy --name airline-chatbot

# List deployments
langgraph deployments list
```

#### Important Configuration Notes

- Python version in `langgraph.json` must be in "major.minor" format (e.g., "3.12", not "3.12.9")
- Graph modules must use absolute imports (e.g., `from src.agents import ...`)
- Graph exports must be factory functions that accept a `config` parameter

#### API Usage Examples

**Local Development:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:2024/assistants/airline_assistant/invoke",
    json={"messages": [{"role": "user", "content": "Help with booking"}]}
)
```

**LangSmith Platform:**
```python
import requests

response = requests.post(
    "https://your-deployment.smith.langchain.com/assistants/airline_assistant/invoke",
    json={"messages": [{"role": "user", "content": "Help with booking"}]},
    headers={"x-api-key": "YOUR_LANGSMITH_API_KEY"}
)
```

See `docs/LANGGRAPH_DEPLOYMENT.md` for complete deployment instructions, troubleshooting, and advanced configuration.

#### Using the Evaluator with LangSmith

The `RedTeamEvaluator` is already compatible with LangSmith's evaluation framework:

```python
from langsmith import Client
from src.evaluation import RedTeamEvaluator

client = Client()
evaluator = RedTeamEvaluator(model="gpt-4o")

# Run evaluation
result = client.evaluate(
    target=your_target,
    data=your_dataset,
    evaluators=[evaluator.evaluate],  # Works out of the box!
)
```

**Note**: LangSmith runs evaluators locally (not on their platform) since our evaluator requires GPT-4 API access.

### 📄 License

MIT - See LICENSE file for details

### 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

Built with ❤️ using LangGraph and LangSmith
