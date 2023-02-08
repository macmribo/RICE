#!/usr/bin/env python
# coding: utf-8

# # Data Preprocess 2

# This journal uses the PV ICE data that we previously generated in [Data Preprocess 1 Section 1](./data_preprocess_1.ipynb) to obtain the tonnes of material processed per tonne of PV Module.
# 
# Ideally, we should be able to do this with the time series waste data that PV ICE generates; unfortunately, RELOG does not have this capability.
# 
# To accommodate, I will do the following:
# 1. Load the waste material data.
# 2. Get the total PV module waste generated from 2023 to 2050. *Note: The 2023 files include waste accumulated from 2010 to 2023*.
# 3. Calculate % of specific material per tonne of total PV waste.
# 
# ***NOTE:** All quantities are given in **metric tonnes**.*

# ## 0. Load necessary libraries

# In[1]:


import numpy as np
import pandas as pd
import os,sys
import matplotlib.pyplot as plt
from pathlib import Path


# ## 1. Load waste material data

# There are a lot of files here, so let's generate a code to load all the files with their variable name.

# In[2]:


mats = ['csi', 'cdte']
material_list_csi = ['glass', 'silicon', 'silver', 'copper', 'aluminium_frames', 'encapsulant', 'backsheet', 'Module']
material_list_cdte = ['cadmium', 'tellurium', 'glass_cdte', 'aluminium_frames_cdte', 'Module', 'copper_cdte', 'encapsulant_cdte']


# There are a bunch of columns that we do not want, so let's ignore them before loading all the files. To do this, I load one of the files (it does not matter which one), and allocate the column names to a variable. Here I want to ignore `['Unnamed: 0', 0, 2010, 'longitude', 'latitude', 'FIPS', 45]`.
# 
# **TO DO:** Get rid of `'Unnamed: 0'` and `0` columns in data_preprocess_1 when I save the files in the first place, it is useless. Once I fix this and re-generate the files, I have to re-write part of this code.

# In[7]:


cols = list(pd.read_csv("csi_wasteEOL_Module.csv", nrows =1))


# In[8]:


rem_cols = ['0','2010','longitude', 'latitude', 'FIPS', '45', 'total waste']


# In[9]:


[cols.remove(item) for item in rem_cols] # This one only works once! It will throw an error if you run it again.


# Load the files, set the column names as int for easy access, and make a list of the variables we are creating.

# In[10]:


materials = []
for y in mats:
    if y == 'csi':
        for x in material_list_csi:
            globals()['%s_%s' % (y, x)] = pd.read_csv('{}_wasteEOL_{}.csv'.format(y, x), usecols =cols) # Load files
            globals()['%s_%s' % (y, x)].columns = globals()['%s_%s' % (y, x)].columns.astype('int')
            materials.append(globals()['%s_%s' % (y, x)])
    elif y == 'cdte':
        for x in material_list_cdte:
            globals()['%s_%s' % (y, x)] = pd.read_csv('{}_wasteEOL_{}.csv'.format(y, x), usecols =cols)
            globals()['%s_%s' % (y, x)].columns = globals()['%s_%s' % (y, x)].columns.astype('int')
            materials.append(globals()['%s_%s' % (y, x)])


# ## 2. Calculate total waste per material

# Sum all years to generate a `total waste` column.

# In[20]:





# In[21]:


for material in materials:
    material['total waste'] = material.loc[:, :].sum(axis=1)


# Get the names of the created variables, create a list and then generate a dataframe with the total generated waste by material.

# The following cell prints all the variables generated in this notebook, I copy and pasted the ones I am interested. This would be helpful to automate the total sum of wastes.
# 

# In[23]:


vnames = [name for name in globals()] 
print(vnames)


# In[45]:


material_vars = ['csi_glass', 'csi_silicon', 'csi_silver', 'csi_copper', 'csi_aluminium_frames', 'csi_encapsulant', 'csi_backsheet', 'csi_Module', 'cdte_cadmium', 'cdte_tellurium', 'cdte_glass_cdte', 'cdte_aluminium_frames_cdte', 'cdte_Module', 'cdte_copper_cdte', 'cdte_encapsulant_cdte']


# In[46]:


total_wastes = pd.DataFrame()


# In[47]:


total_wastes['Material'] = material_vars


# In[48]:


material_vars[1]


# In[49]:


total_waste = []
for mats in range(len(material_vars)):
    total_waste.append(materials[mats]['total waste'].sum(axis=0))


# In[51]:


total_wastes['Total waste'] = total_waste


# ## 3. Calculate tonnes of recycled material per tonne of PV processed.

# Calculate total PV input (cSi + CdTe).

# In[77]:


total_wastes[total_wastes['Material'] == 'csi_Module']['Total waste']


# In[78]:


total_wastes[total_wastes['Material'] == 'cdte_Module']['Total waste']


# In[108]:


total_pv_waste = np.array(sum(total_wastes[total_wastes['Material'] == 'csi_Module']['Total waste'],                              total_wastes[total_wastes['Material'] == 'cdte_Module']['Total waste']))


# In[109]:


total_pv_waste


# In[88]:


total_wastes['Tonnes of waste per tonne of PV'] = total_wastes['Total waste'].divide(total_pv_waste[0])


# Now, we add a new column with the material-specific recycling efficiencies. Luckily we made a dictionary of these values in [Data Preprocess 1 Section 4.3.](./data_preprocess_1.ipynb)

# In[90]:


total_wastes['Recycling Efficiencies'] = [0.98, 0.95, 0.95, 0.95, 1, 1, 1, 0, 0.95, 0.95, 0.9, 1, 0, 0.95, 0.9]


# In[95]:


total_wastes['Tonnes of recycled material per tonne of PV'] =                            total_wastes['Tonnes of waste per tonne of PV'] *                            total_wastes['Recycling Efficiencies']


# In[96]:


total_wastes


# We assume that the material that is not recycled is landfilled. So let's calculate that!

# In[97]:


total_wastes['Tonnes of landfilled material per PV processed'] =                        total_wastes['Tonnes of waste per tonne of PV'] -                        total_wastes['Tonnes of recycled material per tonne of PV']


# Ignore the csi_Module and cdte_Modules. I should probably pop them out of the dataframe but for now I am keeping them for sanity check.

# In[98]:


total_wastes 


# Contaminated glass has to go to a special waste management, so let's put it in its own bin.

# In[137]:


tt_contaminated_glass = np.array(sum(total_wastes[total_wastes['Material'] == 'csi_glass']['Tonnes of landfilled material per PV processed'],                              total_wastes[total_wastes['Material'] == 'cdte_glass_cdte']['Tonnes of landfilled material per PV processed']))
tt_contaminated_glass


# Same goes with cadmium waste.

# In[152]:


tt_cadmium_waste = np.array(total_wastes[total_wastes['Material'] == 'cdte_cadmium']['Tonnes of landfilled material per PV processed'])


# In[153]:


tt_cadmium_waste


# Now let's calculate the rest of the waste:

# In[141]:


tt_all_waste = np.array(total_wastes['Tonnes of landfilled material per PV processed'].sum(axis=0))


# I substract 1 to the count to avoid counting the csi_Modules and cdte_Modules values.

# In[154]:


tt_other_waste = tt_all_waste - ttcadmium_waste - tt_contaminated_glass - 1


# In[155]:


tt_other_waste


# In[ ]:




