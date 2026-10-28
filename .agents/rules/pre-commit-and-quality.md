# Pre-commit & Quality Standards

**Load when:** you are about to commit, open a PR, or claim that checks pass.

## Pre-commit Checks (MANDATORY BEFORE PRs)

**Always run pre-commit checks before creating a pull request.** The PR template
requires this, and PRs will fail if checks don't pass.

```bash
# Install pre-commit hooks (run once per clone)
pixi run -e llmaven pre-commit-install
# ✓ Installs .git/hooks/pre-commit
# ✓ Hooks will automatically run on every commit

# Run pre-commit on staged files only
pixi run -e llmaven pre-commit
# ✓ Fast, only checks staged changes
# ✓ Will auto-fix many issues (trailing whitespace, end-of-file, formatting)
# ⚠️ If fixes are made, files are modified; you must re-stage them

# Run pre-commit on ALL files (required before PR submission)
pixi run -e llmaven pre-commit-all
# ✓ Takes 1-3 minutes on first run (installs hook environments)
# ✓ Subsequent runs are fast (environments are cached)
# ✓ Auto-fixes issues where possible
```

To check a specific file, pass it through the task:
`pixi run -e llmaven pre-commit --files <path>`.

**Pre-commit Hooks Configured** (`.pre-commit-config.yaml`):

- check-added-large-files, check-case-conflict, check-merge-conflict
- check-yaml, check-symlinks, debug-statements
- end-of-file-fixer, trailing-whitespace, mixed-line-ending
- prettier (formats YAML, Markdown, HTML, CSS, JavaScript, JSON)
- ruff-check (with `--fix`) and ruff-format for Python
- codespell (spell checking)
- Disallow improper capitalization (the misspelled form of GitHub)
- Validate Dependabot config and GitHub workflows

**Files Excluded from Pre-commit:** `*.csv` everywhere; codespell also skips
notebooks, `pixi.lock`, and `tests/data/fixtures/*.jsonl`. Prettier skips
`knowledge/` — it folds OKF frontmatter into YAML that `okf` reads as empty.

## Making Changes: Validated Workflow

1. **Setup (first time):**

   ```bash
   pixi install -e llmaven
   pixi run -e llmaven pre-commit-install
   ```

2. **Make your changes** to files — surgically, per
   [working-agreement.md](working-agreement.md).

3. **Test changes:**

   ```bash
   # Stage your changes
   git add <files>

   # Run pre-commit checks
   pixi run -e llmaven pre-commit

   # If checks fail and auto-fix issues, re-add the fixed files
   git add <files>
   ```

4. **Before creating a PR:**

   ```bash
   # Run all hooks, validate the OKF bundle, then run the full test suite
   pixi run -e llmaven verify

   # Verify all checks pass (hooks show "Passed" or "Skipped", okf validate
   # reports 0 errors, 0 warnings, and pytest reports no failures)
   ```

5. **Create PR:** work through the checklist in
   [contribution-discipline.md](contribution-discipline.md) before submitting.
   - The PR template asks you to confirm the tests and `pre-commit` passed
   - Follow Conventional Commits for PR titles
   - Link related issues using "Resolves #<issue-number>"

## Tests

`pixi run -e llmaven test` runs `pytest tests/`, the **full** suite. It needs
Docker running, because Qdrant-backed tests use testcontainers. CI is not a
substitute (see [repository-map.md](repository-map.md#ci)): it skips
`tests/agentic/test_cli.py`. Report the local run's summary line, and name any
test you skipped or deselected and why.

## Commit Messages

Commits and PR titles follow
[Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<scope>): <subject>`, with the subject in the imperative mood.

| Type       | Use for                       |
| ---------- | ----------------------------- |
| `feat`     | New feature                   |
| `fix`      | Bug fix                       |
| `docs`     | Documentation only            |
| `style`    | Formatting, no code change    |
| `refactor` | Code restructuring            |
| `test`     | Adding or updating tests      |
| `perf`     | Performance improvements      |
| `chore`    | Maintenance tasks             |
| `ci`       | CI workflows                  |
| `build`    | Build system and dependencies |

| Scope       | Area                                          |
| ----------- | --------------------------------------------- |
| `api`       | REST API endpoints                            |
| `ui`        | Streamlit frontend                            |
| `infra`     | Pulumi infrastructure                         |
| `core`      | Legacy ML/AI components (`src/llmaven/core/`) |
| `cli`       | Command-line interface                        |
| `agentic`   | Agentic RAG system                            |
| `docker`    | Local stack and service images                |
| `data`      | Request-log tooling (`src/llmaven/data/`)     |
| `knowledge` | OKF project memory                            |
| `docs`      | Documentation                                 |
| `ci`        | CI workflows                                  |
| `deps`      | Dependency updates                            |
| `agents`    | Agent harness (`AGENTS.md`, `.agents/`)       |

The scope is optional; leave it out when no single area fits. Examples:

```text
feat(api): add summarization endpoint
fix(core): handle empty document retrieval
refactor(agentic): simplify ingestion pipeline
test(api): add retrieval endpoint tests
docs: update API documentation
```

The `commit` skill has the full procedure, including the `Assisted-by:` trailer.

## Documentation Standards

- Follow Conventional Commits for commit messages and PR titles
- Use Markdown with proper formatting (enforced by prettier)
- Spell check enabled (codespell)
- No trailing whitespace
- Files must end with newline
- Consistent line endings
