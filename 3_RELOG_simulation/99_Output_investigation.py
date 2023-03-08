#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from datetime import datetime
import shutil
from distutils.dir_util import copy_tree

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# In[2]:


cwd= os.getcwd()


# ### Explore differences between CASE0_v4 and CASE0_v5

# In[3]:


output_folder = os.path.join(cwd, 'output')


# In[42]:


v4 = pd.read_csv(os.path.join(output_folder, '20230303_CASE0_v4', 'plants.csv'))
v5 = pd.read_csv(os.path.join(output_folder, '20230303_CASE0_v5', 'plants.csv'))


# In[43]:


print('Simulation v4 with 14314 tonnes of waste has {} storage facilities.'.format(len(v4)/26))


# In[44]:


print('Simulation v5 with 7157 tonnes of waste has {} storage facilities.'.format(len(v5)/26))


# In[48]:


v4['plant type'].unique()


# In[5]:


man_plants = pd.read_csv(os.path.join(output_folder, '20230306_CASE0_Manufacturing_v1', 'plants.csv'))
man_products = pd.read_csv(os.path.join(output_folder, '20230306_CASE0_Manufacturing_v1', 'products.csv'))
man_transportation = pd.read_csv(os.path.join(output_folder, '20230306_CASE0_Manufacturing_v1', 'transportation.csv'))


# In[ ]:


import seaborn as sns
import re

rc = {'figure.figsize':(5,5),
      'axes.facecolor':'white',
      'axes.grid' : True,
      'grid.color': '1',
      #'font.family':'Times New Roman',
      'font.size' : 9}
plt.rcParams.update(rc)

#sns.set_style("ticks", rc={"axes.edgecolor": ".0", "axes.facecolor":"none"})
palette = sns.color_palette('pastel')


# In[82]:


y_axis_range = list(range(2025, 2051))*5


# In[70]:


mask = man_plants['location name'].str.contains('Port', case=False, na=False)


# In[79]:


fig = sns.lineplot(x="year", y="amount processed (tonne)",
             hue="location name",
             data=man_plants, palette=palette)
fig.set(xlabel='', ylabel='Amount processed [tonne]');
#fig.set_xticklabels(y_axis_range)


# In[ ]:





# In[ ]:




