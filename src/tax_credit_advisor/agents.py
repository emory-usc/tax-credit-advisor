"""Narration roles. Each produces templated text over a computed CreditResult.

These are advisory narrations — they never compute a number, only restate the
figure the engine already produced.
"""

from __future__ import annotations

from .models import CreditResult


def headcount_narration(r: CreditResult) -> str:
    direction = "grew" if r.net_new > 0 else ("shrank" if r.net_new < 0 else "was flat")
    return (
        f"{r.jurisdiction} average headcount {direction} "
        f"from {r.prior_avg:.1f} to {r.current_avg:.1f} "
        f"(net-new {r.net_new:+.1f})."
    )


def credit_narration(r: CreditResult) -> str:
    if not r.has_pack:
        return f"{r.jurisdiction} has no state rule pack; no state credit modeled."
    if r.qualifying_jobs <= 0:
        return (
            f"{r.jurisdiction} does not qualify: net-new {r.net_new:+.1f} is below "
            f"the threshold in its rule pack."
        )
    return (
        f"{r.jurisdiction} qualifies for {r.qualifying_jobs:.1f} jobs at "
        f"${r.annual_credit:,.0f}/yr, ${r.lifetime_credit:,.0f} lifetime "
        f"({r.program})."
    )


def discovery_narration(results: list[CreditResult]) -> str:
    hits = [r for r in results if r.has_pack and r.qualifying_jobs > 0]
    if not hits:
        return "No qualifying jurisdictions found."
    total = sum(r.lifetime_credit for r in hits)
    names = ", ".join(r.jurisdiction for r in hits)
    return (
        f"Discovery found {len(hits)} qualifying jurisdiction(s) — {names} — "
        f"totaling ${total:,.0f} lifetime."
    )


def report_narration(results: list[CreditResult]) -> str:
    identified = sum(r.lifetime_credit for r in results if r.has_pack and r.qualifying_jobs > 0)
    return (
        f"Total identified lifetime credit: ${identified:,.0f}. "
        f"Advisory only — a licensed tax practitioner must sign off before filing."
    )
