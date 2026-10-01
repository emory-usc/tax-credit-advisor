"""CI smoke test for the tax-credit-advisor API surface."""

from fastapi.testclient import TestClient

from tax_credit_advisor.server import app

c = TestClient(app)
assert c.get("/health").status_code == 200
assert c.get("/ready").status_code == 200
r = c.post("/portfolio", headers={"X-API-Key": "dev-key"})
assert r.status_code == 200
ga = next(x for x in r.json()["results"] if x["jurisdiction"] == "GA")
assert ga["lifetime_credit"] == 300000.0
print("API smoke OK")
