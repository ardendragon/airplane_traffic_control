"""Generate and solve the four synthetic TFMP connection scenarios."""

import argparse
import csv
from pathlib import Path

from air_traffic_flow_management import main as solve_case
from tfmp_cases import CONTINUED_PERCENTS, FLIGHT_COUNT, generate_case, write_case


FIELDS = (
    "flights",
    "continued_percent",
    "lp_status",
    "lp_objective",
    "lp_solver_seconds",
    "lp_fractional_flights",
    "lp_noninteger_percent",
    "mip_status",
    "mip_objective",
    "mip_solver_seconds",
)


def run_cases(output_dir: Path, time_limit: float | None) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for continued_percent in CONTINUED_PERCENTS:
        directory = output_dir / f"tfmp_{FLIGHT_COUNT}_flights_{continued_percent}pct"
        write_case(directory, *generate_case(continued_percent))
        lp = solve_case(directory, relax=True, time_limit=time_limit, quiet=True)
        mip = solve_case(directory, relax=False, time_limit=time_limit, quiet=True)
        rows.append(
            {
                "flights": FLIGHT_COUNT,
                "continued_percent": continued_percent,
                "lp_status": lp["status"],
                "lp_objective": lp["objective"],
                "lp_solver_seconds": lp["solver_seconds"],
                "lp_fractional_flights": lp["fractional_flights"],
                "lp_noninteger_percent": lp["noninteger_percent"],
                "mip_status": mip["status"],
                "mip_objective": mip["objective"],
                "mip_solver_seconds": mip["solver_seconds"],
            }
        )
        print(
            f"{continued_percent}% connected: LP {lp['status']}, MIP {mip['status']}",
            flush=True,
        )
    return rows


def markdown_results(rows: list[dict]) -> str:
    lines = [
        "# Synthetic TFMP results",
        "",
        "Each case has 1,500 flights, 144 ten-minute periods, three airports, and three sectors. These are newly generated schedules.",
        "",
        "| Flights | Connected | LP objective | LP noninteger flights | LP time (s) | MIP objective | MIP time (s) | Status |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |",
    ]
    for row in rows:
        lp_objective = f"{row['lp_objective']:,.2f}" if row["lp_objective"] is not None else "—"
        mip_objective = f"{row['mip_objective']:,.2f}" if row["mip_objective"] is not None else "—"
        noninteger = (
            f"{row['lp_noninteger_percent']:.1f}%"
            if row["lp_noninteger_percent"] is not None
            else "—"
        )
        lines.append(
            f"| {row['flights']:,} | {row['continued_percent']}% | "
            f"{lp_objective} | {noninteger} | {row['lp_solver_seconds']:.2f} | "
            f"{mip_objective} | {row['mip_solver_seconds']:.2f} | "
            f"LP {row['lp_status']}; MIP {row['mip_status']} |"
        )
    lines.extend(
        [
            "",
            "Times are Gurobi solve times; they exclude CSV loading and Python model construction.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "generated_cases" / "TFMP",
    )
    parser.add_argument("--time-limit", type=float, help="Per-solve time limit in seconds")
    args = parser.parse_args()
    rows = run_cases(args.output_dir, args.time_limit)
    csv_path = args.output_dir / "tfmp_results.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    markdown_path = args.output_dir / "tfmp_results.md"
    markdown_path.write_text(markdown_results(rows))
    print(f"Wrote {csv_path} and {markdown_path}")


if __name__ == "__main__":
    main()
