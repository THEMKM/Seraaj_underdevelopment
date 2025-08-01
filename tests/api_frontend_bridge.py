import requests

BASE_URL = 'http://localhost:8000'

# Simple check that API health endpoint is reachable under /v1 prefix

def test_health_endpoint():
    resp = requests.get(f"{BASE_URL}/v1/system/health", timeout=5)
    assert resp.status_code == 200
