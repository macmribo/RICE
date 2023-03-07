#!/usr/bin/env python
# coding: utf-8

# In[39]:


import os
from datetime import datetime
import shutil
from distutils.dir_util import copy_tree

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# In[40]:


cwd= os.getcwd()


# ### Explore differences between CASE0_v4 and CASE0_v5

# In[41]:


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


# In[46]:


[storage for storage in v5['amount in storage (tonne)'] if storage != 0]


# In[ ]:




