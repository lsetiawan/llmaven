from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from llmaven.main import app
from llmaven.services import generation_service

client = TestClient(app)


# Define test cases
@pytest.mark.parametrize(
    "prompt,generation_model,expected_status",
    [
        ("What is the capital of France?", "allenai/OLMo-2-1124-7B-Instruct", 200),
        (
            "Explain quantum computing in simple terms.",
            "allenai/OLMo-2-1124-7B-Instruct",
            200,
        ),
    ],
)
def test_generate_endpoint(prompt, generation_model, expected_status):
    """
    Test the text generation API endpoint.
    """
    payload = {"prompt": prompt, "generation_model": generation_model}

    # Mock the model so the test doesn't download and load a 7B checkpoint.
    with (
        patch.object(generation_service, "LanguageModel") as mock_model_cls,
        patch.dict(generation_service.MODEL_INSTANCES, clear=True),
    ):
        mock_model_cls.return_value.inference.return_value = f"Answer to: {prompt}"
        response = client.post("/v1/generate", json=payload)

    mock_model_cls.assert_called_once_with(model_name=generation_model)

    assert response.status_code == expected_status
    assert "answer" in response.json()
    assert isinstance(response.json()["answer"], str)
    assert len(response.json()["answer"]) > 0  # Ensure the model generates text

    print(f"✅ Test passed for prompt: {prompt}")


if __name__ == "__main__":
    pytest.main()
