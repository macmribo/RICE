#!/usr/bin/bash


#SBATCH --mail-user=HOPE.WIKOFF@nrel.gov
#SBATCH --mail-user=macmribo@gmail.com
#SBATCH --mail-type=BEGIN,END,FAIL

#SBATCH --output=R-%j.out
#SBATCH --error=R-%j.err

module load conda
module load julia
module load gurobi

source activate RELOG

### Select the solver you want to run by commenting or uncommenting, each will take around one hour
julia solver.jl
### julia what-if.jl


