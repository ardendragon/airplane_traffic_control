# Second Gurobi Project: Basic Airplane Variables and Constraints

run: 
```bash
source .venv/bin/activate
python second_gurobi_project/air_traffic_flow_management.py
```

The model currently imports a two-flight example from `mock_data.py`.




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












