"""Small feasible instance for exercising the air traffic flow model."""

# Iterating over these dictionaries yields the flight, sector, airport, and time IDs.
T = {t: None for t in range(8)}

K = {
    "A": {
        "D": {t: 1 for t in T},
        "A": {t: 1 for t in T},
    },
    "B": {
        "D": {t: 1 for t in T},
        "A": {t: 1 for t in T},
    },
}

J = {
    "S": {
        "cap": {t: 1 for t in T},
        "F": {"F1": "B", "F2": "B", "F3": "A"},
    },
}

F = {
    flight_id: {
        "num": 3,
        "path": ["A", "S", "B"],
        "next": {"A": "S", "S": "B"},
        "a1": "A",
        "a2": "B",
        "dep": 0,
        "arr": 2,
        "cg": 1,
        "cf": 3,
        "l": {"A": 1, "S": 1},
        "T": {
            "A": (0, 1, 2),
            "S": (1, 2, 3),
            "B": (2, 3, 4),
        },
    }
    for flight_id in ("F1", "F2")
}

# F1's aircraft needs one period at B before it can operate F3.
F["F1"]["s"] = 1
# Make delaying F2 more costly, so the connection affects the optimal plan.
F["F2"]["cg"] = 4
F["F3"] = {
    "num": 3,
    "path": ["B", "S", "A"],
    "next": {"B": "S", "S": "A"},
    "a1": "B",
    "a2": "A",
    "dep": 3,
    "arr": 5,
    "cg": 1,
    "cf": 3,
    "l": {"B": 1, "S": 1},
    "T": {
        "B": (3, 4, 5),
        "S": (4, 5, 6),
        "A": (5, 6, 7),
    },
}

# (preceding flight, following flight) on the same aircraft.
L = (("F1", "F3"),)
