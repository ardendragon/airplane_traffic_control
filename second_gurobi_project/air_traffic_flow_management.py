import gurobipy as gp
from gurobipy import GRB

from mock_data import F, J, K, T


def main() -> None:
	model = gp.Model("air_traffic_flow_management")

	# if plane f has reached sector j by time t
	w = model.addVars(F, (*K, *J), T, vtype=GRB.BINARY, name="choose")

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
						for f in filter(lambda x: F[x]["a1"] == k, F)
					) <= K[k]["D"][t]
			)
		#(3) airplanes that arrive at airport k don't exceed arrival capacity
			model.addConstr(
				gp.quicksum(
					u(f, k, t)
						for f in filter(lambda x: F[x]["a2"] == k, F)
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

	model.optimize()

	if model.Status != GRB.OPTIMAL:
	        raise RuntimeError(f"No optimal plan found (status {model.Status})")

if __name__ == "__main__":
    main()








