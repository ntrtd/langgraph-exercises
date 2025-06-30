# Project Notes for Claude Code

## Linting and Type Checking Commands

To ensure code quality, run the following commands after making changes:

### Linting with Ruff
```bash
.venv/bin/ruff check src/
```

To automatically fix formatting issues:
```bash
.venv/bin/ruff check src/ --fix
```

### Type Checking with MyPy
```bash
.venv/bin/mypy src/
```

Note: The project uses strict mypy settings which may report many type errors. Focus on fixing the most critical ones related to your changes.

### Code Formatting with Black
```bash
.venv/bin/black src/
```
