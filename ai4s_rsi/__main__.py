"""Command-line entry point for the synthetic workflow."""

import argparse
import json
from pathlib import Path

from .pipeline import load_config, run, save, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="AI4S-RSI synthetic workflow demo")
    commands = parser.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run", help="Run the synthetic demonstration")
    execute.add_argument("--config", type=Path, default=Path("configs/demo.json"))
    execute.add_argument("--output", type=Path, default=Path("artifacts/demo"))
    inspect = commands.add_parser("inspect", help="Inspect an existing demonstration run")
    inspect.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        config, task = load_config(args.config)
        record = run(config, task)
        save(record, args.output)
        for item in record["rounds"]:
            print(
                f"Round {item['round']}: propose {len(item['proposals'])} "
                f"-> evaluate -> select {len(item['selected'])} -> feedback"
            )
        print(f"Synthetic demonstration saved to {args.output}")
        print(summary(record))
    else:
        record = json.loads((args.directory / "run.json").read_text(encoding="utf-8"))
        print(summary(record))


if __name__ == "__main__":
    main()
