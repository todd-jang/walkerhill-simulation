"""Pilot gate runner.

Implements the one-week pilot from experiment-design-v1 section 7: two
policies at one price point each, forty personas, contracts A and B, ten
repeats. Reports how often the pairwise ranking flips and the resulting row of
the pilot decision table.

The mock backend is an oracle stand-in. A clean run proves the plumbing works;
it says nothing about real LLM behaviour.

Branch reachability offline: the oracle reaches STOP and, under heavy noise,
the two unstable branches. It cannot reach "A dominates; design unjustified",
because a quantile population is not systematically worse than a calibrated
probability. That branch needs a real model that misreports probabilities.
"""
from __future__ import annotations

import argparse
import json
import random
from collections.abc import Sequence

from .backend import Backend, MockBackend
from .contracts import Contract
from .ground_truth import (
    ARRIVALS_PER_DAY,
    CAPACITY,
    DAY_HORIZON,
    Policy,
    expected_revenue,
    flat_policy,
    lead_band,
    occ_band,
    reference_ranking,
)
from .metrics import cost_to_stability, direction_accuracy, flip_count
from .population import Persona, build_population

DEFAULT_PRICES = (140, 160)
DEFAULT_REPEATS = 10
DEFAULT_POPULATION = 40
CONTRACTS = (Contract.NUMERIC, Contract.BINARY)
DECISION_TABLE = {
    (True, True): "STOP: no divergence, no paper",
    (True, False): "A dominates; design unjustified",
    (False, True): "PROCEED: numeric contract unstable",
    (False, False): "both unstable; seek heterogeneity condition",
}


def run_once(
    policy: Policy,
    contract: Contract,
    backend: Backend,
    population: Sequence[Persona],
    seed: int,
) -> float:
    """One simulated 30-day stay for one policy under one contract."""
    rng = random.Random(seed)
    occupancy = 0
    revenue = 0.0
    for day in range(DAY_HORIZON):
        if occupancy >= CAPACITY:
            break
        price = policy.price(occ_band(occupancy), lead_band(DAY_HORIZON - day))
        for _ in range(ARRIVALS_PER_DAY):
            if occupancy >= CAPACITY:
                break
            persona = population[rng.randrange(len(population))]
            if backend.reply(contract, persona, price).booked(rng):
                occupancy += 1
                revenue += price
    return revenue


def rankings_by_repeat(
    policies: Sequence[Policy],
    contract: Contract,
    backend: Backend,
    population: Sequence[Persona],
    seed: int,
    repeats: int,
) -> tuple[tuple[str, ...], ...]:
    """Ranking after each cumulative repeat."""
    totals = {policy.name: 0.0 for policy in policies}
    history: list[tuple[str, ...]] = []
    for repeat in range(repeats):
        for policy in policies:
            totals[policy.name] += run_once(policy, contract, backend, population, seed + repeat)
        history.append(tuple(sorted(totals, key=lambda name: (-totals[name], name))))
    return tuple(history)


def pilot_decision(stable_a: bool, stable_b: bool) -> str:
    return DECISION_TABLE[(stable_a, stable_b)]


def _parse(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="output-contract pilot gate")
    parser.add_argument("--prices", type=int, nargs=2, default=list(DEFAULT_PRICES))
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--population", type=int, default=DEFAULT_POPULATION)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse(argv)
    population = build_population(args.population)
    policies = tuple(flat_policy(f"P{i}", price) for i, price in enumerate(args.prices))
    reference_order = reference_ranking(policies)
    reference = {policy.name: expected_revenue(policy) for policy in policies}
    calls_per_step = ARRIVALS_PER_DAY * DAY_HORIZON * len(policies)

    rows = []
    for index, contract in enumerate(CONTRACTS):
        # Arrivals stay common across contracts; model noise is drawn from an
        # independent stream so the two contracts are not artificially tied.
        backend = MockBackend(temperature=args.temperature, seed=args.seed + 1000 * index)
        history = rankings_by_repeat(
            policies, contract, backend, population, args.seed, args.repeats
        )
        final = history[-1]
        induced = {name: float(len(policies) - final.index(name)) for name in final}
        accuracy, pairs = direction_accuracy(induced, reference)
        rows.append(
            {
                "contract": contract.value,
                "flips": flip_count(history),
                "stable": flip_count(history) == 0,
                "cost_to_stability": cost_to_stability(history, calls_per_step),
                "direction_accuracy": round(accuracy, 4),
                "pairs": pairs,
                "ranking": list(final),
            }
        )

    stable_a = bool(rows[0]["stable"])
    stable_b = bool(rows[1]["stable"])
    payload = {
        "mode": "mock-oracle" if args.temperature == 0.0 else "mock-noisy",
        "temperature": args.temperature,
        "population": args.population,
        "repeats": args.repeats,
        "reference_order": list(reference_order),
        "reference_revenue": {k: round(v, 1) for k, v in reference.items()},
        "calls_per_checkpoint": calls_per_step,
        "contracts": rows,
        "decision": pilot_decision(stable_a, stable_b),
        "evidence_grade": "harness only; not a result",
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"mode            : {payload['mode']} (temperature={args.temperature})")
    print(f"population      : {args.population} personas, {args.repeats} repeats")
    print(f"policies        : {', '.join(f'{p.name}={p.grid[0][0]}' for p in policies)}")
    print(
        "reference       : "
        + " > ".join(reference_order)
        + f"  (revenue {', '.join(f'{k}={v:.0f}' for k, v in reference.items())})"
    )
    print(f"calls/checkpoint: {calls_per_step}")
    print()
    print(f"{'contract':<9}{'flips':>6}{'stable':>8}{'cost':>8}{'dir':>8}  ranking")
    for row in rows:
        cost = row["cost_to_stability"]
        print(
            f"{row['contract']:<9}{row['flips']:>6}{str(row['stable']):>8}"
            f"{(cost if cost is not None else 'never'):>8}"
            f"{row['direction_accuracy']:>8.2f}  {' > '.join(row['ranking'])}"
        )
    print()
    print(f"decision        : {payload['decision']}")
    if payload["mode"] == "mock-oracle":
        print("note            : oracle run; validates plumbing, not the hypothesis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
