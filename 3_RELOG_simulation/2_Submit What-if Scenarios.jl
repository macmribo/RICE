# Improve output style on Jupyter Notebook
using Logging
global_logger(ConsoleLogger(stdout));

# Install extra packages
using Pkg
Pkg.add("Glob")

# Package to time cells
using TickTock

using RELOG
using Glob
using Logging


folder = joinpath(pwd(), "output")

readdir(folder)



glob(" ", folder)

#problem = "initial"
problem = "20230301_CASE0_v3"

tick()
# Solve reference case

_, model = RELOG.solve("input/$problem/case.json", return_model=true);

# Solve what-if scenarios
for filename in glob("input/what-if_$problem/*.json")
    solution = RELOG.resolve(model, filename)
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






