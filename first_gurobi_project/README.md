# First Gurobi project: choose aircraft routes

Three flights each need one route. The direct corridor can take only two flights. Gurobi chooses the lowest-cost combination that respects this capacity.

From the `Airplane Traffic Control` folder, run:

```bash
source .venv/bin/activate
python first_gurobi_project/route_planner.py
```

The example should choose **Direct** for Alpha and Bravo, **Detour** for Charlie, and report a total cost of **19**.

The model has one binary decision variable `x[flight, route]` for each flight-route pair. It minimizes the sum of selected route costs, with two rules: each flight chooses exactly one route, and each route's number of flights cannot exceed its capacity. The numbers are made up for learning; this is not an operational flight plan.

To experiment, change `capacity["Direct"]` in `route_planner.py` from `2` to `1` and rerun. Then change Charlie's detour cost from `8` to `12` and see which flight is rerouted. A natural next extension is to add departure time slots and a capacity for each route in each slot.

See Gurobi's [Python model reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html) for `addVars`, `addConstr`, and `optimize`.
