import argparse
from collections import defaultdict
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

import mock_data
from ground_holding_cases import load_case


def main(
	case_dir: Path | None = None,
	relax: bool = False,
	time_limit: float | None = None,
	departure_capacity: int | None = None,
	arrival_capacity: int | None = None,
	quiet: bool = False,
) -> dict:
	F, J, K, L, T = (
		load_case(case_dir)
		if case_dir is not None
		else (mock_data.F, mock_data.J, mock_data.K, mock_data.L, mock_data.T)
	)
	model = gp.Model("air_traffic_flow_management")
	if quiet:
		model.Params.OutputFlag = 0
	if time_limit is not None:
		model.Params.TimeLimit = time_limit
	for airport in K.values():
		if departure_capacity is not None:
			airport["D"] = {t: departure_capacity for t in T}
		if arrival_capacity is not None:
			airport["A"] = {t: arrival_capacity for t in T}

	# if plane f has reached sector j by time t
	indices = [(f, j, t) for f in F for j in F[f]["path"] for t in F[f]["T"][j]]
	w = model.addVars(
		indices,
		vtype=GRB.CONTINUOUS if relax else GRB.BINARY,
		ub=1,
		name="choose",
	)
	departing = defaultdict(list)
	arriving = defaultdict(list)
	for f in F:
		departing[F[f]["a1"]].append(f)
		arriving[F[f]["a2"]].append(f)

	# to prevent w's that are outside of the range
	def reached_by(f, j, t):
	    times = F[f]["T"][j]
	    if t < times[0]:
	        return 0
	    if t > times[-1]:
	        return 1
	    return w[f, j, t]


	# if plane f is in sector j at time t
	def u(f, j, t):
		return reached_by(f, j, t) - reached_by(f, j, t - 1)


	#time wasted on ground
	def g(f):
		return gp.quicksum(
			t * u(f, F[f]["path"][0], t)
			for t in range(F[f]["T"][F[f]["a1"]][0], F[f]["T"][F[f]["a1"]][-1] + 1)
		) - F[f]["dep"]

	#time wasted in the air
	def a(f):
		return gp.quicksum(
			t * u(f, F[f]["path"][-1], t)
			for t in range(F[f]["T"][F[f]["a2"]][0], F[f]["T"][F[f]["a2"]][-1] + 1)
		) - F[f]["arr"] - g(f)

	# objective is to minimize total costs of airplanes
	model.setObjective(
	    gp.quicksum(
	    	F[f]["cg"] * g(f) + F[f]["cf"] * a(f)
	    	for f in F
	    ),
	    GRB.MINIMIZE,
	)

	# constraints
	for t in T:
		for k in K:
		#(2) airplanes that take off at airport k don't exceed departure capacity
			model.addConstr(
				gp.quicksum(
					u(f, k, t)
						for f in departing[k]
					) <= K[k]["D"][t]
			)
		#(3) airplanes that arrive at airport k don't exceed arrival capacity
			model.addConstr(
				gp.quicksum(
					u(f, k, t)
						for f in arriving[k]
					) <= K[k]["A"][t]
			)
		#(4) airplanes in sector j at time t cannot exceed sector capacity
		for j in J:
			model.addConstr(
				gp.quicksum(
					reached_by(f, j, t) - reached_by(f, F[f]["next"][j], t)
					for f in J[j]["F"]
				) <= J[j]["cap"][t]
			)

	for f in F:
		#(5) connectivity of sectors in paths
		for i in range(F[f]["num"] - 1):
			j = F[f]["path"][i]
			j2 = F[f]["path"][i + 1]
			for t in F[f]["T"][j]:
				model.addConstr(
					reached_by(f, j2, t + F[f]["l"][j]) - w[f, j, t] <= 0
				)
		#(7) connectivity in time
		for j in F[f]["path"]:
			for t in F[f]["T"][j]:
				model.addConstr(
					u(f, j, t) >= 0
				)
		# make sure the plane has reached the sector by the end of the time it can reach the sector
		for j in F[f]["path"]:
			model.addConstr(
				w[f, j, F[f]["T"][j][-1]] == 1
			)
	#(6) flight connectivity
	for ff, f in L:
		k = F[f]["a1"]
		if F[ff]["a2"] != k:
			raise ValueError(f"{ff} does not arrive at {f}'s departure airport")
		for t in F[f]["T"][k]:
			model.addConstr(
				reached_by(f, k, t) <= reached_by(ff, k, t - F[ff]["s"])
			)

	model.optimize()

	status_names = {
		GRB.OPTIMAL: "OPTIMAL",
		GRB.INFEASIBLE: "INFEASIBLE",
		GRB.TIME_LIMIT: "TIME_LIMIT",
		GRB.INF_OR_UNBD: "INF_OR_UNBD",
		GRB.UNBOUNDED: "UNBOUNDED",
	}
	result = {
		"status": status_names.get(model.Status, f"STATUS_{model.Status}"),
		"objective": model.ObjVal if model.Status == GRB.OPTIMAL else None,
		"solver_seconds": model.Runtime,
		"fractional_flights": None,
		"noninteger_percent": None,
	}
	if relax and model.Status == GRB.OPTIMAL:
		fractional_flights = sum(
			any(1e-6 < w[f, j, t].X < 1 - 1e-6 for j in F[f]["path"] for t in F[f]["T"][j])
			for f in F
		)
		result["fractional_flights"] = fractional_flights
		result["noninteger_percent"] = 100 * fractional_flights / len(F)
	if not quiet:
		if model.Status != GRB.OPTIMAL:
			raise RuntimeError(f"No optimal plan found (status {result['status']})")
		print(f"Objective: {result['objective']:g}")
		if relax:
			print(f"Flights with a fractional variable: {result['fractional_flights']}/{len(F)} ({result['noninteger_percent']:.1f}%)")
	return result

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Solve the air traffic flow model.")
	parser.add_argument("--case-dir", type=Path, help="Directory with generated CSV case files")
	parser.add_argument("--relax", action="store_true", help="Solve the LP relaxation")
	parser.add_argument("--time-limit", type=float, help="Solver time limit in seconds")
	args = parser.parse_args()
	main(args.case_dir, args.relax, args.time_limit)








