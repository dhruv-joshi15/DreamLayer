import sys
import os
import json
import pytest

# Ensure root path is added to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from txt2img_server import app


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_txt2img_valid_payload(client):
    payload = {
        "prompt": "A futuristic city in the clouds",
        "negative_prompt": "",
        "model": "realisticVisionV60B1_v51HyperVAE.safetensors",  # ✅ Real model from your ComfyUI
        "width": 512,
        "height": 512,
        "steps": 30,
        "cfg_scale": 7.5,
        "batch_size": 1,
        "seed": 42,
        "controlnet": {
            "enabled": False,
            "units": []
        }
    }

    response = client.post(
        "/api/txt2img",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "generated_images" in data


def test_txt2img_missing_required_field(client):
    payload = {
        # Missing prompt
        "model": "realisticVisionV60B1_v51HyperVAE.safetensors",
        "width": 512,
        "height": 512,
        "steps": 20,
        "cfg_scale": 7.5,
        "batch_size": 1
    }

    response = client.post(
        "/api/txt2img",
        data=json.dumps(payload),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "Validation failed" in data["message"]
    assert any("prompt" in err["loc"] for err in data["details"])
