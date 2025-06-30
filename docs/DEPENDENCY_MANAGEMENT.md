# Dependency Management Guide

This guide explains how dependencies are managed in the LangGraph Exercises project.

## Overview

The project uses a modern Python dependency management approach with:
- **pyproject.toml** as the single source of truth
- **pip-tools** for generating locked dependency files
- Separate production and development dependencies

## Key Files

### pyproject.toml
The primary configuration file that defines:
- Project metadata
- Python version requirements (>=3.12)
- Production dependencies with version constraints
- Development dependencies in optional-dependencies section

### requirements.in / requirements-dev.in
Input files for pip-tools that mirror pyproject.toml dependencies:
- `requirements.in` - Production dependencies only
- `requirements-dev.in` - Development tools with constraint to production versions

### requirements.txt
Auto-generated locked file with exact versions for reproducible builds.
**DO NOT EDIT MANUALLY** - Always regenerate from .in files.

### langgraph.json
LangGraph deployment configuration that references the same dependencies.
Should stay in sync with pyproject.toml.

## Installation

### For Users
```bash
# Install the package with all dependencies
pip install -e .
```

### For Developers
```bash
# Install with development tools
pip install -e ".[dev]"
```

### For Production
```bash
# Install from locked requirements
pip install -r requirements.txt
```

## Updating Dependencies

### Adding a New Dependency

1. Add to `pyproject.toml` with version constraint:
   ```toml
   dependencies = [
       "existing-package>=1.0.0,<2.0.0",
       "new-package>=0.1.0,<1.0.0",  # Add here
   ]
   ```

2. Update `requirements.in` to match:
   ```
   new-package>=0.1.0,<1.0.0
   ```

3. Regenerate locked files:
   ```bash
   pip-compile requirements.in
   pip-compile requirements-dev.in
   ```

### Updating Existing Dependencies

1. Update version constraint in `pyproject.toml` and `requirements.in`
2. Regenerate:
   ```bash
   pip-compile --upgrade-package package-name requirements.in
   ```

### Updating All Dependencies

```bash
# Update all to latest compatible versions
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
```

## Version Constraints

We use semantic versioning constraints:
- `>=0.2.0,<0.3.0` - Compatible releases (0.2.x)
- `>=1.0.0,<2.0.0` - Major version pinning
- `~=1.2.3` - Compatible version (~=1.2.3 means >=1.2.3, <1.3.0)

## Best Practices

1. **Always use version constraints** - Never use unpinned dependencies
2. **Keep pyproject.toml as source of truth** - Other files should mirror it
3. **Regenerate after changes** - Don't manually edit requirements.txt
4. **Test after updates** - Run full test suite after dependency changes
5. **Document breaking changes** - Note any API changes when updating

## Common Commands

```bash
# Install for development
pip install -e ".[dev]"

# Compile dependencies
pip-compile requirements.in
pip-compile requirements-dev.in

# Upgrade specific package
pip-compile --upgrade-package langchain requirements.in

# Show dependency tree
pip install pipdeptree
pipdeptree

# Check for security vulnerabilities
pip install safety
safety check
```

## Troubleshooting

### Dependency Conflicts
If you encounter conflicts:
1. Check version constraints aren't too restrictive
2. Use `pip-compile --resolver=backtracking` for complex cases
3. Consider upgrading all dependencies together

### Missing Dependencies
If imports fail:
1. Ensure you've run `pip install -e .`
2. Check the dependency is in pyproject.toml
3. Regenerate requirements files

### Version Mismatches
If deployment fails:
1. Verify Python version matches across all configs (3.12)
2. Ensure langgraph.json dependencies match pyproject.toml
3. Regenerate all locked files