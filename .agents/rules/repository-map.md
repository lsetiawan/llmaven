# Repository Map

**Load when:** you need to know what this repository is, where a file lives, or
how it is built and deployed.

## Repository Overview

**LLMaven** (being renamed **llmoxie**; the GitHub repository is
`uw-ssec/llmoxie`, while the package, CLI, and Pixi environment are still named
`llmaven`) is an open-source AI control plane from UW SSEC. It packages AI
infrastructure that can be installed on cloud and HPC systems:

- **Layer 1 — Inference engine:** provided by the cloud or HPC (Azure Foundry
  Models, AWS Bedrock, GCP Vertex AI, vLLM).
- **Layer 2 — API gateway (this repo's core):** LiteLLM for a single
  OpenAI-compatible endpoint with auth, budgets, and spend tracking; MLflow for
  tracking and agent evaluation; PostgreSQL and object storage behind them.
- **Layer 3 — RSE-Plugins:** Claude Code plugins, developed in
  [uw-ssec/rse-plugins](https://github.com/uw-ssec/rse-plugins), not here.

The `llmaven` Python package also carries a FastAPI service, a Streamlit UI, and
an agentic RAG system (see
[`agent_docs/agentic_rag.md`](../../agent_docs/agentic_rag.md)).

**Repository Stats:**

- **Type:** Python package (`src/` layout, hatchling) plus deployment code
- **Language:** Python 3.12 (`requires-python = ">=3.12"`)
- **CLI:** `llmaven` (Typer, `src/llmaven/cli.py`)
- **Infrastructure:** Pulumi Automation API targeting Azure
- **Package manager:** Pixi (see [pixi-environments.md](pixi-environments.md))

## Project Structure & Key Files

```
.
├── .agents/
│   ├── rules/                   # On-demand rules referenced by AGENTS.md
│   └── skills/                  # User-invocable skills (/commit, /verify, ...)
├── .claude/
│   └── skills -> ../.agents/skills  # Symlink so Claude Code discovers the skills
├── .cursorrules -> AGENTS.md    # Cursor reads the same entry point
├── .github/
│   ├── copilot-instructions.md -> ../AGENTS.md  # Copilot reads the same entry point
│   ├── pull_request_template.md # PR template (includes AI disclosure)
│   └── workflows/               # ci.yml (tests + pre-commit), container builds, zizmor
├── agent_docs/                  # Domain guides for agents (endpoints, infra, RAG, ...)
├── archive/                     # Legacy code — DO NOT MODIFY
├── docker/
│   ├── docker-compose.yml       # Local stack mirroring the cloud architecture
│   ├── config.yaml              # LiteLLM config for the local stack
│   ├── dockerfiles/             # litellm, mlflow, backup images
│   └── .env.example             # Copy to docker/.env (gitignored)
├── eval/                        # RAG evaluation and data-extraction experiments
├── knowledge/                   # OKF project memory, managed by the okf CLI
├── scripts/                     # Postgres backup/export helpers
├── src/llmaven/
│   ├── cli.py                   # Typer CLI: server, infra, backup-infra, agentic
│   ├── config.py                # Pydantic Settings for the web service
│   ├── main.py                  # FastAPI app
│   ├── v1/                      # REST API v1 endpoints
│   ├── core/                    # Legacy RAG: embeddings, retriever, generator
│   ├── agentic/                 # Agentic RAG: ingestion, search, agent, providers
│   ├── services/                # Business logic
│   ├── schemas/                 # Pydantic models (API contracts)
│   ├── frontend/                # Streamlit UI
│   ├── proxy/                   # Package stub (only __init__.py)
│   ├── data/                    # Request-log download and session grouping
│   ├── deployment/              # `llmaven infra init|validate|deploy` logic
│   ├── infrastructure/          # Pulumi resources for Azure
│   └── infrastructure_backup/   # Pulumi program for the backup stack
├── tests/                       # pytest suite (agentic/, v1/, data/, infrastructure/)
├── pixi.toml / pixi.lock        # Environments, tasks, and lock file (don't hand-edit the lock)
├── pyproject.toml               # Package metadata, extras (test, deploy, production)
├── AGENTS.md                    # Entry point for AI assistants
├── AI_POLICY.md                 # AI-assistance disclosure policy (Assisted-by trailer)
├── CLAUDE.md                    # Points Claude Code at AGENTS.md (@AGENTS.md)
└── CONTRIBUTING.md              # Human contributor guide
```

## Local Stack

`pixi run -e llmaven up` starts `docker/docker-compose.yml`: PostgreSQL (5432),
MinIO (9000/9001, plus a one-shot `createbuckets` init job), Qdrant (6333),
MLflow (8080), Azurite blob storage (10000) and LiteLLM (4000). It reads
`docker/.env`, created from `docker/.env.example`. `pixi run -e llmaven clean`
runs `docker-compose down -v` and **deletes the stack's data** — ask first.

## Deployment

- `llmaven infra init|validate|deploy|status|destroy` drives Pulumi against
  Azure. Configuration lives in `llmaven-config*.yaml`, which is gitignored and
  holds secrets. See
  [`agent_docs/infrastructure.md`](../../agent_docs/infrastructure.md).
- `.github/workflows/build-services.yml` builds the mlflow, litellm and backup
  images and pushes them to GHCR on pushes to `main` that touch `docker/**` or
  `scripts/backup_postgres.py`, and on releases.
- `deploy` and `destroy` change real cloud resources. Run `--preview` only,
  unless a human has explicitly approved the real run.
- Real environment configs (Azure dev/prod, UW HYAK) live in the private
  `uw-ssec/llmaven-deploy` repository, not here.

## CI

`.github/workflows/ci.yml` runs on pushes to `main` and `feature/**` and on PRs
to `main`, in the `llmaven` environment on Ubuntu:

- pytest in three steps: `tests/` minus `agentic/` and `v1/`, then
  `tests/agentic/` minus `test_cli.py`, then `tests/v1/`. The first step ends
  with `|| echo`, so **core test failures do not fail CI**, and
  `tests/agentic/test_cli.py` never runs there. A green CI run is therefore not
  a full-suite pass — run `pixi run -e llmaven test` and report it.
- `pre-commit run --all-files`.
