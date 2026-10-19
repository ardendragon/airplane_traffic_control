"""Run synthetic cases at the capacity levels in Tables V and VI.

The published tables use different flight-level data. This script copies their
capacity *experiments*, not their reported objective values or feasibility.
"""

import argparse
import csv
from pathlib import Path

from air_traffic_flow_management import main as solve
from ground_holding_cases import CASE_SPECS, generate_case, write_case


# Bertsimas and Stock Patterson (1998), Tables V and VI.
CAPACITY_SWEEPS = {
    (1000, 20): ((32, 17), (32, 16), (32, 15), (32, 14)),
    (1000, 40): ((18, 12), (18, 10), (17, 10), (16, 10)),
    (1000, 60): ((20, 18), (20, 15), (20, 14), (20, 13)),
    (1000, 80): ((30, 30), (20, 20), (19, 19)),
    (3000, 20): ((30, 30), (20, 20), (19, 19)),
    (3000, 40): ((30, 30), (20, 20), (19, 19)),
    (3000, 60): ((30, 30), (20, 20), (19, 19)),
    (3000, 80): ((30, 30), (20, 20), (19, 19)),
}

FIELDS = (
    "flights",
    "continued_percent",
    "departure_capacity",
    "arrival_capacity",
    "status",
    "objective",
    "solver_seconds",
    "fractional_flights",
    "noninteger_percent",
)


def case_path(root: Path, flights: int, continued_percent: int) -> Path:
    directory = root / f"{flights}_flights_{continued_percent}pct"
    if not directory.exists():
        write_case(directory, *generate_case(flights, continued_percent))
    return directory


def run_cases(root: Path, baseline_only: bool, time_limit: float | None) -> list[dict]:
    rows = []
    for (flights, continued_percent), baseline in CASE_SPECS.items():
        directory = case_path(root, flights, continued_percent)
        capacity_pairs = (
            (baseline,) if baseline_only else CAPACITY_SWEEPS[flights, continued_percent]
        )
        for departure_capacity, arrival_capacity in capacity_pairs:
            result = solve(
                directory,
                relax=True,
                time_limit=time_limit,
                departure_capacity=departure_capacity,
                arrival_capacity=arrival_capacity,
                quiet=True,
            )
            row = {
                "flights": flights,
                "continued_percent": continued_percent,
                "departure_capacity": departure_capacity,
                "arrival_capacity": arrival_capacity,
                **result,
            }
            rows.append(row)
            print(
                f"{flights:4d} flights, {continued_percent:2d}% continued, "
                f"{departure_capacity:2d}/{arrival_capacity:2d} capacity: "
                f"{result['status']} ({result['solver_seconds']:.2f}s)",
                flush=True,
            )
    return rows


def markdown_table(rows: list[dict], flights: int) -> str:
    lines = [
        f"## {'Table V' if flights == 1000 else 'Table VI'} style: {flights:,} flights",
        "",
        "| Flights | Continued | Dep. capacity | Arr. capacity | LP objective | Solver time (s) | Noninteger flights | Status |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |",
    ]
    for row in rows:
        if row["flights"] != flights:
            continue
        objective = (
            f"{row['objective']:,.2f}"
            if row["objective"] is not None
            else "inf" if row["status"] == "INFEASIBLE" else "—"
        )
        noninteger = (
            f"{row['noninteger_percent']:.1f}%"
            if row["noninteger_percent"] is not None
            else "—"
        )
        lines.append(
            f"| {row['flights']:,} | {row['continued_percent']}% | "
            f"{row['departure_capacity']} | {row['arrival_capacity']} | "
            f"{objective} | {row['solver_seconds']:.2f} | "
            f"{noninteger} | {row['status']} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case-root",
        type=Path,
        default=Path(__file__).parent / "generated_cases",
        help="Directory holding the eight generated cases",
    )
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help="Run only the eight capacity pairs from Tables I and II",
    )
    parser.add_argument("--time-limit", type=float, help="Per-solve limit in seconds")
    args = parser.parse_args()

    rows = run_cases(args.case_root, args.baseline_only, args.time_limit)
    output_prefix = args.case_root / (
        "baseline_results" if args.baseline_only else "table_v_vi_results"
    )
    csv_path = output_prefix.with_suffix(".csv")
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    markdown = "\n\n".join(
        [
            "# Synthetic ground-holding LP results",
            "These are new synthetic instances. Capacity levels follow the 1998 tables; objectives, feasibility, and fractional-flight percentages need not match the paper.",
            markdown_table(rows, 1000),
            markdown_table(rows, 3000),
        ]
    ) + "\n"
    markdown_path = output_prefix.with_suffix(".md")
    markdown_path.write_text(markdown)
    print(f"\nWrote {csv_path} and {markdown_path}")


if __name__ == "__main__":
    main()
