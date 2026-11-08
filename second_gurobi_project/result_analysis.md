## GHP cases:

### Table V style: 1,000 flights

| Flights | Continued | Dep. capacity | Arr. capacity | Last scheduled departure (period) | LP objective | Solver time (s) | Noninteger flights | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 1,000 | 20% | 32 | 17 | 32 | 64,300.00 | 0.05 | 0.0% | OPTIMAL |
| 1,000 | 20% | 32 | 16 | 32 | 68,400.00 | 0.04 | 0.0% | OPTIMAL |
| 1,000 | 20% | 32 | 15 | 32 | 72,500.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 20% | 32 | 14 | 32 | inf | 0.03 | — | INFEASIBLE |
| 1,000 | 40% | 18 | 12 | 48 | 63,600.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 40% | 18 | 10 | 48 | 73,000.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 40% | 17 | 10 | 48 | 73,000.00 | 0.04 | 0.0% | OPTIMAL |
| 1,000 | 40% | 16 | 10 | 48 | 73,000.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 60% | 20 | 18 | 32 | 65,800.00 | 0.05 | 0.0% | OPTIMAL |
| 1,000 | 60% | 20 | 15 | 32 | 72,200.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 60% | 20 | 14 | 32 | 74,400.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 60% | 20 | 13 | 32 | inf | 0.03 | — | INFEASIBLE |
| 1,000 | 80% | 30 | 30 | 24 | 63,000.00 | 0.03 | 0.0% | OPTIMAL |
| 1,000 | 80% | 20 | 20 | 24 | 72,000.00 | 0.04 | 0.0% | OPTIMAL |
| 1,000 | 80% | 19 | 19 | 24 | inf | 0.06 | — | INFEASIBLE |
### Table V observations
1. **Objective Magnitude:** Objective output is around 70000. With 1000 flights each one on average costs ~70. Holding on the ground costs 50. Thus the above is equivalent to a delay of 1 or 2 units of time on the ground, which makes sense. 

2. **Capacity Effect:** As the min(Dep, Arr) capacity decreases(everything else held constant), the objective increases. This makes sense because if your capacities are being shrinked more planes will have to be delayed, and thus the objective increases. Reason for "min(dep, arr)" is because there are only two airports and there is no on-route/air delaying.

3. **Last scheduled departure** This is determined by capacities and #airplanes. If capacity is too low, you can't schedule all the airplanes in such a short time period, so we push the last scheduled departure forward.

4. **Continued Flights Effect:** in general as continued flight percentage increases, objective increases. Weird outlier at 40% where it actually goes down a bit. This is because, the with the arrival capacity going as low as 10, it is given a 48 time period of departures instead of 32 time period, decreasing delays.

### Table VI style: 3,000 flights

| Flights | Continued | Dep. capacity | Arr. capacity | Last scheduled departure (period) | LP objective | Solver time (s) | Noninteger flights | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 3,000 | 20% | 30 | 30 | 24 | 144,000.00 | 0.11 | 0.0% | OPTIMAL |
| 3,000 | 20% | 20 | 20 | 24 | 216,000.00 | 0.14 | 0.0% | OPTIMAL |
| 3,000 | 20% | 19 | 19 | 24 | inf | 0.40 | — | INFEASIBLE |
| 3,000 | 40% | 30 | 30 | 24 | 159,000.00 | 0.10 | 0.0% | OPTIMAL |
| 3,000 | 40% | 20 | 20 | 24 | 216,000.00 | 0.11 | 0.0% | OPTIMAL |
| 3,000 | 40% | 19 | 19 | 24 | inf | 0.11 | — | INFEASIBLE |
| 3,000 | 60% | 30 | 30 | 24 | 174,000.00 | 0.12 | 0.0% | OPTIMAL |
| 3,000 | 60% | 20 | 20 | 24 | 216,000.00 | 0.09 | 0.0% | OPTIMAL |
| 3,000 | 60% | 19 | 19 | 24 | inf | 0.13 | — | INFEASIBLE |
| 3,000 | 80% | 30 | 30 | 24 | 189,000.00 | 0.08 | 0.0% | OPTIMAL |
| 3,000 | 80% | 20 | 20 | 24 | 216,000.00 | 0.07 | 0.0% | OPTIMAL |
| 3,000 | 80% | 19 | 19 | 24 | inf | 0.17 | — | INFEASIBLE |
### Table VI observations
_most observations are similar as table V except:_

**Continued Flights Effects:** since the last scheduled departure is constant throughout, the objective values increase as continued flights increase too.

## TFMP cases:
### Synthetic TFMP results

Each case has 1,500 flights, 144 ten-minute periods, three airports, and three sectors. These are newly generated schedules.

| Flights | Connected | LP objective | LP noninteger flights | LP time (s) | MIP objective | MIP time (s) | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 1,500 | 20% | 78,900.00 | 0.0% | 0.23 | 78,900.00 | 0.59 | LP OPTIMAL; MIP OPTIMAL |
| 1,500 | 40% | 80,900.00 | 10.1% | 0.37 | 81,500.00 | 1.71 | LP OPTIMAL; MIP OPTIMAL |
| 1,500 | 60% | 83,233.33 | 14.1% | 0.59 | 83,350.00 | 2.21 | LP OPTIMAL; MIP OPTIMAL |
| 1,500 | 80% | 84,633.33 | 17.8% | 0.59 | 84,800.00 | 9.77 | LP OPTIMAL; MIP OPTIMAL |

Times are Gurobi solve times; they exclude CSV loading and Python model construction.
### TFMP Observations

**Continued Flights Effects:** as the percent of continued flights increased, there was a higher(and non-zero) amount of non-integer solutions of the LP. This is probably due to the higher complexity of TFMP compared with GHP, and so, Gurobi was unable to relax the LP into only integers.