# Improve output style on Jupyter Notebook
using Logging
global_logger(ConsoleLogger(stdout));

# Package to time cells
using TickTock

using RELOG, Gurobi, JuMP

gurobi = optimizer_with_attributes(
    Gurobi.Optimizer,
    "TimeLimit" => 3600,
    "MIPGap" => 0.001,
)
using Glob
using Logging


tick()
# Solve reference case
_, model = RELOG.solve("/projects/pvsoiling/RELOG/20230314_Recycling_med_v4/input/solver/case.json", return_model=true, optimizer=gurobi);

# Solve what-if cases:
for filename in glob("input/what-if/*.json")
    solution = RELOG.resolve(model, filename, optimizer=gurobi)
    prefix = joinpath(
        "output",
        "what-if",
        replace(basename(filename), ".json" => ""),
    )
    RELOG.write_plants_report(solution, "$(prefix)_plants.csv")
    RELOG.write_products_report(solution, "$(prefix)_products.csv")
    RELOG.write_plant_outputs_report(solution, "$(prefix)_plant_outputs.csv")
    RELOG.write_plant_emissions_report(solution, "$(prefix)_plant_emissions.csv")
    RELOG.write_transportation_report(solution, "$(prefix)_tr.csv")
    RELOG.write_transportation_emissions_report(solution, "$(prefix)_tr_emissions.csv")
end
tock()


