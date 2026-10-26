from fastapi.testclient import TestClient

from coverage_intel.api.app import create_app


def test_health_endpoint_is_provider_independent() -> None:
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "coverage-intel"}
