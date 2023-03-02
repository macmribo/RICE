# Improve output style on Jupyter Notebook
using Logging
global_logger(ConsoleLogger(stdout));

# Import package
using RELOG

# Package to time cells
using TickTock


problem = "20230301_CASE0_v3"

tick()
# Solve optimization problem
solution = RELOG.solve("input/$problem/case.json")

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors
RELOG.write_plants_report(solution, "output/$problem/plants.csv")

# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure
RELOG.write_transportation_report(solution, "output/$problem/transportation.csv")

# Write CSV report showing primary product amounts, locations and marginal costs
RELOG.write_products_report(solution, "output/$problem/products.csv");
tock()


