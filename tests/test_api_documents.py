from fastapi.testclient import TestClient

from coverage_intel.api.app import create_app


def test_document_registration_returns_accepted_id() -> None:
    response = TestClient(create_app()).post(
        "/documents",
        json={"category": "policy", "document_id": "policy-1"},
    )
    assert response.status_code == 202
    assert response.json()["document_id"] == "policy-1"
