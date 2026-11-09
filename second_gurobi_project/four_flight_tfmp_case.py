"""Four-flight, two-airport TFMP example over periods 0 through 8.

The three sectors form one route in each direction. Sector travel time is a
minimum of two periods; additional time in a sector is airborne delay.
"""

T = {t: None for t in range(9)}

K = {
    airport: {
        "D": {t: 2 for t in T},
        "A": {t: 2 for t in T},
    }
    for airport in ("K0", "K1")
}

J = {sector: {"cap": {t: 2 for t in T}, "F": {}} for sector in ("J0", "J1", "J2")}

F = {}
for flight_id, path in (
    ("F0", ("K0", "J0", "J1", "J2", "K1")),
    ("F1", ("K0", "J0", "J1", "J2", "K1")),
    ("F2", ("K1", "J2", "J1", "J0", "K0")),
    ("F3", ("K1", "J2", "J1", "J0", "K0")),
):
    origin, first, middle, last, destination = path
    next_element = dict(zip(path, path[1:]))
    F[flight_id] = {
        "num": len(path),
        "path": path,
        "next": next_element,
        "a1": origin,
        "a2": destination,
        "dep": 0,
        "arr": 6,
        # Departures are fixed at zero, so ground delay is impossible.
        # A literal infinite objective coefficient is unnecessary and invalid.
        "cg": 0,
        "cf": 1,
        "l": {origin: 0, first: 2, middle: 2, last: 2},
        "max_air_delay": 2,
        "T": {
            origin: (0,),
            first: (0,),
            middle: (2, 3, 4),
            last: (4, 5, 6),
            destination: (6, 7, 8),
        },
    }
    for sector in (first, middle, last):
        J[sector]["F"][flight_id] = next_element[sector]

# No aircraft is reused for another flight in this example.
L = ()
