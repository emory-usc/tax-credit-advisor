# Security Policy

## Reporting a vulnerability

Report security issues privately rather than opening a public issue. Include a
description, reproduction steps, and any proposed fix. Do not include real
customer data or credentials in any report.

## Security posture

- **Deterministic math, advisory narration.** Every figure (net-new headcount,
  threshold test, annual and lifetime credit) is computed in pure Python and
  recorded as a `{step, inputs, formula, output, citation}` trail row. The
  narration roles only restate computed numbers — they can never invent a
  figure because they never compute one. No LLM is called.
- **Audit trail with SHA-256 fingerprint.** The full calculation trail is
  fingerprinted; the same inputs produce the same fingerprint, so a filing can
  be re-derived and verified.
- **Illustrative data only.** Rule packs, thresholds, and per-job amounts are
  clearly-labeled illustrative placeholders — not real statute values, not
  legal or tax advice. This is stated in the README, in the rule packs
  themselves, and on every advisory response.
- **API-key gate.** `/portfolio`, `/discover`, and `/simulate` require
  `X-API-Key` (constant-time compare). `/health` and `/ready` are open for
  probes. The default key is a documented dev-only value — set
  `TAX_CREDIT_API_KEY` for anything beyond localhost.
- **Input validation.** Simulate deltas are bounds-checked and unknown
  jurisdictions are rejected with 404 before any engine work runs.
- **Synthetic data only.** The headcount book is a fictional client generated
  from constants; no real customer data is involved.

## Supported versions

Only the latest `main` branch is supported for security fixes.
