"""HTTP-layer tests for the /api/parts endpoints, using the real dataset."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_facets_returns_distinct_filter_values():
    response = client.get("/api/parts/facets")
    assert response.status_code == 200
    body = response.json()
    assert body["applications"]
    assert body["fuse_types"]
    assert body["applications"] == sorted(body["applications"])


def test_browse_parts_returns_results():
    response = client.get("/api/parts", params={"limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    assert set(body[0].keys()) == {"ID", "DESCRIPTION", "Application", "Attribut1"}


def test_browse_parts_filters_by_application():
    response = client.get("/api/parts", params={"application": "Automotive", "limit": 50})
    assert response.status_code == 200
    body = response.json()
    assert body  # the synthetic dataset always has some Automotive parts
    assert all(part["Application"] == "Automotive" for part in body)


def test_get_part_returns_full_detail():
    part_id = client.get("/api/parts", params={"limit": 1}).json()[0]["ID"]
    response = client.get(f"/api/parts/{part_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["ID"] == part_id
    assert "Rated Current (A)" in body


def test_get_part_missing_returns_404():
    response = client.get("/api/parts/DOES-NOT-EXIST")
    assert response.status_code == 404


def test_alternatives_endpoint_respects_tier_progression():
    part_id = client.get("/api/parts", params={"limit": 1}).json()[0]["ID"]
    tier1 = client.get(f"/api/parts/{part_id}/alternatives", params={"tier": "Tier 1"}).json()
    tier5 = client.get(f"/api/parts/{part_id}/alternatives", params={"tier": "Tier 5"}).json()
    assert len(tier5) >= len(tier1)


def test_alternatives_endpoint_rejects_invalid_tier():
    part_id = client.get("/api/parts", params={"limit": 1}).json()[0]["ID"]
    response = client.get(f"/api/parts/{part_id}/alternatives", params={"tier": "Tier 99"})
    assert response.status_code == 422


def test_explain_rule_based_default():
    part_id = client.get("/api/parts", params={"limit": 1}).json()[0]["ID"]
    response = client.post(f"/api/parts/{part_id}/explain", json={"use_ai": False})
    assert response.status_code == 200
    assert len(response.json()["explanation"]) > 0


def test_explain_ai_mode_returns_503_without_model_installed():
    """Phi-1.5 weights aren't installed in the test environment -- confirms the
    graceful-degradation path (503, not a raw 500 traceback)."""
    part_id = client.get("/api/parts", params={"limit": 1}).json()[0]["ID"]
    response = client.post(f"/api/parts/{part_id}/explain", json={"use_ai": True})
    assert response.status_code == 503
