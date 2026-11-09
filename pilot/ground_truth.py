"""Analytic demand model that supplies the reference policy ranking.

Two-hotel nested logit over a 30-day horizon with capacity 100. The model is
deterministic, so every policy has exactly one expected revenue and the
ranking is total. Persona populations are quantile samples of this same
model, which keeps the finite simulator consistent with the reference.

Price sensitivity (rho) may vary across personas. When it does, the reference
demand is the exact mixture over the persona sensitivities, so the ground
truth still carries no sampling error.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

DAY_HORIZON = 30
CAPACITY = 100
MU = 0.5
ARRIVALS_PER_DAY = 7
PRICE_BUCKETS: tuple[int, ...] = (100, 120, 140, 160, 180, 200, 220)
COMPETITOR_PRICE = 160
ALPHA = 3.0
RHO = 2.5
ETA = 0.6
MARKET = 1.0

OCC_BANDS = 3
LEAD_BANDS = 3


@dataclass(frozen=True)
class Policy:
    """Price grid indexed by occupancy band (rows) and lead-time band (cols)."""

    name: str
    grid: tuple[tuple[int, ...], ...]

    def price(self, occ_band: int, lead_band: int) -> int:
        return self.grid[occ_band][lead_band]


def flat_policy(name: str, price: int) -> Policy:
    """A policy that charges one price regardless of band."""
    return Policy(name, tuple(tuple(price for _ in range(LEAD_BANDS)) for _ in range(OCC_BANDS)))


def arrival_book_prob(price: int, mu: float = MU, rho: float = RHO) -> float:
    """Probability that one arriving customer books with us at this price."""
    own = ALPHA - rho * price / 100.0 + ETA * MARKET
    comp = ALPHA - rho * COMPETITOR_PRICE / 100.0 + ETA * MARKET
    e_own = math.exp(own / mu)
    e_comp = math.exp(comp / mu)
    inside = (e_own + e_comp) ** mu
    p_hotel = inside / (1.0 + inside)
    return p_hotel * e_own / (e_own + e_comp)


def mixture_book_prob(price: int, rhos: Sequence[float], mu: float = MU) -> float:
    """Booking probability averaged over a finite sensitivity distribution."""
    if not rhos:
        raise ValueError("rhos must be non-empty")
    return sum(arrival_book_prob(price, mu=mu, rho=rho) for rho in rhos) / len(rhos)


def occ_band(occupancy: float) -> int:
    ratio = occupancy / CAPACITY
    if ratio < 0.45:
        return 0
    if ratio < 0.75:
        return 1
    return 2


def lead_band(days_remaining: int) -> int:
    if days_remaining > 20:
        return 0
    if days_remaining > 10:
        return 1
    return 2


def expected_revenue(policy: Policy, rhos: Sequence[float] | None = None) -> float:
    """Fluid-limit revenue, optionally averaged over a sensitivity distribution."""
    if rhos is None:
        prob = arrival_book_prob
    else:
        prob = lambda price: mixture_book_prob(price, rhos)  # noqa: E731
    occ = 0.0
    revenue = 0.0
    for day in range(DAY_HORIZON):
        if occ >= CAPACITY:
            break
        price = policy.price(occ_band(occ), lead_band(DAY_HORIZON - day))
        bookings = min(ARRIVALS_PER_DAY * prob(price), CAPACITY - occ)
        occ += bookings
        revenue += bookings * price
    return revenue


def reference_scores(
    policies: Sequence[Policy], rhos: Sequence[float] | None = None
) -> dict[str, float]:
    return {policy.name: expected_revenue(policy, rhos) for policy in policies}


def reference_ranking(
    policies: Sequence[Policy], rhos: Sequence[float] | None = None
) -> tuple[str, ...]:
    """Policies ordered from highest to lowest expected revenue."""
    scored = reference_scores(policies, rhos)
    return tuple(sorted(scored, key=lambda name: (-scored[name], name)))


def grid_policies(base: int = 160, step: int = 20) -> tuple[Policy, ...]:
    """Nine policies: three occupancy slopes crossed with three lead-time slopes."""
    policies: list[Policy] = []
    for occ_slope in (-1, 0, 1):
        for lead_slope in (-1, 0, 1):
            grid = tuple(
                tuple(
                    base + step * (occ_slope * (band_o - 1) + lead_slope * (band_l - 1))
                    for band_l in range(LEAD_BANDS)
                )
                for band_o in range(OCC_BANDS)
            )
            policies.append(Policy(f"o{occ_slope:+d}l{lead_slope:+d}", grid))
    return tuple(policies)
