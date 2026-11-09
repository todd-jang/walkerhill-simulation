"""The three output contracts under comparison."""
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class Contract(str, Enum):
    NUMERIC = "A"
    BINARY = "B"
    REASONED = "C"


@dataclass(frozen=True)
class Reply:
    """One model response to one (persona, price) query."""

    contract: Contract
    probability: float | None = None
    accepted: bool | None = None
    reason: str | None = None

    def booked(self, rng: random.Random) -> bool:
        """Realize the reply as one customer decision."""
        if self.contract is Contract.NUMERIC:
            if self.probability is None:
                raise ValueError("numeric contract reply carries no probability")
            return rng.random() < self.probability
        if self.accepted is None:
            raise ValueError("discrete contract reply carries no decision")
        return self.accepted
