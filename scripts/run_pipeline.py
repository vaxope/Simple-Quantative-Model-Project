import argparse
from pathlib import Path
import yaml
from src.pipeline import run_full_pipeline

def main():
    parser = argparse.ArgumentParser(description="Run the research pipeline end to end")
    parser.add_argument("--config", required=True, help = "Path to a config.yaml")
    parser.add_argument(
        "--out-dir",
        default="data/runs",
        help="Directory to write predictions/backtest_results/metrics into"
    )
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    run_name = config["output"]["run_name"]
    print(f"Running pipeline: {run_name}")
    print(f"  tickers: {config['data']['tickers']}")
    print(f"  model:   {config['model']['name']}")

    results = run_full_pipeline(config)

    out_dir = Path(args.out_dir) / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    results["predictions"].to_parquet(out_dir / "predictions.parquet")
    results["backtest_results"].to_parquet(out_dir / "backtest_results.parquet")
    results["metrics"].to_csv(out_dir / "metrics.csv")

    with open(out_dir / "config.yaml", "w") as f:
        yaml.safe_dump(config, f)

    print(f"\nSaved outputs to {out_dir}/")
    print("\nBacktest metrics:")
    print(results["metrics"].to_string())


if __name__ == "__main__":
    main()
