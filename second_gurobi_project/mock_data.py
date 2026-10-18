"""Small feasible instance for exercising the air traffic flow model."""

# Iterating over these dictionaries yields the flight, sector, airport, and time IDs.
T = {t: None for t in range(5)}

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
        "F": {"F1": "B", "F2": "B"},
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
