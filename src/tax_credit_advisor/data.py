"""Synthetic headcount book for a fictional client, Cascade Freight & Logistics.

prior_avg and current_avg are average monthly headcount for the prior and
current tax year respectively. Entirely synthetic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Site:
    jurisdiction: str
    prior_avg: float
    current_avg: float


SITES: dict[str, Site] = {
    s.jurisdiction: s
    for s in [
        Site("GA", 40.0, 60.0),
        Site("NC", 20.0, 35.0),
        Site("SC", 15.0, 18.0),
        Site("NY", 50.0, 45.0),
        Site("OH", 15.0, 16.0),
        Site("TX", 30.0, 34.0),
    ]
}
