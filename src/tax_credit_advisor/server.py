"""FastAPI delivery surface for the tax-credit engine.

The engine (net-new headcount + benefit math) is deterministic and side-effect
free; this module exposes it over HTTP behind an API-key gate. Every response
is advisory — see SECURITY.md.
"""

from __future__ import annotations

import os
import secrets

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from tax_credit_advisor import __version__, agents, engine
from tax_credit_advisor.data import SITES

_API_KEY = os.environ.get("TAX_CREDIT_API_KEY", "dev-key")

app = FastAPI(
    title="tax-credit-engine",
    version=__version__,
    description=(
        "Deterministic job-creation tax-credit analysis. Illustrative data and "
        "advisory output only — a licensed tax practitioner makes the filing decision."
    ),
)


class SimulateRequest(BaseModel):
    jurisdiction: str
    delta: float


class CreditResultModel(BaseModel):
    jurisdiction: str
    program: str
    prior_avg: float
    current_avg: float
    net_new: float
    qualifying_jobs: float
    annual_credit: float
    lifetime_credit: float
    citation: str
    has_pack: bool


def _result_model(r: engine.CreditResult) -> CreditResultModel:
    return CreditResultModel(
        jurisdiction=r.jurisdiction,
        program=r.program,
        prior_avg=r.prior_avg,
        current_avg=r.current_avg,
        net_new=r.net_new,
        qualifying_jobs=r.qualifying_jobs,
        annual_credit=r.annual_credit,
        lifetime_credit=r.lifetime_credit,
        citation=r.citation,
        has_pack=r.has_pack,
    )


def _authorized(x_api_key: str | None) -> bool:
    return x_api_key is not None and secrets.compare_digest(x_api_key, _API_KEY)


def _require_key(x_api_key: str | None) -> None:
    if not _authorized(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid API key",
        )


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Liveness probe. No auth by design — load balancers need it unauthenticated."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness probe. Confirms the headcount book and rule packs are loaded."""
    return {
        "status": "ready",
        "jurisdictions": len(SITES),
        "rule_packs": len(engine.available_packs()),
    }


@app.post("/portfolio")
def portfolio(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> dict:
    """Full portfolio: every jurisdiction's statutory net-new result."""
    _require_key(x_api_key)
    results = engine.portfolio()
    return {
        "results": [_result_model(r) for r in results],
        "narration": agents.report_narration(results),
    }


@app.post("/discover")
def discover(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> dict:
    """Discovery: qualifying jurisdictions the client may not be tracking."""
    _require_key(x_api_key)
    results = engine.portfolio()
    hits = [r for r in results if r.has_pack and r.qualifying_jobs > 0]
    return {
        "hits": [_result_model(r) for r in hits],
        "narration": agents.discovery_narration(results),
    }


@app.post("/simulate")
def simulate(
    req: SimulateRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict:
    """Re-run the engine for a jurisdiction with a headcount delta."""
    _require_key(x_api_key)
    if req.jurisdiction not in SITES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"unknown jurisdiction: {req.jurisdiction}",
        )
    if not -1000 <= req.delta <= 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="delta must be between -1000 and 1000",
        )
    r = engine.simulate(req.jurisdiction, req.delta)
    return {
        "result": _result_model(r),
        "narration": agents.credit_narration(r),
    }
