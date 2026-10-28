# API Endpoints

**Load when:** adding or changing a REST endpoint under `src/llmaven/v1/`.

## Layers

Each endpoint is split across four layers. Add them in this order:

1. **Schema** (`src/llmaven/schemas/`): Pydantic request and response models
2. **Service** (`src/llmaven/services/`): the business logic, with no FastAPI
   imports
3. **Endpoint** (`src/llmaven/v1/endpoints/`): a thin route handler that calls
   the service
4. **Router** (`src/llmaven/v1/router.py`): registers the endpoint under `/v1`

Then add tests. Model the new endpoint on `v1/endpoints/generate.py` and
`v1/endpoints/retrieve.py`.

## Schema

```python
# src/llmaven/schemas/new_feature.py
from pydantic import BaseModel


class NewFeatureRequest(BaseModel):
    param: str
```

## Service

```python
# src/llmaven/services/new_feature_service.py
def process_feature(param: str) -> dict:
    # Business logic here
    return {"result": "...", "status_code": 200}
```

## Endpoint

Each endpoint module owns its path through the `APIRouter` prefix and registers
its handler on `""`. It uses relative imports:

```python
# src/llmaven/v1/endpoints/new_feature.py
from fastapi import APIRouter, HTTPException

from ...schemas.new_feature import NewFeatureRequest
from ...services.new_feature_service import process_feature

router = APIRouter(prefix="/new-feature", tags=["new-feature"])


@router.post("")
async def new_feature(request: NewFeatureRequest):
    try:
        return process_feature(request.param)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Router

`src/llmaven/v1/router.py` holds `APIRouter(prefix="/v1")` and includes each
endpoint router:

```python
from .endpoints import new_feature

router.include_router(new_feature.router)
```

The route is then `POST /v1/new-feature`, with no trailing slash.

## Tests

Call the route through `TestClient`, and mock whatever the service loads
(models, retrievers, network clients). Unit tests must not download models or
reach external services:

```python
# tests/v1/test_new_feature.py
from unittest.mock import patch

from fastapi.testclient import TestClient

from llmaven.main import app

client = TestClient(app)


def test_new_feature_success():
    with patch(
        "llmaven.v1.endpoints.new_feature.process_feature",
        return_value={"result": "ok", "status_code": 200},
    ):
        response = client.post("/v1/new-feature", json={"param": "test"})
    assert response.status_code == 200
    assert response.json()["result"] == "ok"
```

## Verification

```bash
pixi run -e llmaven pytest tests/v1/test_new_feature.py -v
pixi run -e llmaven verify

# Manual check: start the API, then open http://localhost:8000/docs
pixi run -e llmaven api-server --env development --reload
```
