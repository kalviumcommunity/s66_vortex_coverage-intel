from fastapi.testclient import TestClient

from coverage_intel.api.app import create_app


def test_request_id_is_preserved_or_generated() -> None:
    client = TestClient(create_app())
    supplied = client.get("/health", headers={"X-Request-ID": "request-1"})
    generated = client.get("/health")
    assert supplied.headers["X-Request-ID"] == "request-1"
    assert generated.headers["X-Request-ID"]
