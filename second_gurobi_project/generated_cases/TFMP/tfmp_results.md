# Synthetic TFMP results

Each case has 1,500 flights, 144 ten-minute periods, three airports, and three sectors. These are newly generated schedules.

| Flights | Connected | LP objective | LP noninteger flights | LP time (s) | MIP objective | MIP time (s) | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 1,500 | 20% | 78,900.00 | 0.0% | 0.23 | 78,900.00 | 0.59 | LP OPTIMAL; MIP OPTIMAL |
| 1,500 | 40% | 80,900.00 | 10.1% | 0.37 | 81,500.00 | 1.71 | LP OPTIMAL; MIP OPTIMAL |
| 1,500 | 60% | 83,233.33 | 14.1% | 0.59 | 83,350.00 | 2.21 | LP OPTIMAL; MIP OPTIMAL |
| 1,500 | 80% | 84,633.33 | 17.8% | 0.59 | 84,800.00 | 9.77 | LP OPTIMAL; MIP OPTIMAL |

Times are Gurobi solve times; they exclude CSV loading and Python model construction.
