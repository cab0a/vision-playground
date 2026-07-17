"""Command-line interface for registered Vision Playground experiments."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from vision_playground.runner import (
    EXPERIMENTS,
    ExperimentOutcome,
    run_all_experiments,
    run_experiment,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the unified command-line parser."""
    parser = argparse.ArgumentParser(
        prog="vision-playground",
        description="Run reproducible computer vision experiments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "list",
        help="List registered experiments and their research questions.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run one experiment or the complete default suite.",
    )
    choices = [definition.experiment_id for definition in EXPERIMENTS]
    run_parser.add_argument(
        "experiment",
        choices=[*choices, "all"],
        help="Registered experiment identifier or 'all'.",
    )
    run_parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Root directory for generated artifacts.",
    )
    run_parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/oxford_pet_sample"),
        help="Labeled Oxford-IIIT Pet sample directory.",
    )
    return parser


def _print_outcome(outcome: ExperimentOutcome, output_dir: Path) -> None:
    print(f"Completed: {outcome.experiment}")
    print(f"Evaluations: {outcome.evaluations}")
    print(f"Metrics: {output_dir / outcome.metrics_path}")
    print(f"Visual: {output_dir / outcome.visual_artifact}")


def main(argv: Sequence[str] | None = None) -> int:
    """List or run experiments with stable default configurations."""
    args = build_parser().parse_args(argv)
    if args.command == "list":
        for definition in EXPERIMENTS:
            print(f"{definition.experiment_id}: {definition.title}")
            print(f"  {definition.question}")
        return 0

    if args.experiment == "all":
        outcomes = run_all_experiments(args.output, args.data)
        print(f"Completed experiments: {len(outcomes)}")
        print(f"Evaluations: {sum(item.evaluations for item in outcomes)}")
        print(f"Summary: {args.output / 'experiment_summary.csv'}")
        return 0

    outcome = run_experiment(args.experiment, args.output, args.data)
    _print_outcome(outcome, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
