"""Quantile persona population.

Persona i represents quantile (i + 0.5) / n of the taste distribution implied
by the analytic model. A persona accepts iff its quantile falls below the
model's accept probability, so a finite population reproduces reference demand
in the limit and carries only sampling noise.

Price sensitivity is spread across personas on a log scale. A range of 1.0
makes every persona identical (the homogeneous case); a range of R makes the
most sensitive persona R times more price sensitive than the least sensitive.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .ground_truth import RHO


@dataclass(frozen=True)
class Persona:
    index: int
    quantile: float
    rho: float


def build_population(size: int = 40, sensitivity_range: float = 1.0) -> tuple[Persona, ...]:
    """Build a quantile population with an optional sensitivity spread."""
    if size < 2:
        raise ValueError("population size must be at least 2")
    if sensitivity_range < 1.0:
        raise ValueError("sensitivity_range must be at least 1.0")
    spread = 0.5 * math.log(sensitivity_range)
    personas = []
    for index in range(size):
        quantile = (index + 0.5) / size
        centred = 2.0 * quantile - 1.0
        personas.append(Persona(index, quantile, RHO * math.exp(spread * centred)))
    return tuple(personas)


def sensitivities(population: tuple[Persona, ...]) -> tuple[float, ...]:
    return tuple(persona.rho for persona in population)
