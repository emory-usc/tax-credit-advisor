# Tax Credit Engine

[![CI](https://github.com/emory-usc/tax-credit-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/emory-usc/tax-credit-engine/actions/workflows/ci.yml)

A deterministic job-creation tax-credit engine with a FastAPI delivery
surface, built around one architectural rule:

**the tools compute; the agents narrate.**

The engine (pure Python) computes net-new headcount and the resulting credit
from JSON rule packs. The narration roles only produce templated text over
numbers they were handed — they can never invent a figure, because they never
compute one. Every number on the output traces back to a recorded `{step,
inputs, formula, output, citation}` trail row, and the whole trail is
fingerprinted with SHA-256.

> **Illustrative data only.** The rule packs, thresholds, and per-job amounts
> are illustrative placeholders. They are **not** real statute values and
> nothing here is legal or tax advice. A real deployment would load
> practitioner-signed rule packs; this repo demonstrates the *machinery*, not
> the law.

## The model

| Layer | Role |
|---|---|
| `rules/*.json` | One JSON rule pack per jurisdiction. Adding a jurisdiction is a JSON file plus one registry line. |
| `engine.py` | Statutory net-new headcount + benefit math. Pure, deterministic. |
| `trail.py` | Records every step and a SHA-256 fingerprint over the trail. |
| `agents.py` | Narration roles (headcount / credit / discovery / reporting). Advisory only. |

## Quick start

```bash
pip install -e ".[web]"
tax-credit portfolio            # CLI: full jurisdiction book
tax-credit audit GA             # CLI: trail + fingerprint for one jurisdiction
uvicorn tax_credit_advisor.server:app --port 8000   # the API
```

### API

```
GET  /health                   liveness (unauthenticated, for probes)
GET  /ready                    readiness (book + rule packs loaded)
POST /portfolio                every jurisdiction's statutory result
POST /discover                 qualifying jurisdictions the client may not track
POST /simulate                 re-run the engine with a headcount delta
     headers: X-API-Key: <key>   (constant-time compare; dev default: dev-key)
```

```bash
curl -X POST http://localhost:8000/simulate \
  -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
  -d '{"jurisdiction": "GA", "delta": 10}'
```

## Wrapping as a LangChain tool

The engine is a pure function with an audit trail, so exposing it to an agent
is one decorator — and the trail survives the round trip:

```python
from langchain_core.tools import tool
from tax_credit_advisor import engine
from tax_credit_advisor.data import SITES

@tool
def simulate_hiring(jurisdiction: str, delta: float) -> str:
    """Re-run the statutory credit engine for a jurisdiction with a headcount delta. Advisory only."""
    r = engine.simulate(jurisdiction, delta)
    return f"{r.jurisdiction}: ${r.lifetime_credit:,.0f} lifetime"
```

The agent can narrate the result, but the number it narrates was computed in
Python and recorded in the trail — the pattern this repo exists to demonstrate.

## Deployment

- `Dockerfile` — multi-stage uv build, slim non-root runtime, healthcheck.
- `infra/main.bicep` — Container Apps with scale-to-zero, Log Analytics +
  App Insights, `/health` liveness probe, API key injected as a secure
  parameter. Compiles clean (`az bicep build`).
- `.github/workflows/deploy.yml` — GHCR build/push, Trivy scan (blocking on
  CRITICAL/HIGH), OIDC Bicep deploy on version tags.

## Security posture

See `SECURITY.md`. The short version: deterministic math, SHA-256 audit trail,
illustrative rule data, API-key gate, input bounds-checking, synthetic data.
