"""Generate four synthetic traffic-flow cases with airports and sectors.

The four cases share 1,500 flight schedules and differ in the percentage of
connected flights. The schedules are constructed, not taken from a paper.
"""

import argparse
import csv
import json
from collections import defaultdict, deque
from pathlib import Path


PERIOD_COUNT = 144  # 24 hours in 10-minute periods
MINUTES_PER_PERIOD = 10
FLIGHTS_PER_AIRPORT = 500
FLIGHT_COUNT = 3 * FLIGHTS_PER_AIRPORT
AIRPORT_CAPACITY = 30
SECTOR_CAPACITY = 30
SECTOR_TRAVEL_TIME = 8
MAX_GROUND_DELAY = 4  # Carried over from the ground-holding examples
MAX_AIR_DELAY = 2
MIN_TURNAROUND = 3
GROUND_COST = 50
AIR_COST = 75
CONTINUED_PERCENTS = (20, 40, 60, 80)
AIRPORTS = ("A0", "A1", "A2")
SECTOR_ENDPOINTS = {
    "J0": ("A0", "A1"),
    "J1": ("A0", "A2"),
    "J2": ("A1", "A2"),
}


def generate_case(continued_percent: int):
    """Build tight aircraft chains, then schedule their flights.

    First assign capacity-feasible flight slots, then connect flights whose
    witness arrival and next departure are exactly one turnaround apart. All
    four cases use the same full-chain timetable; lower shares retain nested
    subsets of its links.
    """
    if continued_percent not in CONTINUED_PERCENTS:
        raise ValueError(f"Continued share must be one of {CONTINUED_PERCENTS}")

    flights = []
    for sector, endpoints in SECTOR_ENDPOINTS.items():
        for position in range(500):
            # Thirty sector entries per eight-period wave keep occupancy <= 30.
            wave = position // 30
            witness_departure = wave * SECTOR_TRAVEL_TIME + (position % 30) % 8
            origin, destination = endpoints if position % 2 == 0 else endpoints[::-1]
            flights.append(
                {
                    "flight_id": f"F{len(flights) + 1:05d}",
                    "origin": origin,
                    "sector": sector,
                    "destination": destination,
                    "witness_departure": witness_departure,
                    "witness_sector_entry": witness_departure,
                    "witness_arrival": witness_departure + SECTOR_TRAVEL_TIME,
                    "ground_cost": GROUND_COST,
                    "air_cost": AIR_COST,
                    "max_ground_delay": MAX_GROUND_DELAY,
                    "max_air_delay": MAX_AIR_DELAY,
                }
            )

    arriving_at = defaultdict(deque)
    departing = defaultdict(list)
    for flight in flights:
        arriving_at[flight["destination"], flight["witness_arrival"]].append(flight)
        departing[flight["origin"]].append(flight)

    # Build the 80% aircraft chains before choosing scheduled times. Each link
    # has exactly the three-period minimum turnaround in the witness schedule.
    full_connections = []
    links_by_airport = {}
    for airport in AIRPORTS:
        outgoing = sorted(departing[airport], key=lambda f: (f["witness_departure"], f["flight_id"]))
        airport_links = []
        for successor in outgoing:
            candidates = arriving_at[airport, successor["witness_departure"] - MIN_TURNAROUND]
            if candidates and len(airport_links) < FLIGHTS_PER_AIRPORT * max(CONTINUED_PERCENTS) // 100:
                predecessor = candidates.popleft()
                airport_links.append(
                    {
                        "predecessor": predecessor["flight_id"],
                        "successor": successor["flight_id"],
                        "turnaround": MIN_TURNAROUND,
                    }
                )
        if len(airport_links) != FLIGHTS_PER_AIRPORT * max(CONTINUED_PERCENTS) // 100:
            raise ValueError(f"Not enough feasible aircraft connections at {airport}")
        links_by_airport[airport] = airport_links
        full_connections.extend(airport_links)

    successor_of = {link["predecessor"]: link["successor"] for link in full_connections}
    has_predecessor = {link["successor"] for link in full_connections}
    by_id = {flight["flight_id"]: flight for flight in flights}
    roots = sorted(
        (flight for flight in flights if flight["flight_id"] not in has_predecessor),
        key=lambda flight: (flight["witness_departure"], flight["flight_id"]),
    )
    for index, root in enumerate(roots):
        # A common shift along the chain gives every link zero scheduled slack.
        # Alternating shifts create demand peaks while the witness remains feasible.
        shift = MAX_GROUND_DELAY if root["witness_departure"] >= MAX_GROUND_DELAY and index % 2 == 0 else 0
        flight = root
        while flight is not None:
            flight["scheduled_departure"] = flight["witness_departure"] - shift
            flight["scheduled_arrival"] = flight["scheduled_departure"] + SECTOR_TRAVEL_TIME
            flight = by_id.get(successor_of.get(flight["flight_id"]))

    connections = []
    target_per_airport = FLIGHTS_PER_AIRPORT * continued_percent // 100
    for airport in AIRPORTS:
        # Start with the earlier aircraft rotations, whose delays can flow
        # through more later legs. Higher shares add links to this same set.
        nested_order = sorted(
            links_by_airport[airport],
            key=lambda link: (
                by_id[link["predecessor"]]["witness_departure"],
                link["predecessor"],
            ),
        )
        connections.extend(nested_order[:target_per_airport])

    capacities = [
        {
            "airport": airport,
            "time": t,
            "departure_capacity": AIRPORT_CAPACITY,
            "arrival_capacity": AIRPORT_CAPACITY,
        }
        for airport in AIRPORTS
        for t in range(PERIOD_COUNT)
    ]
    sectors = [
        {
            "sector": sector,
            "time": t,
            "capacity": SECTOR_CAPACITY,
            "travel_time": SECTOR_TRAVEL_TIME,
        }
        for sector in SECTOR_ENDPOINTS
        for t in range(PERIOD_COUNT)
    ]
    metadata = {
        "kind": "tfmp",
        "synthetic": True,
        "flight_count": FLIGHT_COUNT,
        "arrivals_per_airport": FLIGHTS_PER_AIRPORT,
        "continued_percent": continued_percent,
        "period_count": PERIOD_COUNT,
        "minutes_per_period": MINUTES_PER_PERIOD,
        "airport_capacity": AIRPORT_CAPACITY,
        "sector_capacity": SECTOR_CAPACITY,
        "sector_travel_time": SECTOR_TRAVEL_TIME,
        "max_ground_delay": MAX_GROUND_DELAY,
        "max_air_delay": MAX_AIR_DELAY,
        "min_turnaround": MIN_TURNAROUND,
        "ground_cost": GROUND_COST,
        "air_cost": AIR_COST,
        "origin_to_sector_time": 0,
        "note": "Chains are built before scheduled times; each link has zero scheduled slack. Lower shares use earlier rotations. The witness has ground delay only.",
    }
    validate_case(flights, connections, capacities, sectors, metadata)
    return flights, connections, capacities, sectors, metadata


def validate_case(flights, connections, capacities, sectors, metadata):
    """Check all counts, routes, time windows, links, and witness capacities."""
    if len(flights) != FLIGHT_COUNT:
        raise ValueError("Wrong flight count")
    if len(connections) != FLIGHT_COUNT * metadata["continued_percent"] // 100:
        raise ValueError("Wrong continuation count")

    airport_caps = {(r["airport"], r["time"]): r for r in capacities}
    sector_caps = {(r["sector"], r["time"]): r for r in sectors}
    by_id = {f["flight_id"]: f for f in flights}
    arrivals_per_airport = defaultdict(int)
    departures_per_airport = defaultdict(int)
    airport_departures = defaultdict(int)
    airport_arrivals = defaultdict(int)
    sector_occupancy = defaultdict(int)
    for flight in flights:
        origin, sector, destination = flight["origin"], flight["sector"], flight["destination"]
        if (origin, destination) not in (
            SECTOR_ENDPOINTS[sector], SECTOR_ENDPOINTS[sector][::-1]
        ):
            raise ValueError(f"Invalid route for {flight['flight_id']}")
        arrivals_per_airport[destination] += 1
        departures_per_airport[origin] += 1
        departure = flight["witness_departure"]
        arrival = flight["witness_arrival"]
        if not 0 <= departure - flight["scheduled_departure"] <= MAX_GROUND_DELAY:
            raise ValueError("Witness exceeds ground delay bound")
        if flight["witness_sector_entry"] != departure or arrival - departure != SECTOR_TRAVEL_TIME:
            raise ValueError("Witness flight timing is inconsistent")
        if not 0 <= arrival < PERIOD_COUNT:
            raise ValueError("Witness arrival is outside the horizon")
        airport_departures[(origin, departure)] += 1
        airport_arrivals[(destination, arrival)] += 1
        for t in range(departure, arrival):
            sector_occupancy[(sector, t)] += 1

    if any(arrivals_per_airport[a] != FLIGHTS_PER_AIRPORT for a in AIRPORTS):
        raise ValueError("Each airport must receive 500 flights")
    if any(departures_per_airport[a] != FLIGHTS_PER_AIRPORT for a in AIRPORTS):
        raise ValueError("Each airport must originate 500 flights")
    for key, count in airport_departures.items():
        if count > airport_caps[key]["departure_capacity"]:
            raise ValueError(f"Departure capacity exceeded at {key}")
    for key, count in airport_arrivals.items():
        if count > airport_caps[key]["arrival_capacity"]:
            raise ValueError(f"Arrival capacity exceeded at {key}")
    for key, count in sector_occupancy.items():
        if count > sector_caps[key]["capacity"]:
            raise ValueError(f"Sector capacity exceeded at {key}")

    used_predecessors = set()
    used_successors = set()
    for link in connections:
        previous = by_id[link["predecessor"]]
        following = by_id[link["successor"]]
        if link["predecessor"] in used_predecessors or link["successor"] in used_successors:
            raise ValueError("A flight has multiple immediate connections")
        used_predecessors.add(link["predecessor"])
        used_successors.add(link["successor"])
        if previous["destination"] != following["origin"]:
            raise ValueError("Connected flights use different airports")
        for prefix in ("scheduled", "witness"):
            if previous[f"{prefix}_arrival"] + MIN_TURNAROUND != following[f"{prefix}_departure"]:
                raise ValueError("Connection does not have an exact turnaround")


def write_case(directory: Path, flights, connections, capacities, sectors, metadata):
    directory.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("flights.csv", flights),
        ("connections.csv", connections),
        ("capacities.csv", capacities),
        ("sectors.csv", sectors),
    ):
        with (directory / filename).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    with (directory / "scenario.json").open("w") as stream:
        json.dump(metadata, stream, indent=2)
        stream.write("\n")


def load_case(directory: Path):
    """Load a TFMP case into the existing model's F, J, K, L, T structures."""
    directory = Path(directory)
    with (directory / "scenario.json").open() as stream:
        metadata = json.load(stream)
    if metadata.get("kind") != "tfmp":
        raise ValueError(f"{directory} is not a TFMP case")

    def rows(filename):
        with (directory / filename).open(newline="") as stream:
            return list(csv.DictReader(stream))

    T = {t: None for t in range(metadata["period_count"])}
    K = {}
    for row in rows("capacities.csv"):
        airport, t = row["airport"], int(row["time"])
        K.setdefault(airport, {"D": {}, "A": {}})
        K[airport]["D"][t] = int(row["departure_capacity"])
        K[airport]["A"][t] = int(row["arrival_capacity"])

    J = {}
    for row in rows("sectors.csv"):
        sector, t = row["sector"], int(row["time"])
        J.setdefault(sector, {"cap": {}, "F": {}, "travel_time": int(row["travel_time"])})
        J[sector]["cap"][t] = int(row["capacity"])

    F = {}
    for row in rows("flights.csv"):
        flight_id = row["flight_id"]
        origin, sector, destination = row["origin"], row["sector"], row["destination"]
        departure = int(row["scheduled_departure"])
        arrival = int(row["scheduled_arrival"])
        ground_limit = int(row["max_ground_delay"])
        air_limit = int(row["max_air_delay"])
        horizon = metadata["period_count"] - 1
        F[flight_id] = {
            "num": 3,
            "path": [origin, sector, destination],
            "next": {origin: sector, sector: destination},
            "a1": origin,
            "a2": destination,
            "dep": departure,
            "arr": arrival,
            "cg": int(row["ground_cost"]),
            "cf": int(row["air_cost"]),
            "l": {origin: metadata["origin_to_sector_time"], sector: J[sector]["travel_time"]},
            "max_air_delay": air_limit,
            "T": {
                origin: tuple(range(departure, min(horizon, departure + ground_limit) + 1)),
                sector: tuple(range(departure, min(horizon, departure + ground_limit + air_limit) + 1)),
                destination: tuple(range(arrival, min(horizon, arrival + ground_limit + air_limit) + 1)),
            },
        }
        J[sector]["F"][flight_id] = destination

    L = []
    for row in rows("connections.csv"):
        predecessor, successor = row["predecessor"], row["successor"]
        F[predecessor]["s"] = int(row["turnaround"])
        L.append((predecessor, successor))
    return F, J, K, tuple(L), T


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "generated_cases" / "TFMP")
    parser.add_argument("--continued", type=int, choices=CONTINUED_PERCENTS)
    args = parser.parse_args()
    percentages = (args.continued,) if args.continued is not None else CONTINUED_PERCENTS
    for continued_percent in percentages:
        case = generate_case(continued_percent)
        directory = args.output_dir / f"tfmp_{FLIGHT_COUNT}_flights_{continued_percent}pct"
        write_case(directory, *case)
        print(f"Wrote {directory}")


if __name__ == "__main__":
    main()
