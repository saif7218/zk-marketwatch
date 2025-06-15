import argparse
from orchestrator.main_flow import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Apon Family Mart Intelligence Pipeline")
    parser.add_argument('--csv', type=str, default="data/products1.csv", help="Path to products CSV (default: data/products1.csv)")
    args = parser.parse_args()
    run_pipeline(args.csv)
