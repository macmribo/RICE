# Improve output style on Jupyter Notebook
using Logging
global_logger(ConsoleLogger(stdout));

# Package to time cells
using TickTock

using RELOG


using Glob
using Logging


tick()
# Solve reference case
problem = "smallproblem"
_, model = RELOG.solve("input/$problem/InputPipelineData.json", return_model=true);
tock()

tick()
# Solve what-if scenarios
for filename in glob(r"input/whatif-$problem/*.json")
    solution = RELOG.resolve(model, filename, optimizer=gurobi)
    prefix = joinpath(
        r"output",
        "whatif-$problem",
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


