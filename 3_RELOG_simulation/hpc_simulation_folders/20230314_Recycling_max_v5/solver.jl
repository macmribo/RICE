# Improve output style on Jupyter Notebook
using Logging
global_logger(ConsoleLogger(stdout));

# Import package
using RELOG, Gurobi, JuMP
gurobi = optimizer_with_attributes(
    Gurobi.Optimizer,
    "TimeLimit" => 3600,
    "MIPGap" => 0.001,
)
# Package to time cells
using TickTock

tick()
# Solve optimization problem
solution = RELOG.solve("/projects/pvsoiling/RELOG/20230314_Recycling_max_v5/input/solver/case.json", optimizer=gurobi)

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors
tick()
RELOG.write_plants_report(solution, "/projects/pvsoiling/RELOG/20230314_Recycling_max_v5/output/solver/plants.csv")
tock()
# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure
tick()
RELOG.write_transportation_report(solution, "/projects/pvsoiling/RELOG/20230314_Recycling_max_v5/output/solver/transportation.csv")
tock()
# Write CSV report showing primary product amounts, locations and marginal costs
tick()
RELOG.write_products_report(solution, "/projects/pvsoiling/RELOG/20230314_Recycling_max_v5/output/solver/products.csv");
tock()
