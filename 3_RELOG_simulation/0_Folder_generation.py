#!/usr/bin/env python
# coding: utf-8

# # Folder generation

# This jupyter journal was created to generate the needed folders to get ready with a new RELOG simulation.
# There are three main folders in which we need to create new folders:
# * Input: Here is where the input data is saved. We will create two folders here, one for the normal solver input data (the data that we will save here is generated using the `data_preprocess_1.ipynb` found [here](PV_Recycling_Plant/data/data_preprocess_1.ipynb)), and another one for the sensitivity analysis input scenarios or 'what-if'(generated using `Generate What-If Scenarios.ipynb` [notebook](Generate What-If Scenarios.
# * Output: Here is where the solutions of the simulations will be saved. The same way as before, we will create two folders named the same as the folders in the input file, one for the normal solver output data (generated with the `1_Submit Optimization Problem.ipynb`), and another one for the sensitivity analysis output scenarios or 'what-if' (generated with the python file `2_Submit What-if Scenarios.ipynb`).
# * Figures: Same folders as before one for the solver images and another for the sensitivity analysis.
# 
# Lastly, I will generate a special folder that include the necessary files to make an hpc simulation in the case that the simulation takes too long.

# In[4]:


import os
from datetime import datetime
import shutil
from distutils.dir_util import copy_tree


# Fill out with the combination to generate 

# In[1]:


facility_label = ['Manufacturing', 'Recycling','Manufacturing_cap', 'Recycling_cap']
location_label = ['NAICS', '40209']
factor_label_rec = ['05', '1', '2', '5', '10']
factor_label_man = ['0001','05', '1', '2'] # 0 is 0,5


# In[2]:


files_list = []
for fac in facility_label:
    for loc in location_label:
        if fac.startswith('Manufacturing'):
            for fac_man in factor_label_man:
                files_list.append(fac+'_'+loc+'_'+fac_man)
        else:
            for fac_rec in factor_label_rec:
                files_list.append(fac+'_'+loc+'_'+fac_rec) 


# ## Folder generation:

# In[8]:


whatif = False


# In[6]:


cwd = os.getcwd()


# In[14]:


for simulation_name in files_list:
    if whatif:
        input_file = os.path.join(cwd, 'input', simulation_name)
        input_file_whatif = os.path.join(cwd, 'input', 'what-if_'+ simulation_name)
        output_file = os.path.join(cwd, 'output', simulation_name)
        output_file_whatif = os.path.join(cwd, 'output', 'what-if_'+ simulation_name)
        figures_file = os.path.join(cwd, 'figures', simulation_name)
        figures_file_whatif = os.path.join(cwd, 'figures', 'what-if_'+ simulation_name)
        files_to_create = [input_file, input_file_whatif, output_file, output_file_whatif, figures_file, figures_file_whatif]
    else:
        input_file = os.path.join(cwd, 'input', simulation_name)
        output_file = os.path.join(cwd, 'output', simulation_name)
        figures_file = os.path.join(cwd, 'figures', simulation_name)
        files_to_create = [input_file, output_file, figures_file]
    for files in range(len(files_to_create)):
        # Check whether the specified path exists or not
        isExist = os.path.exists(files_to_create[files])
        if isExist:
            print(f"The path for {files_to_create[files]} already exists!")
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(files_to_create[files])
            print(f"The new directory for {files_to_create[files]} has been created!")


# # HPC case generation

# Only use this one when you have your input files ready for simulation, this means that the `input` folder has the `case.json` (i.e. the saved file made in the [RELOG case builder](https://relog.axavier.org/casebuilder)), and the `what-if_blablabla` has been also generated.

# In[498]:


cwd = os.getcwd()


# In[511]:


#facility_label = ['Manufacturing', 'Recycling','Manufacturing_cap', 'Recycling_cap']
facility_label = ['Manufacturing_cap', 'Recycling_cap']
location_label = ['NAICS', '40209']
factor_label_rec = ['05', '1', '2', '5', '10']
factor_label_man = ['0001','05', '1', '2'] # 0 is 0,5


# In[512]:


files_list = []
for fac in facility_label:
    for loc in location_label:
        if fac.startswith('Manufacturing'):
            for fac_man in factor_label_man:
                files_list.append(fac+'_'+loc+'_'+fac_man)
        else:
            for fac_rec in factor_label_rec:
                files_list.append(fac+'_'+loc+'_'+fac_rec) 


# ## HPC folder generation

# Make sure that the simulation folder exists in the main folders, that it has a `case.json` file inside and that it also has the what-if scenarios generated. If these are not created it will throw an error asking you to do those steps first.

# In[10]:


files_list


# In[ ]:


simulation_folders[0]


# In[18]:


os.remove('/Users/mmendez/Documents/Postdoc/Software_dev/RICE/3_RELOG_simulation/input/Recycling_40209_05/.DS_Store')


# In[19]:


os.listdir('/Users/mmendez/Documents/Postdoc/Software_dev/RICE/3_RELOG_simulation/input/Recycling_40209_05')


# In[20]:


for simulation_name in files_list:   
# Check that the path exists
    if whatif:
        input_solver_folder_location = os.path.join(cwd, 'input', simulation_name)
        input_whatif_folder_location = os.path.join(cwd, 'input', 'what-if_'+simulation_name)
        simulation_folders = [input_solver_folder_location, input_whatif_folder_location ]
    else:
        input_solver_folder_location = os.path.join(cwd, 'input', simulation_name)
        simulation_folders = [input_solver_folder_location]
    for files in range(len(simulation_folders)):
        isExist = os.path.exists(simulation_folders[files])
        if isExist:
            print(f"The path for {simulation_folders[files]} exists! You may continue to the next step.")
        else:
            raise PathNotFoundError(f'The path {input_solver_file_location} does not exist, please generate the necessary folders using the 0_Folder_generation.ipynb found in 3_RELOG_simulation.')
# Check that the files are inside
    if whatif:
            if os.listdir(simulation_folders[0]) == ['case.json']:
                print('Case.json exists!')
            else:
                raise FileNotFoundError('The file ''case.json'' does not exist in please generate the the file using RELOG\'s case builder.')
            if len(input_whatif_folder_location) == 0:
                raise FileNotFoundError('The what-if files have not been generated, please go to 3_RELOG_simulation/input/Generate What-If Scenarios.ipynb and generate the scenario files.')
            else:
                print('The what-if files exist, you may continue!')
    else:
            if os.listdir(simulation_folders[0]) == ['case.json']:
                print('Case.json exists!')
            else:
                print(f'File {simulation_folders[0]}')
                raise FileNotFoundError(f'The file ''case.json'' does not exist, please generate the the file using RELOG\'s case builder.')
# Create paths for the hpc
    if whatif:
        hpc_input_solver_folder = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'input', 'solver') 
        hpc_input_whatif_folder = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'input', 'what-if') 
        hpc_output_solver_folder = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'output', 'solver') 
        hpc_output_whatif_folder = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'output', 'what-if') 
        check_list = [hpc_input_solver_folder, hpc_input_whatif_folder, hpc_output_solver_folder, hpc_output_whatif_folder]
    else:
        hpc_input_solver_folder = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'input', 'solver') 
        hpc_output_solver_folder = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'output', 'solver') 
        check_list = [hpc_input_solver_folder, hpc_output_solver_folder]   
# Create files if they don't already exist    
    for files in range(len(check_list)):
        # Check whether the specified path exists or not
        isExist = os.path.exists(check_list[files])
        if isExist:
            print(f"The path for {check_list[files]} already exists!")
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(check_list[files])
            print(f"The new directory for {check_list[files]} has been created!")


# Copy the files from the template codes into the simulation folder:
    cwd = os.getcwd()
    template_files = os.path.join(cwd, 'hpc_simulation_folders', 'template_codes')
    input_files = os.path.join(cwd, 'hpc_simulation_folders', simulation_name)
    copy_tree(template_files, input_files)

    # Read in the file
    with open(os.path.join(input_files, 'solver.jl'), 'r') as file :
        filedata = file.read()
# Change the word 'scenario' for the folder scenario name in the solver.jl and the what-if.jl files:
    # Replace the target string
    filedata = filedata.replace('scenario', simulation_name)

    # Write the file out again
    with open(os.path.join(input_files, 'solver.jl'), 'w') as file:
        file.write(filedata)
    if whatif:
        # Read in the file
        with open(os.path.join(input_files, 'what-if.jl'), 'r') as file :
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace('scenario', simulation_name)

        # Write the file out again
        with open(os.path.join(input_files, 'what-if.jl'), 'w') as file:
            file.write(filedata)
# Copy the solver and whatif files to the hpc scenario folders
    if whatif:
        copy_tree(input_solver_folder_location, hpc_input_solver_folder)
        copy_tree(input_whatif_folder_location, hpc_input_whatif_folder)
    else:
        copy_tree(input_solver_folder_location, hpc_input_solver_folder)


# Now that you have your simulation ready for hpc, copy the simulation folder and paste it in the HPC folder. In my case, I go to the terminal ang run the following line:
# `scp -r /Users/mmendez/Documents/Postdoc/Software_dev/RICE/3_RELOG_simulation/hpc_simulation_folders/name_of_scenario mmendez@eagle.nrel.gov:/projects/pvsoiling/RELOG/`
# 
# **Note: It will ask for the Eagle password**
# 
# After I am done with the simulation, I copy the samle file but now it has output files in it so I take the simulation output folder and save it in the hpc_scenario_outputs folder. After that I manually copy and paste this file into the local output simulation folder.
# `scp -r mmendez@eagle.nrel.gov:/projects/pvsoiling/RELOG/scenario_name/output /Users/mmendez/Documents/Postdoc/Software_dev/RICE/3_RELOG_simulation/hpc_simulation-folders/hpc_scenario_outputs/name_of_scenario`
# 
# **Note: It will ask for the Eagle password**  
#     
# 

# ## Little bonus code for the lazy
# Just run this cell and copy the line you need to either copy from local machine to HPC, of from HPC to local machine:

# Local machine to HPC (copy and paste it into your terminal):

# In[5]:


cwd = os.getcwd()


# In[21]:


print('LOCAL-HPC TO HPC:')
for simulation_name in files_list:
    local_path = os.path.join(cwd, 'hpc_simulation_folders', simulation_name) #change the last entry for the specific name of your simulation
    print('scp -r', local_path, 'mmendez@eagle.nrel.gov:/projects/pvsoiling/RELOG')


# HPC to local machine (copy and paste it into your terminal), this path only works me, but if you have access to the same project folder, use it).

# In[8]:


len(files_list)


# In[22]:


print('HPC TO LOCAL-HPC:')
for simulation_name in files_list:
    local_path = os.path.join(cwd, 'hpc_simulation_folders', simulation_name) 
    hpc_path = os.path.join(f'mmendez@eagle.nrel.gov:/projects/pvsoiling/RELOG/{simulation_name}/output', ) #change the last entry for the specific name of your simulation
    print('scp -r', hpc_path, local_path)


# In[23]:


cwd


# In[27]:


print('LOCAL-HPC TO LOCAL:')
for simulation_name in files_list:
    local_path = os.path.join(cwd, 'hpc_simulation_folders', simulation_name, 'output', 'solver') 
    local_local_path = os.path.join(cwd, 'output', simulation_name ) #change the last entry for the specific name of your simulation
    print('scp -r', local_path, local_local_path)


# In[ ]:





# In[ ]:





# In[ ]:




