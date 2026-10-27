from fastapi.testclient import TestClient

from coverage_intel.api.app import create_app


def test_core_api_flow_exposes_health_and_safe_ask_response() -> None:
    client = TestClient(create_app())
    health = client.get("/health")
    answer = client.post("/ask", json={"question": "What applies?"})

    assert health.status_code == 200
    assert answer.status_code == 200
    assert answer.json()["status"] == "insufficient_evidence"
    assert answer.headers["X-Request-ID"]


def test_ui_endpoint_serves_html() -> None:
    client = TestClient(create_app())
    response = client.get("/ui/", follow_redirects=True)
    assert response.status_code == 200
    assert "Coverage Intel" in response.text
