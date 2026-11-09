"""Model backends.

MockBackend is a seeded oracle: it answers from the analytic model with an
optional temperature that injects noise. It exists so the harness runs at zero
API cost and so every branch of the pilot decision table can be exercised. Its
output is not evidence about real LLM behaviour.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .contracts import Contract, Reply
from .ground_truth import arrival_book_prob
from .population import Persona


class Backend:
    """Interface a real model adapter must implement."""

    def reply(self, contract: Contract, persona: Persona, price: int) -> Reply:
        raise NotImplementedError


@dataclass
class MockBackend(Backend):
    temperature: float = 0.0
    seed: int = 7

    def __post_init__(self) -> None:
        if self.temperature < 0.0:
            raise ValueError("temperature must be non-negative")
        self._rng = random.Random(self.seed)

    def reply(self, contract: Contract, persona: Persona, price: int) -> Reply:
        truth = arrival_book_prob(price, rho=persona.rho)
        if self.temperature > 0.0:
            truth = _clip(truth + self._rng.gauss(0.0, self.temperature))
        if contract is Contract.NUMERIC:
            return Reply(contract, probability=truth)
        accepted = persona.quantile < truth
        reason = None
        if contract is Contract.REASONED:
            reason = "value" if accepted else "price"
        return Reply(contract, accepted=accepted, reason=reason)


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class LLMBackend(Backend):
    """Real model adapter. Needs credentials and an approved call budget.

    See experiment-design-v1 section 7 for the pilot budget before enabling.
    """

    def __init__(self, model: str, api_key_env: str = "OPENAI_API_KEY") -> None:
        self.model = model
        self.api_key_env = api_key_env

    def reply(self, contract: Contract, persona: Persona, price: int) -> Reply:
        raise NotImplementedError(
            f"provider adapter for {self.model!r} is not wired; "
            f"read the key from {self.api_key_env} and honour the pilot budget"
        )
