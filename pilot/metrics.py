"""Ranking and comparison metrics."""
from __future__ import annotations

from collections.abc import Mapping, Sequence


def _ranks(values: Sequence[float]) -> list[float]:
    """Competition ranking with ties averaged."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        shared = (start + end) / 2.0 + 1.0
        for k in range(start, end + 1):
            ranks[order[k]] = shared
        start = end + 1
    return ranks


def spearman(left: Sequence[float], right: Sequence[float]) -> float:
    """Tie-aware Spearman correlation."""
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("spearman needs two equal sequences of length >= 2")
    rl = _ranks(left)
    rr = _ranks(right)
    n = len(rl)
    mean_l = sum(rl) / n
    mean_r = sum(rr) / n
    cov = sum((a - mean_l) * (b - mean_r) for a, b in zip(rl, rr))
    var_l = sum((a - mean_l) ** 2 for a in rl)
    var_r = sum((b - mean_r) ** 2 for b in rr)
    if var_l == 0.0 or var_r == 0.0:
        return 0.0
    return cov / (var_l ** 0.5 * var_r ** 0.5)


def direction_accuracy(
    induced: Mapping[str, float], reference: Mapping[str, float]
) -> tuple[float, int]:
    """Share of policy pairs whose ordering the simulator gets right."""
    names = sorted(induced)
    hits = 0
    total = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]
            true_gap = reference[a] - reference[b]
            if true_gap == 0.0:
                continue
            total += 1
            got = induced[a] - induced[b]
            if got != 0.0 and (got > 0.0) == (true_gap > 0.0):
                hits += 1
    return (hits / total if total else 0.0), total


def cost_to_stability(
    rankings: Sequence[tuple[str, ...]], calls_per_step: int
) -> int | None:
    """Calls needed before the ranking holds for three consecutive checkpoints."""
    run = 1
    for k in range(1, len(rankings)):
        run = run + 1 if rankings[k] == rankings[k - 1] else 1
        if run >= 3:
            return (k + 1) * calls_per_step
    return None


def flip_count(rankings: Sequence[tuple[str, ...]]) -> int:
    """Number of times the ranking changed between consecutive checkpoints."""
    return sum(1 for a, b in zip(rankings, rankings[1:]) if a != b)
