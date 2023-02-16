#!/usr/bin/env python
# coding: utf-8

# # Data Preprocess 3

# This journal explains how to filter the recycling plants candidate locations according to Energy Justice metrics, leveraging [EJScreen: Environmental Justice Screening and Mapping Tool](https://www.epa.gov/ejscreen), more specifically, we will be using [EJScreen Report API](https://ejscreen.epa.gov/mapper/ejscreenapi.html).

# ## 0. Load necessary libraries

# In[1]:


import numpy as np
import pandas as pd
import os,sys
import matplotlib.pyplot as plt
from pathlib import Path

import requests # to get api data


# In[ ]:





# ## 1. Load the file to filter and add FIPS codes

# EJScreen API needs FIPS codes to access the EJ reports. So the first step is to load the file we want to use, in our case 'RELOG_import_data/CandidateLocations_CA.csv'.

# In[26]:


candidates_raw = pd.read_csv('RELOG_import_data/CandidateLocations_CA.csv')
candidates_lat_long = candidates_raw.drop(['name', 'area cost factor'], axis=1, inplace= False)


# In[27]:


candidates_lat_long


# In[33]:


fips_county_codes = []
fips_state_codes = []


# In[34]:


# Code from https://gis.stackexchange.com/questions/294641/python-code-for-transforming-lat-long-into-fips-codes
import requests
import urllib

#Encode parameters 
for lat, lon in candidates_lat_long.itertuples(index=False):
    params = urllib.parse.urlencode({'latitude': lat, 'longitude':lon, 'format':'json'})
    #Contruct request URL
    url = 'https://geo.fcc.gov/api/census/block/find?' + params

    #Get response from API
    response = requests.get(url)

    #Parse json in response
    data = response.json()
    fips_county_codes.append(data['County']['FIPS'])
    fips_state_codes.append(data['State']['FIPS'])
    #Print FIPS code


# In[37]:


candidates_lat_long['fips_county'] = fips_county_codes
candidates_lat_long['fips_state'] = fips_state_codes


# Let's reshape the dataframe to have the names back and all the  EJ indices in the dataframe related to the fips codes.

# In[60]:


ej_candidates = candidates_lat_long.copy()


# In[62]:


ej_candidates['name'] = candidates_raw['name']


# Now, I am going to query a random fips code to get the column names.

# In[66]:


ej_query = requests.get(f'https://ejscreen.epa.gov/mapper/ejscreenRESTbroker.aspx?namestr=Pickens County&geometry=&distance=&unit=9035&areatype=county&areaid=35003&f=pjson')
ej_query_keys = [keys for keys in ej_query.json().keys()]


# In[68]:


ej_candidates[ej_query_keys] = np.nan


# In[76]:


ej_query_values = [value for value in ej_query.json().values()]


# In[87]:


ej_candidates.loc[ej_candidates['fips_county'] == '35003', 'RAW_D_MINOR':] = ej_query_values


# In[89]:


ej_candidates.loc[ej_candidates['fips_county'] == '35003', 'RAW_D_MINOR':]


# In[90]:


ej_candidates[ej_query_keys][ej_candidates['fips_county'] == '35003']


# In[91]:


for fips in fips_list:
    ej_query = requests.get(f'https://ejscreen.epa.gov/mapper/ejscreenRESTbroker.aspx?namestr=Pickens County&geometry=&distance=&unit=9035&areatype=county&areaid={fips}&f=pjson')
    ej_query_values = [value for value in ej_query.json().values()]
    ej_candidates.loc[ej_candidates['fips_county'] == f'{fips}', 'RAW_D_MINOR':] = ej_query_values
    


# There are some percentages values that prevent me from making these numbers floats, so I am going to get rid of the %, I know what is percentage and what is percentile based on the 'EJ_json_dictionary_help.xlsx' file in the folder 'miscellaneous', you can also see a sample of these values from the EJ report screen capture [here](miscellaneous/json_variables_explained.png).

# In[100]:


ej_candidates = ej_candidates.replace({'%':''}, regex=True)
ej_candidates = ej_candidates.replace('N/A',np.nan)


# In[121]:


ej_candidates.loc[:, 'RAW_D_MINOR':'N_P_UST'] = ej_candidates.loc[:, 'RAW_D_MINOR':'N_P_UST'].astype(float)
ej_candidates.loc[:, 'totalPop':'areaid'] = ej_candidates.loc[:, 'totalPop':'areaid'].astype(float)


# In[122]:


ej_candidates.info()


# In[116]:


ej_candidates['name']


# In[132]:


plt.bar("name", ("N_D_MINOR", "N_D_MINOR_PER"), data = ej_candidates)
plt.xlabel("County")
plt.ylabel("Population")
#plt.title("")
plt.show()


# In[129]:


ej_candidates['N_D_MINOR_PER']


# In[ ]:




