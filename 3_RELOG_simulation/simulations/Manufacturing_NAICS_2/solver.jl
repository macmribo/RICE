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
solution = RELOG.solve("/projects/rice/Manufacturing_NAICS_2/input/case.json", optimizer=gurobi)

# Write CSV report showing plant costs, capacities, energy expenditure and
# utilization factors

RELOG.write_plants_report(solution, "/projects/rice/Manufacturing_NAICS_2/output/plants.csv")

# Write CSV report showing amount of product sent from initial locations to plants,
# and from one plant to another. Includes the distance between each pair of
# locations, amount-distance shipped, transportation costs and energy expenditure

RELOG.write_transportation_report(solution, "/projects/rice/Manufacturing_NAICS_2/output/transportation.csv")

# Write CSV report showing primary product amounts, locations and marginal costs

RELOG.write_products_report(solution, "/projects/rice/Manufacturing_NAICS_2/output/products.csv")

RELOG.write_plant_emissions_report(solution, "/projects/rice/Manufacturing_NAICS_2/output/plant_emissions.csv")

RELOG.write_plant_outputs_report(solution, "/projects/rice/Manufacturing_NAICS_2/output/plant_oputputs.csv")

RELOG.write_transportation_emissions_report(solution, "/projects/rice/Manufacturing_NAICS_2/output/transportation_emissions.csv")
tock()


