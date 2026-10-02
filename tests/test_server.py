"""Tests for the Tax Credit Engine FastAPI surface."""

from fastapi.testclient import TestClient

from tax_credit_advisor.server import app

client = TestClient(app)


def test_health_is_unauthenticated():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_reports_engine_state():
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["jurisdictions"] == 6
    assert body["rule_packs"] == 5


def test_portfolio_with_valid_key():
    r = client.post("/portfolio", headers={"X-API-Key": "dev-key"})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 6
    ga = next(x for x in results if x["jurisdiction"] == "GA")
    assert ga["lifetime_credit"] == 300000.0


def test_discover_returns_qualifying_hits():
    r = client.post("/discover", headers={"X-API-Key": "dev-key"})
    assert r.status_code == 200
    hits = r.json()["hits"]
    assert {h["jurisdiction"] for h in hits} == {"GA", "NC"}


def test_simulate_delta():
    r = client.post(
        "/simulate",
        json={"jurisdiction": "GA", "delta": 10.0},
        headers={"X-API-Key": "dev-key"},
    )
    assert r.status_code == 200
    assert r.json()["result"]["lifetime_credit"] == 450000.0


def test_simulate_unknown_jurisdiction_is_404():
    r = client.post(
        "/simulate",
        json={"jurisdiction": "ZZ", "delta": 1.0},
        headers={"X-API-Key": "dev-key"},
    )
    assert r.status_code == 404


def test_simulate_rejects_out_of_range_delta():
    r = client.post(
        "/simulate",
        json={"jurisdiction": "GA", "delta": 5000.0},
        headers={"X-API-Key": "dev-key"},
    )
    assert r.status_code == 422


def test_protected_endpoints_require_key():
    assert client.post("/portfolio").status_code == 401
    assert client.post("/discover").status_code == 401
    assert client.post("/simulate", json={"jurisdiction": "GA", "delta": 1.0}).status_code == 401
