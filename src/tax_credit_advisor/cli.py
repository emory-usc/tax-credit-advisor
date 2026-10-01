"""CLI: portfolio / discover / simulate / audit."""

from __future__ import annotations

import argparse
import sys

from . import agents, engine
from .trail import TrailRecorder


def _print_result(r) -> None:
    if r.has_pack:
        print(
            f"{r.jurisdiction:3s} {r.program:32s} net-new {r.net_new:+5.1f}  "
            f"qual {r.qualifying_jobs:5.1f}  ${r.annual_credit:>8,.0f}/yr  "
            f"${r.lifetime_credit:>10,.0f} lifetime"
        )
    else:
        print(f"{r.jurisdiction:3s} (no state pack)            net-new {r.net_new:+5.1f}")


def cmd_portfolio() -> None:
    for r in engine.portfolio():
        _print_result(r)


def cmd_discover() -> None:
    results = engine.portfolio()
    hits = [r for r in results if r.has_pack and r.qualifying_jobs > 0]
    print(agents.discovery_narration(results))
    for r in hits:
        print(f"  {r.jurisdiction}: {agents.credit_narration(r)}")


def cmd_simulate(jurisdiction: str, delta: float) -> None:
    r = engine.simulate(jurisdiction, delta)
    print(agents.headcount_narration(r))
    print(agents.credit_narration(r))


def cmd_audit(jurisdiction: str) -> None:
    r = engine.compute_credit(engine.SITES[jurisdiction], engine.load_pack(jurisdiction))
    trail = TrailRecorder()
    engine.compute_credit(engine.SITES[jurisdiction], engine.load_pack(jurisdiction), trail)
    print(f"audit trail for {jurisdiction}:")
    for s in trail.steps:
        print(f"  {s.step:16s} {s.formula}")
        print(f"                 inputs={s.inputs} -> output={s.output}")
    print(f"  fingerprint (sha256): {trail.fingerprint()}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tax-credit")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("portfolio")
    sub.add_parser("discover")

    s = sub.add_parser("simulate")
    s.add_argument("jurisdiction")
    s.add_argument("delta", type=float)

    a = sub.add_parser("audit")
    a.add_argument("jurisdiction")

    args = p.parse_args(argv)
    if args.cmd == "portfolio":
        cmd_portfolio()
    elif args.cmd == "discover":
        cmd_discover()
    elif args.cmd == "simulate":
        cmd_simulate(args.jurisdiction, args.delta)
    elif args.cmd == "audit":
        cmd_audit(args.jurisdiction)
    return 0


if __name__ == "__main__":
    sys.exit(main())
