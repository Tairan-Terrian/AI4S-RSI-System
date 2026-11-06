"""Proposal, evaluation, selection, feedback and traceable run records."""

import json
from dataclasses import asdict
from pathlib import Path

from .adapters import (
    EvaluationAdapter,
    ProposalAdapter,
    SyntheticEvaluator,
    SyntheticProposer,
)


def load_config(config_path: Path) -> tuple[dict, dict]:
    config_path = Path(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config["mode"] != "synthetic":
        raise ValueError("This public demo supports mode='synthetic' only.")
    if config["rounds"] < 1:
        raise ValueError("rounds must be positive")
    if not 1 <= config["select"] <= config["candidates_per_round"]:
        raise ValueError("select must be between 1 and candidates_per_round")
    if config["initial_radius"] <= 0:
        raise ValueError("initial_radius must be positive")
    task_path = config_path.parent / config["task_file"]
    task = json.loads(task_path.read_text(encoding="utf-8"))
    bounds = task["parameter_bounds"]
    if set(bounds) != {"x", "y"} or any(low >= high for low, high in bounds.values()):
        raise ValueError("The demo requires increasing x and y parameter bounds.")
    return config, task


def run(
    config: dict,
    task: dict,
    proposer: ProposalAdapter | None = None,
    evaluator: EvaluationAdapter | None = None,
) -> dict:
    proposer = proposer or SyntheticProposer(config["seed"], config["initial_radius"])
    evaluator = evaluator or SyntheticEvaluator()
    feedback = None
    rounds = []
    for number in range(1, config["rounds"] + 1):
        proposals = proposer.propose(task, number, config["candidates_per_round"], feedback)
        evaluations = [evaluator.evaluate(candidate) for candidate in proposals]
        ranked = sorted(evaluations, key=lambda item: (
            -item.metrics["quality"], item.metrics["cost"], item.candidate_id
        ))
        selected = [item.candidate_id for item in ranked[:config["select"]]]
        leader = next(candidate for candidate in proposals if candidate.id == selected[0])
        previous_radius = feedback["radius"] if feedback else config["initial_radius"]
        feedback = {
            "center": leader.parameters,
            "radius": round(previous_radius * 0.65, 6),
            "leading_quality": ranked[0].metrics["quality"],
            "action": "Refine sampling around the leading candidate.",
        }
        rounds.append({
            "round": number,
            "proposals": [asdict(candidate) for candidate in proposals],
            "evaluations": [asdict(evaluation) for evaluation in evaluations],
            "selected": selected,
            "feedback": feedback,
        })
    # Omit local file paths from portable output records.
    public_config = {key: value for key, value in config.items() if key != "task_file"}
    return {
        "schema_version": "1.0",
        "mode": "synthetic",
        "notice": "Demonstration data from a toy mathematical function.",
        "task": task,
        "config": public_config,
        "rounds": rounds,
        "final_selection": rounds[-1]["selected"],
    }


def summary(record: dict) -> str:
    lines = [
        "# Workflow demonstration",
        "",
        record["notice"],
        "",
        f"Task: {record['task']['name']}",
        "",
        "| Round | Proposals | Selected | Leading quality | Next radius |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in record["rounds"]:
        lines.append(
            f"| {item['round']} | {len(item['proposals'])} | {len(item['selected'])} "
            f"| {item['feedback']['leading_quality']:.6f} "
            f"| {item['feedback']['radius']:.6f} |"
        )
    lines.extend(["", "Final selection: " + ", ".join(record["final_selection"]), ""])
    return "\n".join(lines)


def save(record: dict, output: Path) -> None:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "run.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output / "summary.md").write_text(summary(record), encoding="utf-8")
