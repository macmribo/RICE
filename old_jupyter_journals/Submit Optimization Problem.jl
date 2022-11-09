# Improve output style on Jupyter Notebook
using Logging
global_logger(ConsoleLogger(stdout));

# Import package
using RELOG

# Package to time cells
using TickTock

tick()
# Solve optimization problem
solution = RELOG.solve("input/smallproblem/InputPipelineData.json")

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors
RELOG.write_plants_report(solution, "output/smallproblem/plants.csv")

# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure
RELOG.write_transportation_report(solution, "output/smallproblem/transportation.csv")

# Write CSV report showing primary product amounts, locations and marginal costs
RELOG.write_products_report(solution, "output/smallproblem/products.csv");
tock()

tick()
# Solve optimization problem
solution = RELOG.solve("input/conservative/locodata_ultra.json")

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors
RELOG.write_plants_report(solution, "output/conservative/plants.csv")

# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure
RELOG.write_transportation_report(solution, "output/conservative/transportation.csv")

# Write CSV report showing primary product amounts, locations and marginal costs
RELOG.write_products_report(solution, "output/conservative/products.csv");
tock()

# Solve optimization problem
solution = RELOG.solve("input/optimistic/locodata_ultra.json")

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors
RELOG.write_plants_report(solution, "output/optimistic/plants.csv")

# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure
RELOG.write_transportation_report(solution, "output/optimistic/transportation.csv")

# Write CSV report showing primary product amounts, locations and marginal costs
RELOG.write_products_report(solution, "output/optimistic/products.csv");


