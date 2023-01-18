#!/usr/bin/env python
# coding: utf-8

# In[13]:


import json
import numpy as np
import os
import pandas as pd


# In[2]:


conservative_file = 'input/conservative/locodata_ultra.json'
optimistic_file = 'input/optimistic/locodata_ultra.json'


# In[31]:


with open(conservative_file) as f:
    data_c = json.load(f)
    
with open(optimistic_file) as f:
    data_o = json.load(f)


# In[46]:


data_d_loc = data_c['plants']['Ultra Plant']['locations']


# In[56]:


locs = []
for location in data_d_loc:
    locs.append(location)
    


# In[57]:


for locations in locs:
    for material in data_d_loc['disposal']:
        


# In[58]:


# Given nested dictionary
list = [
   {
      "Fruit": [{"Price": 15.2, "Quality": "A"},
         {"Price": 19, "Quality": "B"},
         {"Price": 17.8, "Quality": "C"},
      ],
      "Name": "Orange"
   },
   {
      "Fruit": [{"Price": 23.2, "Quality": "A"},
         {"Price": 28, "Quality": "B"}
      ],
      "Name": "Grapes"
   }
]

rows = []

# Getting rows


# In[59]:


for data in list:
    data_row = data['Fruit']
    print(data_row)
    n = data['Name']
    print(n)
    for row in data_row:
        row['Name'] = n
        print(row['Name'])
        rows.append(row)
        print(rows)


# In[60]:


df = pd.DataFrame(rows)

df = df.pivot_table(index='Name', columns=['Quality'],
               values=['Price']).reset_index()
print(df)


# In[ ]:




