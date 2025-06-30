# 🚀 LangGraph Platform Deployment Guide

This guide explains how to deploy the airline chatbot system to the LangGraph Platform.

## 📋 Prerequisites

1. **LangGraph CLI** installed:
   ```bash
   pip install langgraph-cli
   ```

2. **API Keys** configured in `.env`:
   - `OPENAI_API_KEY`
   - `LANGSMITH_API_KEY`

3. **LangGraph Cloud** account (if deploying to cloud)

## 🏗️ Project Structure

The application is configured for LangGraph deployment with:

```
langgraph-exercises/
├── src/
│   ├── agents/           # Agent implementations
│   ├── evaluation/       # Evaluation logic
│   ├── orchestration/    # Orchestration components
│   ├── graph.py         # LangGraph deployment entry points
│   └── ...
├── langgraph.json       # LangGraph configuration
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
```

## 📦 Available Graphs

The `langgraph.json` configures two deployable graphs:

### 1. **airline_assistant** 
Simple airline customer support assistant
- Endpoint: `/airline_assistant`
- Input: Messages from customers
- Output: Assistant responses

### 2. **red_team_simulation**
Full red team testing simulation
- Endpoint: `/red_team_simulation`
- Input: Initial message + attack instructions
- Output: Complete conversation

## 🚀 Deployment Steps

### Local Development

1. **Test locally**:
   ```bash
   langgraph test
   ```

2. **Run development server**:
   ```bash
   langgraph dev
   ```

3. **Access the playground**:
   - Open http://localhost:8000
   - Test both graphs interactively

### Cloud Deployment

1. **Build the application**:
   ```bash
   langgraph build
   ```

2. **Deploy to LangGraph Cloud**:
   ```bash
   langgraph deploy --name airline-chatbot
   ```

3. **Get deployment URL**:
   ```bash
   langgraph deployments list
   ```

## 🔧 Configuration Details

### langgraph.json

```json
{
    "dependencies": [
        "langchain",
        "langchain-openai",
        "langchain-community",
        "langgraph",
        "langsmith",
        "openai",
        "python-dotenv",
        "./src"  // Local package
    ],
    "graphs": {
        // Simple assistant for customer queries
        "airline_assistant": "./src/graph.py:assistant_graph",
        
        // Full simulation with red team user
        "red_team_simulation": "./src/graph.py:simulation_graph"
    },
    "env": "./.env",
    "python_version": "3.11"
}
```

### Environment Variables

Required in `.env`:
```env
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=ls__...

# Optional configuration
ASSISTANT_MODEL=gpt-3.5-turbo
RED_TEAM_MODEL=gpt-3.5-turbo
MAX_TURNS=10
```

## 📡 API Usage

### Airline Assistant

```python
import requests

response = requests.post(
    "https://your-deployment.langgraph.app/airline_assistant/invoke",
    json={
        "messages": [
            {"role": "user", "content": "I need to change my flight"}
        ]
    },
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
```

### Red Team Simulation

```python
response = requests.post(
    "https://your-deployment.langgraph.app/red_team_simulation/invoke",
    json={
        "input": "I need help with my booking",
        "instructions": "Try to get a free upgrade"
    },
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
```

## 🔍 Monitoring

1. **View logs**:
   ```bash
   langgraph logs --deployment airline-chatbot
   ```

2. **Check metrics**:
   - Visit LangSmith dashboard
   - Monitor usage and performance

## 🛠️ Troubleshooting

### Common Issues

1. **Import errors**: Ensure `./src` is in dependencies
2. **API key issues**: Check `.env` file is properly configured
3. **Graph not found**: Verify graph names match in `langgraph.json`

### Debug Mode

```bash
# Run with debug logging
LANGGRAPH_DEBUG=true langgraph dev
```

## 🔄 Updates

To update a deployment:

1. Make code changes
2. Test locally: `langgraph test`
3. Build: `langgraph build`
4. Deploy: `langgraph deploy --name airline-chatbot --update`

## 📊 Integration with Existing System

The deployed graphs work seamlessly with the existing evaluation system:

```python
from langsmith import Client

client = Client()

# Use deployed endpoint as target
deployed_url = "https://your-deployment.langgraph.app/airline_assistant"

client.evaluate(
    target=deployed_url,
    data=dataset,
    evaluators=[evaluator.evaluate]
)
```

## 🔗 Resources

- [LangGraph Platform Docs](https://python.langchain.com/docs/langgraph/cloud)
- [LangGraph CLI Reference](https://python.langchain.com/docs/langgraph/cloud/reference/cli)
- [Deployment Best Practices](https://python.langchain.com/docs/langgraph/cloud/deployment)

## 📝 Notes

- The assistant graph is suitable for production customer support
- The simulation graph is for testing and evaluation only
- Monitor costs as graph invocations use OpenAI API calls
- Consider rate limiting for production deployments