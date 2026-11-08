# Synthetic ground-holding LP results

These are new synthetic instances. Capacity levels follow the 1998 tables; objectives, feasibility, and fractional-flight percentages need not match the paper.

Last scheduled departure is the latest scheduled takeoff period in that case's input flights. Each period is 15 minutes; all cases use periods 0–63.

## Table V style: 1,000 flights

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

## Table VI style: 3,000 flights

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
