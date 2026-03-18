"""CLI for plottwist."""
import sys, json, argparse
from .core import Plottwist

def main():
    parser = argparse.ArgumentParser(description="PlotTwist — Interactive AI Fiction. Choose-your-own-adventure stories with AI-generated narratives.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Plottwist()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.generate(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"plottwist v0.1.0 — PlotTwist — Interactive AI Fiction. Choose-your-own-adventure stories with AI-generated narratives.")

if __name__ == "__main__":
    main()
