"""Choose routes for three flights when the direct corridor is congested."""

import gurobipy as gp
from gurobipy import GRB


# These are example costs, not measured flight times. Change them to experiment.
cost = {
    "Alpha": {"Direct": 5, "Detour": 9},
    "Bravo": {"Direct": 6, "Detour": 10},
    "Charlie": {"Direct": 7, "Detour": 8},
}
capacity = {"Direct": 2, "Detour": 3}
routes = tuple(capacity)


def main() -> None:
    model = gp.Model("first_air_traffic_model")

    # x[flight, route] is 1 if that flight uses that route, and 0 otherwise.
    x = model.addVars(cost, routes, vtype=GRB.BINARY, name="choose")

    model.setObjective(
        gp.quicksum(cost[flight][route] * x[flight, route]
                    for flight in cost for route in routes),
        GRB.MINIMIZE,
    )

    for flight in cost:
        model.addConstr(
            gp.quicksum(x[flight, route] for route in routes) == 1,
            name=f"one_route_{flight}",
        )

    for route in routes:
        model.addConstr(
            gp.quicksum(x[flight, route] for flight in cost) <= capacity[route],
            name=f"capacity_{route}",
        )

    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f"No optimal plan found (status {model.Status})")

    print(f"\nMinimum total cost: {model.ObjVal:g}")
    for flight in cost:
        chosen = next(route for route in routes if x[flight, route].X > 0.5)
        print(f"{flight}: {chosen} (cost {cost[flight][chosen]})")


if __name__ == "__main__":
    main()
