"""Main experiment path: nine policies crossed with three heterogeneity levels.

Reports ranking fidelity for each output contract at each level and asks the
question the paper depends on: does the contract that wins at low
heterogeneity lose at high heterogeneity?

The mock backend is an oracle. A clean sweep shows whether the harness can
separate the contracts at all; it does not establish the result.
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
    grid_policies,
    lead_band,
    occ_band,
    reference_ranking,
    reference_scores,
)
from .metrics import direction_accuracy, flip_count, spearman
from .population import Persona, build_population, sensitivities

DEFAULT_LEVELS = (1.0, 3.0, 10.0)
DEFAULT_POPULATION = 40
DEFAULT_REPEATS = 8
CONTRACTS = (Contract.NUMERIC, Contract.BINARY)


def run_once(
    policy: Policy,
    contract: Contract,
    backend: Backend,
    population: Sequence[Persona],
    seed: int,
) -> float:
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


def run_level(
    policies: Sequence[Policy],
    population: Sequence[Persona],
    contract: Contract,
    repeats: int,
    seed: int,
    temperature: float,
) -> dict[str, object]:
    backend = MockBackend(temperature=temperature, seed=seed)
    totals = {policy.name: 0.0 for policy in policies}
    history: list[tuple[str, ...]] = []
    for repeat in range(repeats):
        for policy in policies:
            totals[policy.name] += run_once(
                policy, contract, backend, population, seed + 17 * repeat
            )
        history.append(tuple(sorted(totals, key=lambda n: (-totals[n], n))))

    reference = reference_scores(policies, sensitivities(population))
    order = [policy.name for policy in policies]
    accuracy, pairs = direction_accuracy(totals, reference)
    return {
        "contract": contract.value,
        "spearman": round(spearman([totals[n] for n in order], [reference[n] for n in order]), 4),
        "direction_accuracy": round(accuracy, 4),
        "pairs": pairs,
        "flips": flip_count(history),
        "ranking": list(history[-1]),
        "reference": list(reference_ranking(policies, sensitivities(population))),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="nine-policy contract sweep")
    parser.add_argument("--levels", type=float, nargs="+", default=list(DEFAULT_LEVELS))
    parser.add_argument("--population", type=int, default=DEFAULT_POPULATION)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    policies = grid_policies()
    results: list[dict[str, object]] = []
    for level in args.levels:
        population = build_population(args.population, level)
        for index, contract in enumerate(CONTRACTS):
            row = run_level(
                policies,
                population,
                contract,
                args.repeats,
                args.seed + 1000 * index,
                args.temperature,
            )
            row["heterogeneity"] = level
            results.append(row)

    gaps = []
    for level in args.levels:
        numeric = next(r for r in results if r["heterogeneity"] == level and r["contract"] == "A")
        binary = next(r for r in results if r["heterogeneity"] == level and r["contract"] == "B")
        gaps.append(round(float(numeric["direction_accuracy"]) - float(binary["direction_accuracy"]), 4))

    crosses = any(g > 0 for g in gaps) and any(g < 0 for g in gaps)
    payload = {
        "mode": "mock-oracle" if args.temperature == 0.0 else "mock-noisy",
        "policies": len(policies),
        "population": args.population,
        "repeats": args.repeats,
        "accuracy_gap_A_minus_B": dict(zip([str(l) for l in args.levels], gaps)),
        "crossover": crosses,
        "rows": results,
        "evidence_grade": "harness only; not a result",
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"policies {len(policies)}, population {args.population}, repeats {args.repeats}, "
          f"temperature {args.temperature}")
    print(f"{'hetero':>7}{'contract':>9}{'spearman':>10}{'acc':>8}{'flips':>7}  top policy")
    for row in results:
        print(f"{row['heterogeneity']:>7.1f}{row['contract']:>9}{row['spearman']:>10.3f}"
              f"{row['direction_accuracy']:>8.3f}{row['flips']:>7}  {row['ranking'][0]}")
    print()
    print("accuracy gap A-B :", {k: v for k, v in payload["accuracy_gap_A_minus_B"].items()})
    print("crossover        :", "YES" if crosses else "NO")
    if payload["mode"] == "mock-oracle":
        print("note             : oracle sweep; separates plumbing, not the hypothesis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
