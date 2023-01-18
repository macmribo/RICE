#!/usr/bin/env python
# coding: utf-8

# # What-if scenario file generator

# ### Load necessary libraries

# In[1]:


import json
import numpy as np
import os


# ### Create the conservative what if scenario files

# In[2]:


conservative_file = 'input/conservative/locodata_ultra.json'
optimistic_file = 'input/optimistic/locodata_ultra.json'


# In[7]:


conservative_whatif = 'input/whatif-conservative/'
optimistic_whatif = 'input/whatif-optimistic/'


# In[ ]:


with open(conservative_file) as f:
    data_c = json.load(f)
    
with open(optimistic_file) as f:
    data_o = json.load(f)


# ### Arrays with the parameter changes

# In[4]:


storage_cost = np.array([0.0, 50, 100, 150, 300, 600])
storage_cap = np.array([0.25, 0.5, 1, 2, 4])


# ### Change the original file and save the different scenarios

# #### Conservative

# In[8]:


for cap in storage_cap:
    for cost in storage_cost:
        with open(conservative_file) as f:
            data = json.load(f)
        for locations in data['plants']['Ultra Plant']['locations']:
            data['plants']['Ultra Plant']['locations'][locations]['storage']['limit (tonne)'] = np.multiply(data['plants']['Ultra Plant']['locations'][locations]['storage']['limit (tonne)'],cap).tolist()
            data['plants']['Ultra Plant']['locations'][locations]['storage']['cost ($/tonne)'] = np.array([cost for item in range(len(data['plants']['Ultra Plant']['locations'][locations]['storage']['cost ($/tonne)']))]).tolist()
        with open(os.path.join(conservative_whatif, 'storage_ultra_cap_' +str(cap)+ '_cost_'+str(cost)+'.json'), 'w') as f:
                json.dump(data, f, indent=2)      


# #### Optimistic

# In[9]:


for cap in storage_cap:
    for cost in storage_cost:
        with open(conservative_file) as f:
            data = json.load(f)
        for locations in data['plants']['Ultra Plant']['locations']:
            data['plants']['Ultra Plant']['locations'][locations]['storage']['limit (tonne)'] = np.multiply(data['plants']['Ultra Plant']['locations'][locations]['storage']['limit (tonne)'],cap).tolist()
            data['plants']['Ultra Plant']['locations'][locations]['storage']['cost ($/tonne)'] = np.array([cost for item in range(len(data['plants']['Ultra Plant']['locations'][locations]['storage']['cost ($/tonne)']))]).tolist()
        with open(os.path.join(optimistic_whatif, 'storage_ultra_cap_' +str(cap)+ '_cost_'+str(cost)+'.json'), 'w') as f:
                json.dump(data, f, indent=2)      


# #### Small case

# In[ ]:


small_case_file = 'input/smallproblem/InputPipelineData.json'
small_case_whatif = 'input/whatif-smallproblem/'


# In[ ]:


for cap in storage_cap:
    for cost in storage_cost:
        with open(small_case_file) as f:
            data_s = json.load(f)
        for locations in data_s['plants']['Ultra Plant']['locations']:
            data_s['plants']['Ultra Plant']['locations'][locations]['storage']['limit (tonne)'] = np.multiply(data_s['plants']['Ultra Plant']['locations'][locations]['storage']['limit (tonne)'],cap).tolist()
            data_s['plants']['Ultra Plant']['locations'][locations]['storage']['cost ($/tonne)'] = np.array([cost for item in range(len(data_s['plants']['Ultra Plant']['locations'][locations]['storage']['cost ($/tonne)']))]).tolist()
        with open(os.path.join(small_case_whatif, 'storage_ultra_cap_' +str(cap)+ '_cost_'+str(cost)+'.json'), 'w') as f:
                json.dump(data_s, f, indent=2)    


# In[ ]:




