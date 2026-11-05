"""
Script: scripts/generate_dashboard.py
Loads the held-out evaluation results and builds the interactive HTML dashboard.
"""

import json
import sys
from pathlib import Path

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.herm4ai.dashboard import generate_html_dashboard


def main():
    heldout_results_file = Path("results/heldout_results.json")
    if not heldout_results_file.exists():
        print(f"Error: {heldout_results_file} not found. Please run scripts/run_evaluation.py first.")
        sys.exit(1)

    with open(heldout_results_file, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    # Find the HERM4AI evaluation entry
    herm_res = next((r for r in all_results if r["system_name"] == "HERM4AI"), None)
    if not herm_res:
        print("Error: No HERM4AI results found in heldout_results.json")
        sys.exit(1)

    out_path = generate_html_dashboard(herm_res["case_details"], "results/observability_dashboard.html")
    print(f"Dashboard successfully generated -> {out_path}")


if __name__ == "__main__":
    main()
