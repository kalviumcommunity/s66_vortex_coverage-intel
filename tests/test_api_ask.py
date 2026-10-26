from fastapi.testclient import TestClient

from coverage_intel.api.app import create_app


def test_ask_endpoint_returns_structured_insufficient_evidence() -> None:
    response = TestClient(create_app()).post("/ask", json={"question": "Is water damage covered?"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "insufficient_evidence"
    assert body["query_id"]
