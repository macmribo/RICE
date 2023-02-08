#!/usr/bin/env python
# coding: utf-8

# ## Visualize What-If Scenarios

# In[1]:


from glob import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import re
re.compile('<title>(.*)</title>')

sns.set()


# In[11]:


problem = 'what-if_cui'
#problem = 'what-if_initial'


# ### Systematically collate plant data across scenarios

# In[ ]:





# In[12]:


pdata = []
for filename in sorted(glob(f"output/{problem}/*plants.csv")):
    matches = re.findall(r"_cap_([0.0-9.0]*)_cost_(\d+)", filename)[0]
    cap = float(matches[0])
    cost = int(matches[1])
    pld = pd.read_csv(filename)
    pld["filename"] = filename
    pld["Storage Limit (%)"] = cap*100
    pld["Storage Cost ($/tonne/yr)"] = cost
    pdata += [pld]
    
pdata = pd.concat(pdata)
display(pdata.describe().T)


# ### Systematically collate plant output data across scenarios

# In[14]:


ddata = []
for filename in sorted(glob(f"output/{problem}/*outputs.csv")):
    matches = re.findall(r"_cap_([0.0-9.0]*)_cost_(\d+)", filename)[0]
#     cap = int(float(matches[0]))
#     cost = int(matches[1])
    cap = float(matches[0])
    cost = int(matches[1])
#     print(matches,'   |   ',cap, cost)
    dd = pd.read_csv(filename)
    dd["filename"] = filename
    dd["Storage Limit (%)"] = cap*100
    dd["Storage Cost ($/tonne/yr)"] = cost
    ddata += [dd]
    
ddata = pd.concat(ddata)
display(ddata.describe().T)


# ### Systematically collate transport data across scenarios

# In[15]:


tdata = []
for filename in sorted(glob(f"output/{problem}/*tr.csv")):
    matches = re.findall(r"_cap_([0.0-9.0]*)_cost_(\d+)", filename)[0]
    cap = float(matches[0])
    cost = int(matches[1])
    td = pd.read_csv(filename)
    td["filename"] = filename
    td["Storage Limit (%)"] = cap*100
    td["Storage Cost ($/tonne/yr)"] = cost
    tdata += [td]
    
tdata = pd.concat(tdata)
display(tdata.describe().T)


# ### Prepare data for visualization

# In[16]:



#Battery amount and Acquisition cost 
batteries_tonne = pdata['amount processed (tonne)'].sum()
acquisition = 358 # $/tonne

# total plant cost
pin = pdata.groupby([
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)"
]).sum()[
    "total cost ($)"
].reset_index().pivot(
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)",
    "total cost ($)",
)


# Transport cost
tin = tdata.groupby([
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)"
]).sum()['transportation cost ($)'].reset_index().pivot(
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)",
    "transportation cost ($)",
)

# disposal cost
din = ddata.groupby([
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)"
]).sum()['disposal cost ($)'].reset_index().pivot(
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)",
    "disposal cost ($)",
)

# amount of battery recycled
bat_amt = pdata.groupby([
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)"
]).sum()[
    "amount processed (tonne)"
].reset_index().pivot(
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)",
    "amount processed (tonne)",
)


# ### Specific Recycling cost

# In[17]:


sum_per_battery = ((pin+tin+din)/bat_amt) + acquisition 


fig, ax = plt.subplots(
    figsize=(6,5),
)
sns.heatmap(
    sum_per_battery,
    annot=True,
    fmt=",.0f",
    cbar=False,
    linewidths=0.25,
);
plt.tight_layout()
fig.savefig(f"figures/{problem}/HeatMapCostPerBat.pdf", dpi=300)
# fig.savefig("figures/whatif/HeatMapCostPerBat.png", dpi=300)


# ### Plant Utilization

# In[8]:


summary = pdata.groupby([
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)"
]).mean()[
    "utilization factor (%)"
].reset_index().pivot(
    "Storage Limit (%)",
    "Storage Cost ($/tonne/yr)",
    "utilization factor (%)",
)

fig, ax = plt.subplots(
    figsize=(6,5),
)
sns.heatmap(
    summary,
    annot=True,
    fmt=",.0f",
    cbar=False,
    linewidths=0.25,
);
plt.tight_layout()

fig.savefig(f"figures/{problem}/HeatMapUtilization.pdf", dpi=300)
# fig.savefig("figures/whatif/HeatMapCostPerBat.png", dpi=300)


# In[ ]:





# In[ ]:




