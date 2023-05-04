#!/usr/bin/env python
# coding: utf-8

# In[68]:


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import re


# In[69]:


plants = pd.read_csv('plants.csv')


# In[70]:


plants.head()


# In[71]:


plants_copy = plants.copy()


# In[72]:


states = []
for location in plants['location name']:
    states.append(location.split(', ')[2])


# In[73]:


plants_copy['state'] = states


# In[74]:


plt.scatter(plants_copy['location name'], plants_copy['total cost ($)'] )
plt.xticks(rotation=90)
plt.show()


# In[75]:


plants_by_loc = plants_copy.groupby(by='location name').sum()


# In[76]:


fig, ax = plt.subplots()
ax.stem(plants_by_loc.index, plants_by_loc['total cost ($)'])
plt.xticks(rotation=90)
plt.show()


# In[77]:


plants_by_loc_year = plants_copy.groupby(by=['location name', 'year']).sum()


# In[88]:


plants_by_loc_year.loc[plants_by_loc_year.index[0:26]]['utilization factor (%)']


# In[96]:


plants_by_loc_year


# In[100]:


[location for location in plants_by_loc_year.loc[]:]


# In[93]:


[location for location in plants_by_loc_year.get_level_values('location name')]


# In[ ]:




