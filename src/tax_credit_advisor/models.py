"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TrailStep:
    step: str
    inputs: dict
    formula: str
    output: dict
    citation: str


@dataclass(frozen=True)
class CreditResult:
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
    trail: tuple[TrailStep, ...] = field(default_factory=tuple)
