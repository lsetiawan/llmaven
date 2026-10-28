# Code Conventions

**Load when:** naming a new module, class, function or constant, or answering a
style question.

## Naming

| Kind              | Convention         | Example                                  |
| ----------------- | ------------------ | ---------------------------------------- |
| Python modules    | `snake_case.py`    | `qdrant_manager.py`                      |
| Classes           | `PascalCase`       | `LanguageModel`, `QdrantManager`         |
| Functions/methods | `snake_case`       | `retrieve_docs()`, `perform_retrieval()` |
| Constants         | `UPPER_SNAKE_CASE` | `MODEL_INSTANCES`                        |
| Config files      | `kebab-case.yaml`  | `llmaven-config.yaml`                    |

## Style

Ruff lints and formats Python through pre-commit (`ruff-check --fix` and
`ruff-format`), with its default settings. `pyproject.toml` only sets excludes.
The `.flake8` file in the repo root isn't used by any hook or CI job. Don't
follow its 120-character limit; `ruff-format` wraps at 88. Run
`pixi run -e llmaven pre-commit-all`; see
[pre-commit-and-quality.md](pre-commit-and-quality.md).

## Follow Existing Patterns

When unsure, copy the nearest existing code:

- `src/llmaven/services/`: service layer
- `src/llmaven/v1/endpoints/`: route handlers (see
  [api-endpoints.md](api-endpoints.md))
- `src/llmaven/agentic/`: agentic RAG components (see
  [agentic-rag.md](agentic-rag.md))
