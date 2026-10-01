"""Deterministic statutory engine: net-new headcount + benefit math.

Rule packs are loaded from rules/*.json. The engine records every step to a
TrailRecorder. There is no LLM anywhere in this path.
"""

from __future__ import annotations

import json
from pathlib import Path

from .data import SITES, Site
from .models import CreditResult
from .trail import TrailRecorder

RULES_DIR = Path(__file__).resolve().parent / "rules"


def load_pack(jurisdiction: str) -> dict | None:
    path = RULES_DIR / f"{jurisdiction}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def available_packs() -> list[str]:
    return sorted(p.stem for p in RULES_DIR.glob("*.json"))


def compute_credit(
    site: Site,
    pack: dict | None,
    trail: TrailRecorder | None = None,
) -> CreditResult:
    trail = trail or TrailRecorder()
    prior = site.prior_avg
    current = site.current_avg
    net_new = current - prior
    trail.record(
        "net_new",
        {"current_avg": current, "prior_avg": prior},
        "net_new = current_avg - prior_avg",
        {"net_new": net_new},
        "headcount reconciliation",
    )

    if pack is None:
        return CreditResult(
            jurisdiction=site.jurisdiction,
            program="(no state pack)",
            prior_avg=prior,
            current_avg=current,
            net_new=net_new,
            qualifying_jobs=0.0,
            annual_credit=0.0,
            lifetime_credit=0.0,
            citation="",
            has_pack=False,
            trail=tuple(trail.steps),
        )

    threshold = pack["threshold_new_jobs"]
    per_job = pack["benefit"]["amount"]
    years = pack["period_years"]

    qualifies = net_new >= threshold
    qualifying = net_new if qualifies else 0.0
    trail.record(
        "threshold",
        {"net_new": net_new, "threshold": threshold},
        "qualifies = net_new >= threshold",
        {"qualifies": qualifies},
        pack["citation"],
    )

    annual = qualifying * per_job
    trail.record(
        "annual_credit",
        {"qualifying_jobs": qualifying, "amount_per_job": per_job},
        "annual = qualifying_jobs * amount_per_job",
        {"annual": annual},
        pack["citation"],
    )

    lifetime = annual * years
    trail.record(
        "lifetime_credit",
        {"annual": annual, "period_years": years},
        "lifetime = annual * period_years",
        {"lifetime": lifetime},
        pack["citation"],
    )

    return CreditResult(
        jurisdiction=site.jurisdiction,
        program=pack["name"],
        prior_avg=prior,
        current_avg=current,
        net_new=net_new,
        qualifying_jobs=qualifying,
        annual_credit=annual,
        lifetime_credit=lifetime,
        citation=pack["citation"],
        has_pack=True,
        trail=tuple(trail.steps),
    )


def portfolio() -> list[CreditResult]:
    results = []
    for code, site in SITES.items():
        results.append(compute_credit(site, load_pack(code)))
    return results


def simulate(jurisdiction: str, delta: float) -> CreditResult:
    """Re-run the engine for a jurisdiction with a headcount delta."""
    site = SITES[jurisdiction]
    adjusted = Site(jurisdiction, site.prior_avg, site.current_avg + delta)
    return compute_credit(adjusted, load_pack(jurisdiction))
