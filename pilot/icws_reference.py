"""Confirmed parameters from Majidi et al., ICWS 2026 (R5).

The full text was obtained 2026-11-10. This module pins down what the paper
actually specifies so that later baselines can be described against it instead
of against the abstract. Per proposal-methodology-v0.7 section 5.13:

- the archetype scoring procedure is absorbed as REFERENCE ONLY; our design
  does not assign archetypes numerically, so the delta table must never
  claim "we replicate the paper";
- the batched prompt structure is absorbed as rules only;
- the policy formulas are registered as benchmark candidates with the
  paper's Taupo values, which do not transfer to Walkerhill without a
  recalibration.

Priors w_k are the paper's case-study strata (112 agents: 28 budget,
12 business, 65 leisure, 7 luxury); the paper states they are assumed, not
estimated. alpha for the reference price is required explicitly because the
paper fixes it at an undisclosed baseline value.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum


class Archetype(str, Enum):
    BUDGET = "budget"
    BUSINESS = "business"
    LUXURY = "luxury"
    LEISURE = "leisure"


@dataclass(frozen=True)
class Observable:
    """Booking attributes the paper conditions archetype scores on."""

    lead_days: int
    nights: int
    adults: int
    children: int = 0


# Paper Table 1: expert-defined score contributions delta_{j,k}.
LEAD_TIME_DELTAS: tuple[tuple[tuple[int, int], dict[Archetype, float]], ...] = (
    ((0, 3), {Archetype.BUDGET: -1.0, Archetype.BUSINESS: 2.0, Archetype.LUXURY: -1.0, Archetype.LEISURE: -1.0}),
    ((4, 14), {Archetype.BUDGET: 0.0, Archetype.BUSINESS: 1.0, Archetype.LUXURY: 0.0, Archetype.LEISURE: 0.0}),
    ((15, 30), {Archetype.BUDGET: 1.0, Archetype.BUSINESS: -1.0, Archetype.LUXURY: 1.0, Archetype.LEISURE: 1.0}),
    ((31, float("inf")), {Archetype.BUDGET: 2.0, Archetype.BUSINESS: -2.0, Archetype.LUXURY: 1.0, Archetype.LEISURE: 1.0}),
)

TRIP_LENGTH_DELTAS: tuple[tuple[tuple[int, int], dict[Archetype, float]], ...] = (
    ((1, 1), {Archetype.BUDGET: -1.0, Archetype.BUSINESS: 2.0, Archetype.LUXURY: -1.0, Archetype.LEISURE: -1.0}),
    ((2, 3), {Archetype.BUDGET: 0.0, Archetype.BUSINESS: 0.0, Archetype.LUXURY: 0.0, Archetype.LEISURE: 1.0}),
    ((4, 7), {Archetype.BUDGET: 0.0, Archetype.BUSINESS: -1.0, Archetype.LUXURY: 1.0, Archetype.LEISURE: 2.0}),
    ((8, float("inf")), {Archetype.BUDGET: 1.0, Archetype.BUSINESS: -2.0, Archetype.LUXURY: 2.0, Archetype.LEISURE: 2.0}),
)


def occupant_deltas(observable: Observable) -> dict[Archetype, float]:
    """Occupant contributions. Unlisted compositions contribute zero."""
    if observable.adults == 1 and observable.children == 0:
        return {Archetype.BUDGET: 1.0, Archetype.BUSINESS: 1.0, Archetype.LUXURY: -1.0, Archetype.LEISURE: 0.0}
    if observable.adults == 2 and observable.children == 0:
        return {Archetype.BUDGET: 0.0, Archetype.BUSINESS: 1.0, Archetype.LUXURY: 1.0, Archetype.LEISURE: 1.0}
    if observable.adults == 1 and observable.children >= 1:
        return {Archetype.BUDGET: 1.0, Archetype.BUSINESS: -1.0, Archetype.LUXURY: -1.0, Archetype.LEISURE: 1.0}
    if observable.adults >= 2 and observable.children >= 1:
        return {Archetype.BUDGET: -1.0, Archetype.BUSINESS: -2.0, Archetype.LUXURY: 2.0, Archetype.LEISURE: 2.0}
    return {archetype: 0.0 for archetype in Archetype}


PAPER_PRIORS: dict[Archetype, float] = {
    Archetype.BUDGET: 28 / 112,
    Archetype.BUSINESS: 12 / 112,
    Archetype.LUXURY: 7 / 112,
    Archetype.LEISURE: 65 / 112,
}


def _delta(signal: tuple[tuple[tuple[int, int], dict[Archetype, float]], ...], value: int) -> dict[Archetype, float]:
    for (low, high), deltas in signal:
        if low <= value <= high:
            return deltas
    raise ValueError(f"no scoring bucket covers value {value}")


def archetypes(observable: Observable, priors: dict[Archetype, float]) -> dict[Archetype, float]:
    """Softmax posterior over archetypes (paper equations 13-14)."""
    scores = {
        archetype: math.log(priors[archetype])
        + _delta(LEAD_TIME_DELTAS, observable.lead_days)[archetype]
        + _delta(TRIP_LENGTH_DELTAS, observable.nights)[archetype]
        + occupant_deltas(observable)[archetype]
        for archetype in Archetype
    }
    peak = max(scores.values())
    evidence = sum(math.exp(score - peak) for score in scores.values())
    normalized = {archetype: math.exp(score - peak) / evidence for archetype, score in scores.items()}
    return normalized


def assign(observable: Observable, priors: dict[Archetype, float], rng: random.Random) -> Archetype:
    """Sample one archetype from the posterior (paper follows [18])."""
    options = list(Archetype)
    weights = [archetypes(observable, priors)[archetype] for archetype in options]
    return rng.choices(options, weights=weights, k=1)[0]


def reference_price(recent_mean: float, competitor_mean: float, alpha: float) -> float:
    """Reference-price anchor (paper equation 6). alpha is an assumption input."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must lie in [0, 1]")
    return alpha * recent_mean + (1.0 - alpha) * competitor_mean


def dynamic_price(base_price: float, occupancy_ratio: float) -> float:
    """Occupancy-based posted price (paper equations 21-22, Taupo values)."""
    multiplier = max(0.65, 1.0 + 0.4 * (occupancy_ratio - 0.5))
    return base_price * multiplier


# Paper section III.E.1: batched multi-agent call, absorbed as rules.
BATCH_SPEC: dict[str, object] = {
    "one_call_per_simulation_day": True,
    "shared_state_once": True,
    "sub_batch_when_context_overflow": True,
    "invalid_json_fallback": "no_booking",
    "invalid_category_fallback": "no_booking",
    "track_invalid_response_rate": True,
    "case_study_model": "GPT-4o",
    "case_study_temperature": 0.7,
}
