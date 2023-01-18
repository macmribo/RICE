# RICE

How to run the RELOG software with PV_ICE.

---
## RELOG and HPC User Guide

**Assumption:** You have an NREL HPC account and you are entering from VS Code .

Let’s start!

### STEP 1: (Optional) Setup vscode with Eagle.

Install the Remote – SSH extension
Setup the ssh configuration file: F1 + Remote-SSH: Connect to Host + Add new SSH Host + ssh <username>@eagle.hpc.nrel.gov
Enter password
TODO: how to setup vscode so it stops asking for password, it is something with the ssh config and keys.

### STEP 2: Load conda and create a new environment.

```
cd /projects/pvsoiling # Navigate to your project folder.
mkdir RELOG # Create a folder for your subproject.
module load conda # Activate conda
conda create -n RELOG python=3.9.4 # Create new environment.
conda activate RELOG # Activate the created environment, check this link in case Eagle does not recognize the name of you environment.
```

### STEP 3: Install necessary packages.

```
conda install jupyterlab
conda install pandas
conda install numpy
conda install matplotlib
conda install seaborn
conda install geopandas
```

### STEP 4: Load julia and install RELOG.

```
module load julia
using Pkg
Pkg.add(name=”RELOG”, version=”0.5”)
```

### STEP 5: Copy your files to the project folder

In a NEW TERMINAL (not inside vs code and Eagle) copy the following line, with your specific paths. ADVICE: Have your input files such as the solver file and the what-if scenarios, and output files (just the necessary folders, i.e. one for the solver outputs and another one with the what-if scenarios) ready so you don’t have to manupulate these files through you Eagle session.
`scp -r local/computer/path/of/the/original/folder user@eagle.nrel.gov:/projects/allocatingproject/folder/where/copy/goes`

### STEP 6: Create the .sbatch file
Before running the job, it is necessary to create a job file that streamlines the files to run. You can also add useful commands to this file to get notifications when your run has started, when it is done, and if it has failed or. Here is an example of the one I use, mine is called file_batch.sbatch (the name can be anything!).

```
#!/usr/bin/bash

#SBATCH --mail-user=MACARENA.MENDEZRIBO@nrel.gov # User email address to receive notifications.
#SBATCH --mail-type=BEGIN,END,FAIL	# Send notifications when it begins, it ends and if it fails.
module load conda
module load julia
module load gurobi

source activate RELOG

julia Smallproblem_what-if.jl # Change this file for the scenario you want to run.
```

***Notes:***
Batch files commands start with a # are NOT comments, comments use three #.
Find more sample batch files here.

### STEP 7: Run the job with Eagle.

```
sbatch -A pvsoiling -t 10 -N 1 -p debug file_batch.sbatch
batch -A pvsoiling -t 300 -N 1 -p standard file_batch.sbatch
```

* -A: project allocation, in this case ‘pvsoiling’
* -t: time allocated for the run
* -N: number of nodes
* -p: debug (max -t 60 and max -N 2) or standard (limited by the allocated project).

Lastly, specify the batch file, in my case is file_batch.sbatch
It seems like the standard scenarios take around 50 minutes. What-if analysis are to be determined.

### STEP 8: Collect the output files and paste them outside Eagle for data processing.
This is a personal choice. For me, this is easier than doing data wrangling inside Eagle, this way I use jupyter notebook outside.

`scp -r user@eagle.nrel.gov:/projects/allocatingproject/folder/where/output/folder/is local/computer/path/of/copied/folder`


#### Useful how-to links: 
* [HPC Eagle Documentation](https://www.nrel.gov/hpc/eagle-system.html)
* [NREL HPC Github](https://nrel.github.io/HPC/Documentation/)
* [GitHub NREL HPC wiki](https://github.com/NREL/HPC/wiki/)
* [sbatch commands](https://slurm.schedmd.com/sbatch.html)
* [Commands to Monitor and Control Jobs on Eagle](https://www.nrel.gov/hpc/eagle-monitor-control-commands.html)
