from fastapi.testclient import TestClient


def test_basic_health(client: TestClient) -> None:
    response = client.get("/v1/system/health")
    assert response.status_code == 200
    assert "overall_status" in response.json()


def test_readiness_probe(client: TestClient) -> None:
    response = client.get("/v1/system/health/readiness")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ready"


def test_liveness_probe(client: TestClient) -> None:
    response = client.get("/v1/system/health/liveness")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "alive"
