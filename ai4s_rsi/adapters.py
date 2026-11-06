"""Replaceable proposal and evaluation interfaces with synthetic demo adapters.

The reference evaluator is a toy mathematical function. It is not a scientific
predictor, an external service, or a language model.
"""

from dataclasses import dataclass
from random import Random
from typing import Protocol


@dataclass(frozen=True)
class Candidate:
    id: str
    parameters: dict[str, float]


@dataclass(frozen=True)
class Evaluation:
    candidate_id: str
    metrics: dict[str, float]
    status: str = "synthetic"


class ProposalAdapter(Protocol):
    def propose(
        self, task: dict, round_number: int, count: int, feedback: dict | None
    ) -> list[Candidate]:
        ...


class EvaluationAdapter(Protocol):
    def evaluate(self, candidate: Candidate) -> Evaluation:
        ...


class SyntheticProposer:
    """Seeded exploration around the previous round's leading candidate."""

    def __init__(self, seed: int, initial_radius: float) -> None:
        self.random = Random(seed)
        self.initial_radius = initial_radius

    def propose(
        self, task: dict, round_number: int, count: int, feedback: dict | None
    ) -> list[Candidate]:
        bounds = task["parameter_bounds"]
        center = feedback["center"] if feedback else {
            key: (low + high) / 2 for key, (low, high) in bounds.items()
        }
        radius = feedback["radius"] if feedback else self.initial_radius
        candidates = []
        for index in range(count):
            # Retain the current center so that feedback has an explicit anchor.
            params = {
                key: round(
                    max(low, min(high, center[key] + (
                        0 if index == 0 else self.random.uniform(-radius, radius)
                    ))),
                    6,
                )
                for key, (low, high) in bounds.items()
            }
            candidates.append(Candidate(f"candidate-{round_number}-{index + 1}", params))
        return candidates


class SyntheticEvaluator:
    """A transparent two-parameter toy score, used only to illustrate data flow."""

    def evaluate(self, candidate: Candidate) -> Evaluation:
        x, y = candidate.parameters["x"], candidate.parameters["y"]
        quality = 1.0 / (1.0 + (x - 0.25) ** 2 + (y + 0.35) ** 2)
        cost = (abs(x) + abs(y)) / 2.0
        return Evaluation(candidate.id, {
            "quality": round(quality, 6),
            "cost": round(cost, 6),
        })
