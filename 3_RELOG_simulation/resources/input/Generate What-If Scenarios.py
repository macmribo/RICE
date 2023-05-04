#!/usr/bin/env python
# coding: utf-8

# ## Generate What-if Scenarios

# In[3]:


import json
max_capacity = 5628

problem = '20230301_CASE0_v3' #paste here the simulation name (folder in input) you want to run.


# In[4]:


with open(f"{problem}/case.json") as infile:
    case = json.load(infile)
    t = case["parameters"]["time horizon (years)"]
    for cap in [0.25, 0.5, 1, 2, 4]: # Do not ad cap '0' or the HPC will not find a solution for the '0' cap scenarios.
        for cost in [25, 50, 100, 150, 300, 600]:
            for plant in case["plants"].values():
                for loc in plant["locations"].values():
                    loc["storage"]["cost ($/tonne)"] = [cost for _ in range(t)]
                    loc["storage"]["limit (tonne)"] = cap * max_capacity
            with open(
                f"what-if_{problem}/storage_ultra_cap_{cap}_cost_{cost}.json",
                "w",
            ) as outfile:
                json.dump(case, outfile, indent=2)


# In[ ]:




