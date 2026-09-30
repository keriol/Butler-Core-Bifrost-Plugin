# Contributing

Bifröst is developed Git-first.

## Workflow

1. Start from a GitHub Issue.
2. Create a focused branch.
3. Keep one focused feature per commit.
4. Run the complete test suite.
5. Open a pull request against `main`.
6. Merge only with green CI and appropriate evidence.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall -q src tests
python -m pytest
python -m build
```

Public contributions must not include credentials, private endpoints,
household-specific identifiers or deployment-specific implementation details.
