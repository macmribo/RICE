#!/usr/bin/env python
# coding: utf-8

# # Folder generation

# This jupyter journal was created to generate the needed folders to get ready with a new RELOG simulation.
# There are three main folders in which we need to create new folders:
# * Input: Here is where the input data is saved. We will create two folders here, one for the normal solver input data (the data that we will save here is generated using the `data_preprocess_1.ipynb` found [here](PV_Recycling_Plant/data/data_preprocess_1.ipynb)), and another one for the sensitivity analysis input scenarios or 'what-if'(generated using `Generate What-If Scenarios.ipynb` [notebook](Generate What-If Scenarios.
# * Output: Here is where the solutions of the simulations will be saved. The same way as before, we will create two folders named the same as the folders in the input file, one for the normal solver output data (generated with the `1_Submit Optimization Problem.ipynb`), and another one for the sensitivity analysis output scenarios or 'what-if' (generated with the python file `2_Submit What-if Scenarios.ipynb`).
# * Figures: Same folders as before one for the solver images and another for the sensitivity analysis.

# ## Folder name convention:

# I like naming my scenarios with the date I created them in ISO format (i.e. YYYYMMDD) and a name that helps me identify my scenario.

# In[3]:


import os


# In[12]:


simulation_name = '20230213_folder_generation_test' # This line is the only one that needs to be changed.
simulation_whatif = 'what-if_' + simulation_name


# In[13]:


cwd = os.getcwd()


# In[9]:


input_file = os.path.join(cwd, 'input', simulation_name)
input_file_whatif = os.path.join(cwd, 'input', simulation_whatif)
output_file = os.path.join(cwd, 'output', simulation_name)
output_file_whatif = os.path.join(cwd, 'output', simulation_whatif)
figures_file = os.path.join(cwd, 'figures', simulation_name)
figures_file_whatif = os.path.join(cwd, 'figures', simulation_whatif)


# In[14]:


files_to_create = [input_file, input_file_whatif, output_file, output_file_whatif, figures_file, figures_file_whatif]


# In[18]:


files_to_create[5]


# In[20]:


for files in range(len(files_to_create)):
    # Check whether the specified path exists or not
    isExist = os.path.exists(files_to_create[files])
    if isExist:
        print(f"The path for {files_to_create[files]} already exists!")
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(files_to_create[files])
        print(f"The new directory for {files_to_create[files]} has been created!")


# In[ ]:




