"""Guard the platform-only scope of the llmaven CLI after the RAG sunset.

The REST API server, Streamlit UI and agentic RAG system moved to
uw-ssec/llmoxie-rag. These tests fail if any of those surfaces come back.
"""

from __future__ import annotations

import importlib.util

import pytest
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
