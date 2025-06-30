# Configuration Guide

This guide explains all configuration options available in the LangGraph Exercises project.

## Overview

The project uses a centralized configuration system managed through the `Config` class in `src/config.py`. All settings are loaded from environment variables with sensible defaults.

## Configuration Hierarchy

1. **Environment Variables** - Highest priority
2. **`.env` file** - Loaded via python-dotenv
3. **Default values** - Built into Config class

## Environment Variables

### API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (local mode) | None | OpenAI API key for local execution |
| `LANGSMITH_API_KEY` | Yes | None | LangSmith API key for evaluation tracking |
| `LANGGRAPH_API_KEY` | Yes (remote mode) | None | API key for deployed LangGraph instance |
| `LANGSMITH_PROJECT` | No | None | LangSmith project name for organization |
| `LANGGRAPH_DEPLOYMENT_URL` | Yes (remote mode) | None | URL of deployed LangGraph instance |

### Model Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEFAULT_MODEL` | No | `gpt-4o` | Default model for all components |
| `ASSISTANT_MODEL` | No | `{DEFAULT_MODEL}` | Model for airline assistant |
| `RED_TEAM_MODEL` | No | `{DEFAULT_MODEL}` | Model for red team attacker |
| `EVALUATOR_MODEL` | No | `{DEFAULT_MODEL}` | Model for evaluation judge |
| `MODEL_TEMPERATURE` | No | `0.7` | Temperature for model responses (0-2) |
| `MODEL_MAX_TOKENS` | No | None | Maximum tokens for responses |

### Dataset Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATASET_NAME` | No | `Airline Red Teaming` | Name of the evaluation dataset |
| `DATASET_URL` | No | (see below) | LangSmith public dataset URL |

Default dataset URL: `https://smith.langchain.com/public/c232f4e0-0fc0-42b6-8f1f-b1fbd30cc339/d`

### Simulation Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAX_TURNS` | No | `10` | Maximum conversation turns |
| `INPUT_KEY` | No | `input` | Key for input in examples |
| `INSTRUCTIONS_KEY` | No | `instructions` | Key for red team instructions |

### Evaluation Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EVALUATION_MODE` | No | `local` | Execution mode: `local` or `remote` |
| `NUM_EXAMPLES` | No | None | Number of examples to run (None = all) |
| `SKIP_EXAMPLE` | No | `false` | Skip the demo simulation |

### Logging Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `LOG_FORMAT` | No | (see below) | Python logging format string |
| `ENVIRONMENT` | No | `development` | Environment name: development, staging, production |

Default log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Configuration Modes

### Local Mode

For local development and testing:

```env
EVALUATION_MODE=local
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=ls__...
```

### Remote Mode

For using deployed LangGraph instances:

```env
EVALUATION_MODE=remote
LANGGRAPH_DEPLOYMENT_URL=https://your-deployment.smith.langchain.com
LANGGRAPH_API_KEY=your-deployment-key
LANGSMITH_API_KEY=ls__...
```

## Using the Config Class

### Basic Usage

```python
from src.config import get_config

# Get singleton instance
config = get_config()

# Access configuration
print(config.assistant_model)
print(config.max_turns)

# Validate configuration
config.validate()
```

### Getting Model Configuration

```python
# Get model config for a component
assistant_config = config.get_model_config("assistant")
# Returns: {"model": "gpt-4o", "temperature": 0.7, "max_tokens": None}

# Get default model config
default_config = config.get_model_config()
```

### Configuration Dictionary

```python
# Get config as dictionary (excludes sensitive data)
config_dict = config.to_dict()
# API keys are automatically excluded
```

## Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use appropriate models** - GPT-4 for evaluation, GPT-3.5 for testing
3. **Set `LANGSMITH_PROJECT`** - Helps organize evaluations
4. **Use `ENVIRONMENT`** - Differentiate dev/staging/prod
5. **Configure logging** - Set appropriate log levels

## Validation

The Config class validates:
- Required API keys based on execution mode
- Numeric values are in valid ranges
- Execution mode is valid ("local" or "remote")

Run validation explicitly:
```python
config = get_config()
config.validate()  # Raises ValueError if invalid
```

## Example Configurations

### Development Setup
```env
# API Keys
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=ls__...

# Use faster models for development
DEFAULT_MODEL=gpt-3.5-turbo

# Debug logging
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Quick testing
NUM_EXAMPLES=5
```

### Production Evaluation
```env
# API Keys
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=production-evals

# Use best models
DEFAULT_MODEL=gpt-4o
EVALUATOR_MODEL=gpt-4o

# Production settings
LOG_LEVEL=INFO
ENVIRONMENT=production

# Full evaluation
NUM_EXAMPLES=
SKIP_EXAMPLE=true
```

### Remote Deployment Testing
```env
# Remote execution
EVALUATION_MODE=remote
LANGGRAPH_DEPLOYMENT_URL=https://airline-bot.smith.langchain.com
LANGGRAPH_API_KEY=deployment-key-123

# Evaluation tracking
LANGSMITH_API_KEY=ls__...
LANGSMITH_PROJECT=deployment-tests

# Test subset
NUM_EXAMPLES=10
```

## Troubleshooting

### Missing API Keys
```
ValueError: Configuration validation failed:
  - OPENAI_API_KEY is required for local execution
```
**Solution**: Set the required environment variable in `.env`

### Invalid Mode
```
ValueError: Invalid EVALUATION_MODE: production. Must be 'local' or 'remote'
```
**Solution**: Use either "local" or "remote" for EVALUATION_MODE

### Model Temperature Out of Range
```
ValueError: MODEL_TEMPERATURE must be between 0 and 2, got 3.5
```
**Solution**: Set MODEL_TEMPERATURE between 0 and 2

## Migration from Direct Environment Variables

The old approach read environment variables directly:
```python
# Old approach (deprecated)
model = os.getenv("ASSISTANT_MODEL", "gpt-3.5-turbo")
```

New approach uses Config class:
```python
# New approach (recommended)
config = get_config()
model = config.assistant_model
```

Benefits:
- Centralized defaults
- Validation
- Type safety
- Easier testing
- Single source of truth