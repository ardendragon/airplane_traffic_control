"""Generate synthetic ground-holding cases and load them into the model.

These cases match the sizes and constant capacities in Bertsimas and Stock
Patterson (1998), Tables I-II. The flight schedules are newly constructed;
they are not the unpublished flight-level data used in that paper.
"""

import argparse
import csv
import json
from collections import defaultdict, deque
from pathlib import Path


# (flight count, continued-flight percentage): (departure, arrival capacity)
CASE_SPECS = {
    (1000, 20): (32, 15),
    (1000, 40): (17, 10),
    (1000, 60): (20, 14),
    (1000, 80): (20, 20),
    (3000, 20): (20, 20),
    (3000, 40): (20, 20),
    (3000, 60): (20, 20),
    (3000, 80): (20, 20),
}

PERIODS = 64
FLIGHTS_PER_AIRPORT = 500
FLIGHT_TIME = 2
MAX_DELAY = 4
TURNAROUND = 1
GROUND_COST = 50
AIR_COST = 75


def generate_case(flight_count: int, continued_percent: int):
    """Return raw flight, connection, capacity, and metadata records.

    A known feasible schedule is constructed first. Scheduled departures are
    moved up to three periods earlier in four-period blocks to create peaks.
    Connections are selected only when that feasible schedule has enough
    turnaround time. The witness schedule is retained for validation only.
    """
    if (flight_count, continued_percent) not in CASE_SPECS:
        raise ValueError("Choose a flight count and continued share in CASE_SPECS")

    departure_capacity, arrival_capacity = CASE_SPECS[
        flight_count, continued_percent
    ]
    airport_count = flight_count // FLIGHTS_PER_AIRPORT
    airports = [f"A{i}" for i in range(airport_count)]
    flights = []

    for destination_index, destination in enumerate(airports):
        origin = airports[(destination_index - 1) % airport_count]
        for position in range(FLIGHTS_PER_AIRPORT):
            witness_departure = position // arrival_capacity
            scheduled_departure = witness_departure - witness_departure % 4
            flights.append(
                {
                    "flight_id": f"F{len(flights) + 1:05d}",
                    "origin": origin,
                    "destination": destination,
                    "scheduled_departure": scheduled_departure,
                    "scheduled_arrival": scheduled_departure + FLIGHT_TIME,
                    "witness_departure": witness_departure,
                    "witness_arrival": witness_departure + FLIGHT_TIME,
                    "ground_cost": GROUND_COST,
                    "air_cost": AIR_COST,
                    "max_delay": MAX_DELAY,
                }
            )

    arrivals = defaultdict(list)
    departures = defaultdict(list)
    for flight in flights:
        arrivals[flight["destination"]].append(flight)
        departures[flight["origin"]].append(flight)

    connections = []
    per_airport_target = flight_count * continued_percent // 100 // airport_count
    for airport in airports:
        incoming = sorted(
            arrivals[airport], key=lambda f: (f["witness_arrival"], f["flight_id"])
        )
        outgoing = sorted(
            departures[airport], key=lambda f: (f["witness_departure"], f["flight_id"])
        )
        available = deque()
        incoming_index = 0
        chosen = 0
        for successor in outgoing:
            while (
                incoming_index < len(incoming)
                and incoming[incoming_index]["witness_arrival"] + TURNAROUND
                <= successor["witness_departure"]
            ):
                available.append(incoming[incoming_index])
                incoming_index += 1
            if available and chosen < per_airport_target:
                predecessor = available.popleft()
                connections.append(
                    {
                        "predecessor": predecessor["flight_id"],
                        "successor": successor["flight_id"],
                        "turnaround": TURNAROUND,
                    }
                )
                chosen += 1
        if chosen != per_airport_target:
            raise ValueError(f"Could not create enough connections at {airport}")

    capacities = [
        {
            "airport": airport,
            "time": t,
            "departure_capacity": departure_capacity,
            "arrival_capacity": arrival_capacity,
        }
        for airport in airports
        for t in range(PERIODS)
    ]
    metadata = {
        "synthetic": True,
        "flight_count": flight_count,
        "airport_count": airport_count,
        "flights_per_arrival_airport": FLIGHTS_PER_AIRPORT,
        "continued_percent": continued_percent,
        "period_count": PERIODS,
        "minutes_per_period": 15,
        "flight_time_periods": FLIGHT_TIME,
        "max_delay_periods": MAX_DELAY,
        "departure_capacity_per_period": departure_capacity,
        "arrival_capacity_per_period": arrival_capacity,
        "ground_cost_per_period": GROUND_COST,
        "air_cost_per_period": AIR_COST,
        "source": "Bertsimas and Stock Patterson (1998), Tables I-II: scenario settings only",
        "note": "Schedules and connections are synthetic; published outcomes are not expected.",
    }
    validate_case(flights, connections, capacities, metadata)
    return flights, connections, capacities, metadata


def validate_case(flights, connections, capacities, metadata):
    """Check the counts, capacity-feasible witness, and connection schedule."""
    if len(flights) != metadata["flight_count"]:
        raise ValueError("Wrong flight count")
    expected_links = metadata["flight_count"] * metadata["continued_percent"] // 100
    if len(connections) != expected_links:
        raise ValueError("Wrong continuation count")

    by_id = {flight["flight_id"]: flight for flight in flights}
    airport_capacity = {
        (row["airport"], row["time"]): row for row in capacities
    }
    departures = defaultdict(int)
    arrivals = defaultdict(int)
    arrival_counts = defaultdict(int)
    for flight in flights:
        arrival_counts[flight["destination"]] += 1
        delay = flight["witness_departure"] - flight["scheduled_departure"]
        if not 0 <= delay <= flight["max_delay"]:
            raise ValueError("Witness departure is outside its feasible window")
        if flight["witness_arrival"] - flight["scheduled_arrival"] != delay:
            raise ValueError("Witness arrival does not preserve flight time")
        if flight["scheduled_arrival"] + flight["max_delay"] >= metadata["period_count"]:
            raise ValueError("Arrival window extends past the horizon")
        departures[(flight["origin"], flight["witness_departure"])] += 1
        arrivals[(flight["destination"], flight["witness_arrival"])] += 1

    if any(count != FLIGHTS_PER_AIRPORT for count in arrival_counts.values()):
        raise ValueError("Each airport must receive 500 flights")
    for key, count in departures.items():
        if count > airport_capacity[key]["departure_capacity"]:
            raise ValueError(f"Witness exceeds departure capacity at {key}")
    for key, count in arrivals.items():
        if count > airport_capacity[key]["arrival_capacity"]:
            raise ValueError(f"Witness exceeds arrival capacity at {key}")

    predecessors = set()
    successors = set()
    for link in connections:
        predecessor = by_id[link["predecessor"]]
        successor = by_id[link["successor"]]
        if link["predecessor"] in predecessors or link["successor"] in successors:
            raise ValueError("A flight has multiple immediate connections")
        predecessors.add(link["predecessor"])
        successors.add(link["successor"])
        if predecessor["destination"] != successor["origin"]:
            raise ValueError("Connected flights use different airports")
        if (
            predecessor["witness_arrival"] + link["turnaround"]
            > successor["witness_departure"]
        ):
            raise ValueError("Witness violates turnaround time")


def write_case(directory: Path, flights, connections, capacities, metadata):
    directory.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("flights.csv", flights),
        ("connections.csv", connections),
        ("capacities.csv", capacities),
    ):
        with (directory / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    with (directory / "scenario.json").open("w") as stream:
        json.dump(metadata, stream, indent=2)
        stream.write("\n")


def load_case(directory: Path):
    """Convert the compact raw files to the model's F, J, K, L, T dictionaries."""
    directory = Path(directory)
    with (directory / "scenario.json").open() as stream:
        metadata = json.load(stream)

    def rows(filename):
        with (directory / filename).open(newline="") as stream:
            return list(csv.DictReader(stream))

    flight_rows = rows("flights.csv")
    connection_rows = rows("connections.csv")
    capacity_rows = rows("capacities.csv")
    T = {t: None for t in range(metadata["period_count"])}
    J = {}
    K = {}
    for row in capacity_rows:
        airport = row["airport"]
        t = int(row["time"])
        K.setdefault(airport, {"D": {}, "A": {}})
        K[airport]["D"][t] = int(row["departure_capacity"])
        K[airport]["A"][t] = int(row["arrival_capacity"])

    F = {}
    for row in flight_rows:
        f = row["flight_id"]
        origin, destination = row["origin"], row["destination"]
        departure, arrival = int(row["scheduled_departure"]), int(row["scheduled_arrival"])
        max_delay = int(row["max_delay"])
        F[f] = {
            "num": 2,
            "path": [origin, destination],
            "next": {origin: destination},
            "a1": origin,
            "a2": destination,
            "dep": departure,
            "arr": arrival,
            "cg": int(row["ground_cost"]),
            "cf": int(row["air_cost"]),
            "l": {origin: metadata["flight_time_periods"]},
            "T": {
                origin: tuple(range(departure, departure + max_delay + 1)),
                destination: tuple(range(arrival, arrival + max_delay + 1)),
            },
        }

    L = []
    for row in connection_rows:
        predecessor, successor = row["predecessor"], row["successor"]
        F[predecessor]["s"] = int(row["turnaround"])
        L.append((predecessor, successor))
    return F, J, K, tuple(L), T


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "generated_cases")
    parser.add_argument("--flights", type=int, choices=(1000, 3000))
    parser.add_argument("--continued", type=int, choices=(20, 40, 60, 80))
    args = parser.parse_args()
    if (args.flights is None) != (args.continued is None):
        parser.error("Provide both --flights and --continued, or neither for all cases")
    specs = (
        [(args.flights, args.continued)]
        if args.flights is not None
        else CASE_SPECS
    )
    for flight_count, continued_percent in specs:
        case = generate_case(flight_count, continued_percent)
        directory = args.output_dir / f"{flight_count}_flights_{continued_percent}pct"
        write_case(directory, *case)
        print(f"Wrote {directory}")


if __name__ == "__main__":
    main()
