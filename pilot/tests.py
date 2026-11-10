"""Tests for the pilot harness."""
from __future__ import annotations

import random
import unittest

from .backend import MockBackend
from .contracts import Contract, Reply
from .ground_truth import (
    PRICE_BUCKETS,
    arrival_book_prob,
    expected_revenue,
    flat_policy,
    reference_ranking,
)
from .icws_reference import (
    BATCH_SPEC,
    PAPER_PRIORS,
    Archetype,
    Observable,
    archetypes,
    assign,
    dynamic_price,
    reference_price,
)
from .metrics import cost_to_stability, direction_accuracy, flip_count, spearman
from .pilot_run import (
    DEFAULT_POPULATION,
    DEFAULT_PRICES,
    DEFAULT_REPEATS,
    pilot_decision,
    rankings_by_repeat,
)
from .population import build_population


class GroundTruthTests(unittest.TestCase):
    def test_book_probability_falls_as_price_rises(self) -> None:
        probs = [arrival_book_prob(price) for price in PRICE_BUCKETS]
        self.assertEqual(probs, sorted(probs, reverse=True))
        self.assertEqual(len(set(probs)), len(probs))

    def test_low_price_outearns_high_price(self) -> None:
        low = expected_revenue(flat_policy("low", 140))
        high = expected_revenue(flat_policy("high", 190))
        self.assertGreater(low, high)

    def test_cheapest_price_does_not_maximise_revenue(self) -> None:
        revenues = {price: expected_revenue(flat_policy(str(price), price)) for price in PRICE_BUCKETS}
        best = max(revenues, key=lambda price: revenues[price])
        self.assertNotEqual(best, PRICE_BUCKETS[0])

    def test_reference_ranking_is_total(self) -> None:
        policies = [flat_policy("a", 140), flat_policy("b", 190), flat_policy("c", 160)]
        order = reference_ranking(policies)
        self.assertEqual(sorted(order), ["a", "b", "c"])


class PopulationTests(unittest.TestCase):
    def test_quantiles_stay_inside_the_unit_interval(self) -> None:
        population = build_population(40)
        self.assertTrue(all(0.0 < persona.quantile < 1.0 for persona in population))

    def test_too_small_population_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_population(1)


class ContractTests(unittest.TestCase):
    def test_numeric_reply_without_probability_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Reply(Contract.NUMERIC).booked(random.Random(1))

    def test_discrete_reply_without_decision_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Reply(Contract.BINARY).booked(random.Random(1))


class MetricTests(unittest.TestCase):
    def test_spearman_is_one_for_identical_orders(self) -> None:
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)

    def test_spearman_is_minus_one_for_reversed_orders(self) -> None:
        self.assertAlmostEqual(spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0)

    def test_direction_accuracy_is_one_for_perfect_order(self) -> None:
        accuracy, pairs = direction_accuracy({"a": 3.0, "b": 2.0, "c": 1.0}, {"a": 9, "b": 5, "c": 1})
        self.assertAlmostEqual(accuracy, 1.0)
        self.assertEqual(pairs, 3)

    def test_cost_to_stability_waits_for_three_matching_checkpoints(self) -> None:
        history = (("a", "b"), ("b", "a"), ("a", "b"), ("a", "b"), ("a", "b"))
        self.assertEqual(cost_to_stability(history, 100), 500)

    def test_cost_to_stability_is_none_when_ranking_never_holds(self) -> None:
        history = (("a", "b"), ("b", "a"), ("a", "b"), ("b", "a"))
        self.assertIsNone(cost_to_stability(history, 100))

    def test_flip_count_counts_changes(self) -> None:
        history = (("a", "b"), ("a", "b"), ("b", "a"), ("a", "b"))
        self.assertEqual(flip_count(history), 2)


class IcwsReferenceTests(unittest.TestCase):
    """R5 confirmed parameters (v0.7 section 5.13). Paper claims only."""

    SHORT_LEAD_SOLO = Observable(lead_days=2, nights=1, adults=1)

    def test_posteriors_sum_to_one(self) -> None:
        posterior = archetypes(self.SHORT_LEAD_SOLO, PAPER_PRIORS)
        self.assertAlmostEqual(sum(posterior.values()), 1.0)

    def test_short_lead_short_stay_solo_leans_business(self) -> None:
        posterior = archetypes(self.SHORT_LEAD_SOLO, PAPER_PRIORS)
        best = max(posterior, key=posterior.get)
        self.assertIs(best, Archetype.BUSINESS)

    def test_long_lead_family_trip_pushes_business_last(self) -> None:
        family = Observable(lead_days=45, nights=9, adults=2, children=2)
        posterior = archetypes(family, PAPER_PRIORS)
        self.assertLess(posterior[Archetype.BUSINESS], posterior[Archetype.LUXURY])
        self.assertLess(posterior[Archetype.BUSINESS], posterior[Archetype.LEISURE])

    def test_assignment_stays_in_the_domain(self) -> None:
        for _ in range(50):
            self.assertIn(assign(self.SHORT_LEAD_SOLO, PAPER_PRIORS, random.Random(3)), Archetype)

    def test_dynamic_price_rises_with_occupancy_and_floors(self) -> None:
        prices = [dynamic_price(200.0, occupancy / 100) for occupancy in range(0, 101, 5)]
        self.assertEqual(prices, sorted(prices))
        # Paper values: at empty rooms the multiplier is max(0.65, 1 + 0.4*(0-0.5)) = 0.8.
        self.assertEqual(prices[0], 160.0)
        self.assertGreaterEqual(prices[0], 200.0 * 0.65)

    def test_reference_price_interpolates(self) -> None:
        self.assertAlmostEqual(reference_price(100.0, 200.0, alpha=0.25), 175.0)
        with self.assertRaises(ValueError):
            reference_price(100.0, 200.0, alpha=1.5)

    def test_batch_spec_covers_the_fallback_rules(self) -> None:
        self.assertIs(BATCH_SPEC["one_call_per_simulation_day"], True)
        self.assertEqual(BATCH_SPEC["invalid_json_fallback"], "no_booking")
        self.assertIs(BATCH_SPEC["track_invalid_response_rate"], True)


class PilotTests(unittest.TestCase):
    def test_oracle_run_is_stable_for_the_default_pair(self) -> None:
        policies = [flat_policy(f"P{i}", price) for i, price in enumerate(DEFAULT_PRICES)]
        population = build_population(DEFAULT_POPULATION)
        for contract in (Contract.NUMERIC, Contract.BINARY):
            backend = MockBackend(temperature=0.0, seed=3)
            history = rankings_by_repeat(policies, contract, backend, population, 3, DEFAULT_REPEATS)
            self.assertEqual(flip_count(history), 0, msg=f"contract {contract.value} flipped")

    def test_near_tie_pair_is_undetectable(self) -> None:
        """A 1% revenue gap sits inside sampling noise, so the pilot avoids it."""
        policies = [flat_policy("P0", 120), flat_policy("P1", 140)]
        population = build_population(DEFAULT_POPULATION)
        backend = MockBackend(temperature=0.0, seed=1)
        history = rankings_by_repeat(policies, Contract.NUMERIC, backend, population, 1, DEFAULT_REPEATS)
        self.assertGreater(flip_count(history), 0)

    def test_decision_table_matches_the_protocol(self) -> None:
        self.assertIn("no paper", pilot_decision(True, True))
        self.assertIn("design unjustified", pilot_decision(True, False))
        self.assertIn("PROCEED", pilot_decision(False, True))
        self.assertIn("heterogeneity", pilot_decision(False, False))


if __name__ == "__main__":
    unittest.main()
