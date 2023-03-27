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
solution = RELOG.solve("/projects/pvsoiling/RELOG/scenario/input/solver/case.json", optimizer=gurobi)

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors

RELOG.write_plants_report(solution, "/projects/pvsoiling/RELOG/scenario/output/solver/plants.csv")

# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure

RELOG.write_transportation_report(solution, "/projects/pvsoiling/RELOG/scenario/output/solver/transportation.csv")

# Write CSV report showing primary product amounts, locations and marginal costs

RELOG.write_products_report(solution, "/projects/pvsoiling/RELOG/scenario/output/solver/products.csv");

RELOG.write_plant_emissions_report(solution, "/projects/pvsoiling/RELOG/scenario/output/solver/plant_emissions.csv");

RELOG.write_plant_outputs_report(solution, "/projects/pvsoiling/RELOG/scenario/output/solver/plant_oputputs.csv");

RELOG.write_transportation_emissions_report(solution, "/projects/pvsoiling/RELOG/scenario/output/solver/transportation_emissions.csv");
tock()


