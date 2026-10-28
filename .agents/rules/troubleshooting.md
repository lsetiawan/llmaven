# Troubleshooting

**Load when:** a documented command fails or behaves unexpectedly.

## Issue: "pre-commit not found" or command fails

**Solution:** Run `pixi install -e llmaven` first, and pass `-e llmaven` to
`pixi run`. pre-commit is only in the `llmaven` environment.

## Issue: Pre-commit check fails after making fixes

**Behavior:** Pre-commit hooks like `trailing-whitespace` auto-fix files. When
this happens:

- The hook shows "Failed" with "files were modified by this hook"
- You must re-stage the fixed files: `git add <files>`
- Re-run `pixi run -e llmaven pre-commit` to verify

**This is expected behavior, not an error.**

## Issue: Modifying pixi.toml breaks the environment

**Solution:**

```bash
# Validate syntax, reinstall environment
pixi install -e llmaven

# If still broken, ask the user before removing .pixi and reinstalling
```

## Issue: Platform not supported

`pixi.toml` supports `linux-64` and `osx-arm64` only. Adding a platform forces a
full re-solve of every environment, including the CUDA wheel pinned under
`[target.linux-64.pypi-dependencies]`; raise it with a maintainer rather than
adding it in an unrelated PR.

## Issue: `pixi.lock` changed format or CI cannot read it

**Cause:** a Pixi newer than CI's `v0.63.2` re-solved the lock and wrote a newer
lock-file `version:`. **Solution:** discard the lock change and re-lock with
Pixi 0.63.2.

## Issue: `okf validate` fails in `pixi run -e llmaven verify`

**Solution:** Follow the "Repo-specific traps" in the `okf-memory` skill — the
usual causes are an orphaned concept (no `relate` link), a `description:` that
prettier or a hand edit folded across lines, or a `code_refs` path that is not
tracked. Never fix it by deleting the concept without telling the user.

## Issue: tests fail with Docker or testcontainers errors

**Solution:** The suite starts Qdrant through testcontainers, so Docker must be
running. Check with `docker info`. If Docker is unavailable, say the test step
was skipped and why rather than reporting `verify` as passed.

## Issue: `docker compose` fails on missing variables

**Solution:** `docker/docker-compose.yml` reads `docker/.env`, which is
gitignored. Create it from `docker/.env.example`;
`docker compose -f docker/docker-compose.yml config` shows the resolved file and
any unset variables.

## Issue: Qdrant reports `Collection not found`

**Cause:** a wrong collection name or Qdrant location, or a collection that was
never created. The agentic system defaults to `agentic-rag` at
`http://localhost:6333` (`AGENTIC_COLLECTION_NAME`, `AGENTIC_QDRANT_URL`).

**Diagnosis:** list the collections that actually exist:

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")  # or path="..." for local storage
print([c.name for c in client.get_collections().collections])
```

Then fix the name or location, or ingest first
(`pixi run -e llmaven llmaven agentic ingest <dir>`).

## Issue: `CUDA out of memory` loading a model

**Solution:** load the legacy generator with quantization,
`LanguageModel.load_language_model(quantization="4bit")` (or `"8bit"`). Failing
that, use a smaller model or run on CPU. The generation service loads models
with `"8bit"`.

## Issue: API server won't start

**Diagnosis:** start it in development mode and read the traceback:

```bash
pixi run -e llmaven api-server --env development --reload
```

Check for port 8000 already in use (`lsof -i :8000`), missing environment
variables, and import errors.

## Issue: Packages missing or at the wrong version

**Solution:** reinstall the environment and check that the package imports:

```bash
pixi install -e llmaven
pixi run -e llmaven llmaven version
```

If that doesn't fix it, ask the user before running `pixi clean`, which deletes
`.pixi/`.
