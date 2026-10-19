# Second Gurobi Project: Basic Airplane Variables and Constraints

## Synthetic ground-holding test cases

`ground_holding_cases.py` generates the eight cases in the published scenario
table: 1,000 flights at 20%, 40%, 60%, or 80% continuation (with capacities
32/15, 17/10, 20/14, and 20/20), and 3,000 flights at the same shares (all
with capacities 20/20). Each airport receives 500 flights over 64 fifteen-minute
periods. The generator uses a maximum delay of four periods and a one-period
turnaround. It constructs a capacity-feasible schedule before assigning the
requested number of aircraft connections.

The flight times, schedules, airport assignments, and connections are **synthetic**.
The table does not include the original flight-level data, so solving these cases
will not reproduce the paper's objective values or its reported percentages of
noninteger flights. The generator uses illustrative costs of 50 per ground-delay
period and 75 per air-delay period.

Generate all cases, or one case, from the repository root:

```bash
python second_gurobi_project/ground_holding_cases.py
python second_gurobi_project/ground_holding_cases.py --flights 1000 --continued 40
```

Each case directory contains `flights.csv` (one row per flight),
`connections.csv` (predecessor, successor, turnaround), `capacities.csv`
(one row per airport and period), and `scenario.json` (case metadata).
`ground_holding_cases.load_case()` converts those files to the model's
`F`, `J`, `K`, `L`, and `T` structures. The example cases have no en-route
sectors, so `J` is empty.

Run a generated case as a binary program, or use `--relax` for the LP relaxation:

```bash
source .venv/bin/activate
python second_gurobi_project/air_traffic_flow_management.py --case-dir second_gurobi_project/generated_cases/1000_flights_40pct --relax
```

The LP command reports the number of flights with at least one fractional
cumulative decision variable. For your own raw input, these three CSV tables
and one metadata file are preferable to storing one row for every
flight/airport/time combination: the loader creates feasible-time indices in
memory, and Gurobi creates variables only for those indices.

To run the capacity sweeps from Tables V and VI of Bertsimas and Stock
Patterson (1998), use:

```bash
python second_gurobi_project/run_ground_holding_cases.py
```

The runner generates any missing synthetic cases, solves the LP relaxation at
each of the 27 capacity combinations, and writes `table_v_vi_results.csv` and
`table_v_vi_results.md` under `second_gurobi_project/generated_cases/`.
Use `--baseline-only` for the eight capacity pairs from Tables I and II, or
`--time-limit 60` for a per-solve limit. `solver_seconds` measures Gurobi solve
time, excluding Python model construction and CSV loading. These numbers are
not comparable to the paper's CPU times on its hardware. The current generator
uses one period of minimum turnaround, which does not ensure the one period of
scheduled slack used in the 1994 experiment.

## Small mock case and model notes

run: 
```bash
source .venv/bin/activate
python second_gurobi_project/air_traffic_flow_management.py
```

Without `--case-dir`, the model imports a three-flight example from `mock_data.py`.




Beginning Variables:
set of flights
F = {
	"name": {
		num: number of flights in path
		path: ["name", "name", ...] the ith sector in flight path(or the 	   airport if i=0 or N) is the ith element in this list
		next: a mapping between a input sector and the next sector after it
		a1: path[0]
		a2: path[-1]
		dep: scheduled departure time
		arr: scheduled arrival time
		cg: cost of holding this flight on ground for one time
		cf: cost of holding this flight in air for one time
		l(j): time for flight to travel through sector j// use lambda notation
		T(j): times for flight to arrive at sector j // same here
		not this rn:
		s: turnaround time of an airplane after flight f
	}
}

set of sectors
J = {
	"name": {
		cap[t]: capacity of sector j at time t
		T(f): set of feasible times for flight F to arrive at this sector
		F: dictionary of flights that go into j mapped to the next sector flight goes to
	}
}

set of airports
K = {
	"name": {
		D(t) : departure capacity of airport at time t
		#maybe write as a list so:
		D: [3, 4, 3, 4,3 ] and so on
		A(t) : arrival capacity of airport at time t
		#same thing
}

not this rn 
L = {
	some f': f f' is continued by f
}


T = for i in range(start_time, end_time)


decision variables:

w = model.addVars(F, J, T, vtype=GRB.BINARY, name="choose") airplane f arrives at sector j *by* time t




define function: u
u(F, J, T):
return w[F, J, T] - w[F, J, T - 1]

time wasted on ground
def g(f):
return gp.quicksum(
t * u(f, f.path[0], t)
for t in range(f.T[f.a1][0], f.T[f.a1][-1] + 1)
) - f.dep

time wasted in the air
def a(f):
return gp.quicksum(
t * u(f, f.path[-1], t)
for t in range(f.T[f.a2][0], f.T[f.a2][-1] + 1)
) - f.arr - g(f)


Objective Function
model.setObjective(
    gp.quicksum(
    f.cg * g(f) + f.cf * a(f)
    for f in F
    ),
    GRB.MINIMIZE,
)



for t in T:
	for k in K:
	(2)
		model.addconstr(
			gp.quicksum(
				u(f, k, t)
				for f in filter(lambda: x: x.a1 == k, F)
			) <= k.D[t]
		)
	(3)
		model.addconstr(
			gp.quicksum(
				u(f, k, t)
				for f in filter(lambda: x: x.a2 == k, F)
			) <= k.A[t]
		)
	(4)
******i think this works but not sure******
	for j in J:
		model.addconstr(
			gp.quicksum(
				w[f, j, t] - w[f, f.next[j], t]
				for f in j.F
			) <= j.cap[t]
		)
*******************************************

for f in F:
	(5)
	for i in range(f.num - 1):
		j = f.path[i]
		j2 = f.path[i + 1] ***i have a feeling maybe range error here***
		for t in f.T.j:
			model.addconstr(
				w[f, j2, t + f.l[j]] - w[f, j, t] <= 0
			)
	(7)
	for j in F.path:
		for t in F.T:
			model.addconstr(
				u(f, j, t) >= 0
			)
	extra one:
	for f in F:
		for j in J:
			model.addconstr(
				w[f][j][f.T[-1]] == 1
			)












