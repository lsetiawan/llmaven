"""Guard the platform-only scope of the llmaven CLI after the RAG sunset.

The REST API server, Streamlit UI and agentic RAG system moved to
uw-ssec/llmoxie-rag. These tests fail if any of those surfaces come back.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys

import pytest
import typer
from typer.testing import CliRunner

from llmaven.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """Return a Typer CLI runner."""
    return CliRunner()


@pytest.mark.parametrize("argv", [["server", "serve"], ["server", "ui"]])
def test_server_commands_removed(runner: CliRunner, argv: list[str]) -> None:
    result = runner.invoke(app, argv)
    assert result.exit_code == 2
    assert "No such command" in result.output


@pytest.mark.parametrize(
    "module",
    [
        "llmaven.main",
        "llmaven.config",
        "llmaven.v1",
        "llmaven.services",
        "llmaven.schemas",
        "llmaven.core",
        "llmaven.frontend",
    ],
)
def test_api_modules_removed(module: str) -> None:
    assert importlib.util.find_spec(module) is None


@pytest.mark.parametrize("cmd", ["ingest", "search", "chat"])
def test_agentic_commands_removed(runner: CliRunner, cmd: str) -> None:
    result = runner.invoke(app, ["agentic", cmd])
    assert result.exit_code == 2
    assert "No such command" in result.output


def test_agentic_package_removed() -> None:
    assert importlib.util.find_spec("llmaven.agentic") is None


def test_cli_exposes_only_platform_commands() -> None:
    assert set(typer.main.get_command(app).commands) == {
        "infra",
        "backup-infra",
        "version",
    }


def test_cli_import_does_not_load_rag_modules() -> None:
    banned = {
        "qdrant_client",
        "fastembed",
        "docling",
        "pydantic_ai",
        "langchain",
        "fastapi",
        "streamlit",
        "transformers",
        "torch",
    }
    code = (
        "import sys, llmaven.cli; "
        f"print(sorted({{m.split('.')[0] for m in sys.modules}} & {banned!r}))"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert out.stdout.strip() == "[]"
