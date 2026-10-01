"""TrailRecorder: every computed step is recorded and fingerprinted.

The fingerprint is a SHA-256 over the canonical JSON of the trail, so a
re-run over the same inputs produces an identical fingerprint.
"""

from __future__ import annotations

import hashlib
import json

from .models import TrailStep


class TrailRecorder:
    def __init__(self):
        self.steps: list[TrailStep] = []

    def record(self, step: str, inputs: dict, formula: str, output: dict, citation: str) -> None:
        self.steps.append(
            TrailStep(
                step=step,
                inputs=dict(sorted(inputs.items())),
                formula=formula,
                output=dict(sorted(output.items())),
                citation=citation,
            )
        )

    def fingerprint(self) -> str:
        canonical = json.dumps(
            [s.__dict__ for s in self.steps], sort_keys=True, default=str
        )
        return hashlib.sha256(canonical.encode()).hexdigest()
