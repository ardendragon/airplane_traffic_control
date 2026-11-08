## GHP cases:
### Table V observations
1. **Objective Magnitude:** Objective output is around 70000. With 1000 flights each one on average costs ~70. Holding on the ground costs 50. Thus the above is equivalent to a delay of 1 or 2 units of time on the ground, which makes sense. 

2. **Capacity Effect:** As the min(Dep, Arr) capacity decreases(everything else held constant), the objective increases. This makes sense because if your capacities are being shrinked more planes will have to be delayed, and thus the objective increases. Reason for "min(dep, arr)" is because there are only two airports and there is no on-route/air delaying.

3. **Last scheduled departure** This is determined by capacities and #airplanes. If capacity is too low, you can't schedule all the airplanes in such a short time period, so we push the last scheduled departure forward.

4. **Continued Flights Effect:** in general as continued flight percentage increases, objective increases. Weird outlier at 40% where it actually goes down a bit. This is because, the with the arrival capacity going as low as 10, it is given a 48 time period of departures instead of 32 time period, decreasing delays.

### Table VI observations
_most observations are similar as table V except:_
4. **Continued Flights Effects:** since the last scheduled departure is constant throughout, the objective values increase as continued flights increase too.

## TFMP cases:
1. **Continued Flights Effects:** as the percent of continued flights increased, there was a higher(and non-zero) amount of non-integer solutions of the LP. This is probably due to the higher complexity of TFMP compared with GHP, and so, Gurobi was unable to relax the LP into only integers.