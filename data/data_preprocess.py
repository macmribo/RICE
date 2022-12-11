#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os,sys
import matplotlib.pyplot as plt
from pathlib import Path

from geopy.geocoders import Nominatim
from geopy.point import Point
# initialize Nominatim API
geolocator = Nominatim(user_agent="geoapiExercises")


# ### Get the GIS locations from the latitude and longitude

# Filter the USA areas.

# In[2]:


GISfile = str(Path().resolve().parent.parent.parent / 'gis_centroid_n.xlsx')
GIS = pd.read_excel(GISfile)
GIS_us = GIS[GIS.country == 'USA']
GIS_us.reset_index(inplace=True)
GIS_us = GIS_us.iloc[0:134]


# In[3]:


def city_state_country(row):
    # I map latitude and longitude with actual names of those places.
    coord = f"{row['lat']}, {row['long']}"
    location = geolocator.reverse(coord, exactly_one=True)
    address = location.raw['address']
    city = address.get('city', '')
    county = address.get('county', '')
    state = address.get('state', '')
    country = address.get('country', '')
    county_state = address.get('county', 'state')
    row['city'] = city
    row['county'] = county
    row['state'] = state
    row['country'] = country
    row['location'] = county_state
    return row


# In[4]:


# This one takes a long time!! Applty the previous function to obtain the names of the locations.
GIS = GIS.apply(city_state_country, axis=1)


# In[6]:


GIS_us_long_lat = GIS_us[['long', 'lat']]
GIS_us_id = GIS_us[['id']]


# In[7]:


cwd = os.getcwd()
pvice_folder = os.path.join(cwd, 'PV_ICE_outputs')


# In[8]:


csi_eol = pd.read_csv(os.path.join(pvice_folder, 'PVICE_RELOG_PCA_cSi_WasteEOL.csv'), index_col='year')
cdte_eol = pd.read_csv(os.path.join(pvice_folder, 'PVICE_RELOG_PCA_CdTe_WasteEOL.csv'), index_col='year')


# In[9]:


print('We have %s collection centers.' % len(GIS_us))


# Now I need to select the columns and separate them by material, then add a column identifying the locations. Ideally, I need to populate the table for the material

# In[10]:


material_list_csi = ['glass', 'silicon', 'silver', 'copper', 'aluminium_frames', 'encapsulant', 'backsheet', 'Module']
material_list_cdte = ['cadmium', 'telluride', 'glass_cdte', 'aluminium_frames_cdte', 'Module']


# In[11]:


nums = np.arange(1,42)
years = np.arange(2010,2051)
years_dict = {nums[i]: years[i] for i in range(len(nums))}


# In[15]:


mats = ['csi', 'cdte']


# In[39]:


for y in mats:
    if y == 'csi':
        for x in material_list_csi:
            globals()['%s_%s_sel' % (y, x)] = [col for col in globals()['%s_eol' % y].columns if x in col]
            globals()['%s_%s' % (y, x)] = csi_eol.filter(globals()['%s_%s_sel' % (y, x)], axis=1)
            globals()['%s_%s' % (y, x)] = globals()['%s_%s' % (y, x)].transpose()
            globals()['%s_%s' % (y, x)].reset_index(inplace=True)
            globals()['%s_%s' % (y, x)] = pd.concat([globals()['%s_%s' % (y, x)], GIS_us_long_lat], axis=1, ignore_index=True)
            globals()['%s_%s' % (y, x)].rename(columns = years_dict, inplace=True)
            globals()['%s_%s' % (y, x)].rename(columns = {42:'PCA area'}, inplace=True)
            globals()['%s_%s' % (y, x)].rename(columns = {43:'longitude', 44:'latitude'}, inplace=True)
            globals()['%s_%s' % (y, x)]['total waste'] = globals()['%s_%s' % (y, x)].loc[:, 2010:2050].sum(axis=1)
            globals()['%s_%s' % (y, x)].to_csv('{}_wasteEOL_{}.csv'.format(y, x))
            print(y+x)
    elif y == 'cdte':
        for x in material_list_cdte:
            globals()['%s_%s_sel' % (y, x)] = [col for col in globals()['%s_eol' % y].columns if x in col]
            globals()['%s_%s' % (y, x)] = cdte_eol.filter(globals()['%s_%s_sel' % (y, x)], axis=1)
            globals()['%s_%s' % (y, x)] = globals()['%s_%s' % (y, x)].transpose()
            globals()['%s_%s' % (y, x)].reset_index(inplace=True)
            globals()['%s_%s' % (y, x)] = pd.concat([globals()['%s_%s' % (y, x)], GIS_us_long_lat], axis=1, ignore_index=True)
            globals()['%s_%s' % (y, x)].rename(columns = years_dict, inplace=True)
            globals()['%s_%s' % (y, x)].rename(columns = {42:'PCA area'}, inplace=True)
            globals()['%s_%s' % (y, x)].rename(columns = {43:'longitude', 44:'latitude'}, inplace=True)
            globals()['%s_%s' % (y, x)]['total waste'] = globals()['%s_%s' % (y, x)].loc[:, 2010:2050].sum(axis=1)
            globals()['%s_%s' % (y, x)].to_csv('{}_wasteEOL_{}.csv'.format(y, x))
            print(y+x)


# ### Shankey Diagram

# For the Shankey Diagram, I need:
# 1) Get the total waste (cSi + CdTe).
# 2) Get the % of cSi and CdTe (bin1).
# 3) Get the % of each material in cSi and CdTe.
# 4) Add all those materials into material bins .
# 5) Pass them by an intermediate bin with the recycling process an d  their recycling yield.
# 6) Add all those materials and check how much of each could contribute to revenue based on their value.
# 
# * The 100% is 1 tonne of PV waste.

# ### 1. Total waste

# In[ ]:


total_pv_waste = 


# In[70]:


csi_waste = csi_Module['total waste'].sum()
cdte_waste = cdte_Module['total waste'].sum()
all_waste = csi_waste + cdte_waste
print(f'There are {all_waste:.2f} tonnes of PV waste (that\'s {all_waste/1000000:.2f} million metric tonnes).')
print(f'There are {csi_waste:.2f} tonnes of cSi, and {cdte_waste:.2f} tonnes of CdTe.')
perc_csi = csi_waste/all_waste
perc_cdte = cdte_waste/all_waste
print(f'Of all the waste, {perc_csi*100:.2f}% is cSi, and {perc_cdte*100:.2f}% is CdTe.')


# In[ ]:





# In[ ]:


import plotly.graph_objects as go

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["PV Waste", "A2", "B1", "B2", "C1", "C2"],
      color = "blue"
    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2]
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()


# In[ ]:





# In[ ]:





# In[ ]:


from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})

import plotly.express as px

fig = px.choropleth_mapbox(df, geojson=counties, locations='fips', color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'unemp':'unemployment rate'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()


# In[ ]:





# In[ ]:




