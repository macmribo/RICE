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


# ---
# ## 1. Generate waste files

# ### 1.1. Get the GIS locations from the latitude and longitude

# Filter the USA areas.

# In[2]:


GISfile = str(Path().resolve().parent.parent.parent / 'gis_centroid_n.xlsx')
GIS = pd.read_excel(GISfile)
GIS_us = GIS[GIS.country == 'USA']
GIS_us.reset_index(inplace=True)
GIS_us = GIS_us.iloc[0:134]


# In[4]:


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


# In[5]:


# This one takes a long time!! Apply the previous function to obtain the names of the locations.
GIS = GIS.apply(city_state_country, axis=1)


# In[157]:


GIS


# In[155]:


GIS_us_long_lat = GIS_us[['long', 'lat']]
GIS_us_id = GIS_us[['id']]


# ### 1.2. Correlate GIS longitude and latitude with FIPS codes for the map diagram

# In[431]:


fips_county_codes = []
fips_state_codes = []


# In[432]:


# Code from https://gis.stackexchange.com/questions/294641/python-code-for-transforming-lat-long-into-fips-codes
import requests
import urllib

#Encode parameters 
for lon, lat in GIS_us_long_lat.itertuples(index=False):
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


# In[433]:


data


# In[434]:


GIS_us_long_lat['fips_county'] = fips_county_codes
GIS_us_long_lat['fips_state'] = fips_state_codes


# In[435]:


GIS_us_long_lat


# ### 1.3. Separate the PV ICE output and create individual material file

# In[436]:


cwd = os.getcwd()
pvice_folder = os.path.join(cwd, 'PV_ICE_outputs')


# In[437]:


csi_eol = pd.read_csv(os.path.join(pvice_folder, 'PVICE_RELOG_PCA_cSi_WasteEOL.csv'), index_col='year')
cdte_eol = pd.read_csv(os.path.join(pvice_folder, 'PVICE_RELOG_PCA_CdTe_WasteEOL.csv'), index_col='year')


# In[438]:


print('We have %s collection centers.' % len(GIS_us))


# Now I need to select the columns and separate them by material, then add a column identifying the locations. Ideally, I need to populate the table for the material

# In[439]:


material_list_csi = ['glass', 'silicon', 'silver', 'copper', 'aluminium_frames', 'encapsulant', 'backsheet', 'Module']
material_list_cdte = ['cadmium', 'tellurium', 'glass_cdte', 'aluminium_frames_cdte', 'Module', 'copper_cdte', 'encapsulant_cdte']


# In[440]:


nums = np.arange(1,42)
years = np.arange(2010,2051)
years_dict = {nums[i]: years[i] for i in range(len(nums))}


# In[441]:


mats = ['csi', 'cdte']


# In[442]:


GIS_us_long_lat


# In[443]:


for y in mats:
    if y == 'csi':
        for x in material_list_csi:
            globals()['%s_%s_sel' % (y, x)] = [col for col in globals()['%s_eol' % y].columns if x in col]
            globals()['%s_%s' % (y, x)] = csi_eol.filter(globals()['%s_%s_sel' % (y, x)], axis=1)
            globals()['%s_%s' % (y, x)] = globals()['%s_%s' % (y, x)].transpose()
            globals()['%s_%s' % (y, x)].reset_index(inplace=True)
            globals()['%s_%s' % (y, x)] = pd.concat([globals()['%s_%s' % (y, x)], GIS_us_long_lat], axis=1, ignore_index=True)
            globals()['%s_%s' % (y, x)].rename(columns = years_dict, inplace=True)
           # globals()['%s_%s' % (y, x)].rename(columns = {42:'PCA area'}, inplace=True)
            globals()['%s_%s' % (y, x)].rename(columns = {42:'longitude', 43:'latitude', 44:'FIPS'}, inplace=True)
            globals()['%s_%s' % (y, x)]['total waste'] = globals()['%s_%s' % (y, x)].loc[:, 2010:2050].sum(axis=1)
            globals()['%s_%s' % (y, x)].to_csv('{}_wasteEOL_{}.csv'.format(y, x))
    elif y == 'cdte':
        for x in material_list_cdte:
            globals()['%s_%s_sel' % (y, x)] = [col for col in globals()['%s_eol' % y].columns if x in col]
            globals()['%s_%s' % (y, x)] = cdte_eol.filter(globals()['%s_%s_sel' % (y, x)], axis=1)
            globals()['%s_%s' % (y, x)] = globals()['%s_%s' % (y, x)].transpose()
            globals()['%s_%s' % (y, x)].reset_index(inplace=True)
            globals()['%s_%s' % (y, x)] = pd.concat([globals()['%s_%s' % (y, x)], GIS_us_long_lat], axis=1, ignore_index=True)
            globals()['%s_%s' % (y, x)].rename(columns = years_dict, inplace=True)
           # globals()['%s_%s' % (y, x)].rename(columns = {42:'PCA area'}, inplace=True)
            globals()['%s_%s' % (y, x)].rename(columns = {42:'longitude', 43:'latitude', 44:'FIPS'}, inplace=True)
            globals()['%s_%s' % (y, x)]['total waste'] = globals()['%s_%s' % (y, x)].loc[:, 2010:2050].sum(axis=1)
            globals()['%s_%s' % (y, x)].to_csv('{}_wasteEOL_{}.csv'.format(y, x))


# ## 2. Make the initial amounts file

# Here I will be generating the file that has the waste initial amounts according to RELOG's template (Initial amounts - Template.csv).
# ![image.png](Initial_amounts_temp.png)
# 
# I have two options:
# 1) Add at the wastes and then do the processing to create ONE template of initial amounts.
# 2) Create THREE templates, two with CdTe and cSi separated, and then create another one summing the previous two.
# 
# I am going to do option 2, that way if we decide to generate a separate RELOG scenario with one or the other technology, we have already separate files. I am also  going to create the files for individual materials in case they update the software so we also have material timeseries.

# ### 2.1. Load the waste files that we just generated.

# **LOAD OPTION 1:** If you have run Section 1 cells, fetch the data as csi_Module and cdte_Module. I make a copy of these files since I will be changing them considerably.

# In[575]:


csi_Module_ia = csi_Module.copy()
csi_glass_ia = csi_glass.copy()
csi_silicon_ia = csi_silicon.copy()
csi_silver_ia = csi_silver.copy()
csi_copper_ia = csi_copper.copy()
csi_aluminium_frames_ia = csi_aluminium_frames.copy()
csi_encapsulant_ia = csi_encapsulant.copy()
csi_backsheet_ia = csi_backsheet.copy()


cdte_Module_ia = cdte_Module.copy()
cdte_cadmium_ia = cdte_cadmium.copy()
cdte_tellurium_ia = cdte_tellurium.copy()
cdte_glass_cdte_ia = cdte_glass_cdte.copy()
cdte_aluminium_frames_cdte_ia = cdte_aluminium_frames_cdte.copy()
cdte_copper_cdte_ia = cdte_copper_cdte.copy()
cdte_encapsulant_cdte_ia = cdte_encapsulant_cdte.copy()

# 'ia' stands for initial amounts


# **LOAD OPTION 2:** If you have run Section 1 cells, use function load_csv with the corresponding file name.

# In[546]:


# Uncomment if you need this option
# csi_Module = pd.read_csv('csi_wasteEOL_Module.csv')
# cdte_Module = pd.read_csv('cdte_wasteEOL_Module.csv')


# ### 2.2. Drop unnecessary columns

# Drop the 0, 2010 (there is no waste here), FIPS, 45, longitude, latitude and total waste columns. Then I insert the 'name' row and then move longitude and latitude rows

# In[576]:


csi_Module_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_glass_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_silicon_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_silver_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_copper_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_aluminium_frames_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_encapsulant_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_backsheet_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.


# In[577]:


cdte_Module_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_cadmium_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_tellurium_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_glass_cdte_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.)
cdte_aluminium_frames_cdte_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_copper_cdte_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_encapsulant_cdte_ia.drop([0, 2010, 'FIPS', 45, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.


# ### 2.3. Add the name locations, latitude and longitude with the right names to the right position.

# I take the location file from GIS.

# In[578]:


GIS_usa = GIS[GIS.country == 'United States']
GIS_usa.reset_index(inplace=True)
GIS_usa = GIS_usa.iloc[0:134] # I slice it until 142 because the next locations are not in ReEDS.


# In[579]:


csi_Module_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_Module_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_Module_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_glass_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_glass_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_glass_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_silicon_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_silicon_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_silicon_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_silver_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_silver_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_silver_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_copper_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_copper_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_copper_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_aluminium_frames_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_aluminium_frames_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_aluminium_frames_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_encapsulant_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_encapsulant_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_encapsulant_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_backsheet_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
csi_backsheet_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_backsheet_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 


# In[580]:


cdte_Module_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_Module_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_Module_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_cadmium_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_cadmium_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_cadmium_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_tellurium_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_tellurium_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_tellurium_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_glass_cdte_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_glass_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_glass_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_aluminium_frames_cdte_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_aluminium_frames_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_aluminium_frames_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_copper_cdte_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_copper_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_copper_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_encapsulant_cdte_ia.insert(0, 'name', GIS_usa[['location']]) # Run this one only once or it will throw an error.
cdte_encapsulant_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_encapsulant_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 


# #### 2.3.1 (Optional/to be decided) Add accumulated waste until year 2023

# In[581]:


csi_Module_ia_sumyears = csi_Module_ia.loc[:, 2011:2023].sum(axis=1)
csi_glass_ia_sumyears = csi_glass_ia.loc[:, 2011:2023].sum(axis=1)
csi_silicon_ia_sumyears = csi_silicon_ia.loc[:, 2011:2023].sum(axis=1)
csi_silver_ia_sumyears = csi_silver_ia.loc[:, 2011:2023].sum(axis=1)
csi_copper_ia_sumyears = csi_copper_ia.loc[:, 2011:2023].sum(axis=1)
csi_aluminium_frames_ia_sumyears = csi_aluminium_frames_ia.loc[:, 2011:2023].sum(axis=1)
csi_encapsulant_ia_sumyears = csi_encapsulant_ia.loc[:, 2011:2023].sum(axis=1)
csi_backsheet_ia_sumyears = csi_backsheet_ia.loc[:, 2011:2023].sum(axis=1)



cdte_cadmium_ia_sumyears = cdte_cadmium_ia.loc[:, 2011:2023].sum(axis=1)
cdte_tellurium_ia_sumyears = cdte_tellurium_ia.loc[:, 2011:2023].sum(axis=1)
cdte_glass_cdte_ia_sumyears = cdte_glass_cdte_ia.loc[:, 2011:2023].sum(axis=1)
cdte_aluminium_frames_cdte_ia_sumyears = cdte_aluminium_frames_cdte_ia.loc[:, 2011:2023].sum(axis=1)
cdte_copper_cdte_ia_sumyears = cdte_copper_cdte_ia.loc[:, 2011:2023].sum(axis=1)
cdte_encapsulant_cdte_ia_sumyears = cdte_encapsulant_cdte_ia.loc[:, 2011:2023].sum(axis=1)


# In[ ]:


csi_Module_ia
csi_glass_ia
csi_silicon_ia
csi_silver_ia
csi_copper_ia
csi_aluminium_frames_ia
csi_encapsulant_ia
csi_backsheet_ia

cdte_Module_ia
cdte_cadmium_ia
cdte_tellurium_ia
cdte_glass_cdte_ia
cdte_aluminium_frames_cdte_ia
cdte_copper_cdte_ia
cdte_encapsulant_cdte_ia


# In[ ]:





# In[ ]:





# Drop columns 2011 to 2022

# In[582]:


csi_Module_ia.drop(csi_Module_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_glass_ia.drop(csi_glass_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_silicon_ia.drop(csi_silicon_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_silver_ia.drop(csi_silver_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_copper_ia.drop(csi_copper_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_aluminium_frames_ia.drop(csi_aluminium_frames_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_encapsulant_ia.drop(csi_encapsulant_ia.loc[:, 2011:2023], inplace=True, axis=1)
csi_backsheet_ia.drop(csi_backsheet_ia.loc[:, 2011:2023], inplace=True, axis=1)

cdte_Module_ia.drop(cdte_Module_ia.loc[:, 2011:2023], inplace=True, axis=1)
cdte_cadmium_ia.drop(cdte_cadmium_ia.loc[:, 2011:2023], inplace=True, axis=1)
cdte_tellurium_ia.drop(cdte_tellurium_ia.loc[:, 2011:2023], inplace=True, axis=1)
cdte_glass_cdte_ia.drop(cdte_glass_cdte_ia.loc[:, 2011:2023], inplace=True, axis=1)
cdte_aluminium_frames_cdte_ia.drop(cdte_aluminium_frames_cdte_ia.loc[:, 2011:2023], inplace=True, axis=1)
cdte_copper_cdte_ia.drop(cdte_copper_cdte_ia.loc[:, 2011:2023], inplace=True, axis=1)
cdte_encapsulant_cdte_ia.drop(cdte_encapsulant_cdte_ia.loc[:, 2011:2023], inplace=True, axis=1)


# Insert the 2023 column that summed the waste between 2011 to 2023.

# In[583]:


csi_Module_ia.insert(3, 2023, csi_Module_ia_sumyears)
csi_glass_ia.insert(3, 2023, csi_glass_ia_sumyears)
csi_silicon_ia.insert(3, 2023, csi_silicon_ia_sumyears)
csi_silver_ia.insert(3, 2023, csi_silver_ia_sumyears)
csi_copper_ia.insert(3, 2023, csi_copper_ia_sumyears)
csi_aluminium_frames_ia.insert(3, 2023, csi_aluminium_frames_ia_sumyears)
csi_encapsulant_ia.insert(3, 2023, csi_encapsulant_ia_sumyears)
csi_backsheet_ia.insert(3, 2023, csi_backsheet_ia_sumyears)

cdte_Module_ia.insert(3, 2023, cdte_Module_ia_sumyears) 
cdte_cadmium_ia.insert(3, 2023, cdte_cadmium_ia_sumyears) 
cdte_tellurium_ia.insert(3, 2023, cdte_tellurium_ia_sumyears) 
cdte_glass_cdte_ia.insert(3, 2023, cdte_glass_cdte_ia_sumyears) 
cdte_aluminium_frames_cdte_ia.insert(3, 2023, cdte_aluminium_frames_cdte_ia_sumyears) 
cdte_copper_cdte_ia.insert(3, 2023, cdte_copper_cdte_ia_sumyears) 
cdte_encapsulant_cdte_ia.insert(3, 2023, cdte_encapsulant_cdte_ia_sumyears) 


# In[ ]:





# In[ ]:





# #### 2.3.1. Change years for amounts

# Change the column names as 'amount 1', 'amount 2', etc. I am not sure if it matters, but I am going to do it just in case!
# From 2023 to 2050, we have a total of 28 amounts.

# In[584]:


csi_Module_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_glass_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_silicon_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_silver_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_copper_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_aluminium_frames_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_encapsulant_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
csi_backsheet_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)

cdte_Module_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
cdte_cadmium_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
cdte_tellurium_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
cdte_glass_cdte_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
cdte_aluminium_frames_cdte_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
cdte_copper_cdte_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)
cdte_encapsulant_cdte_ia.set_axis(['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'], axis=1, inplace=True)


# ## 2.4. Add common dataframes and create a new ones

# Here I add cSi and CdTe modules as one, and common materials as one.

# In[586]:


pv_Modules_ia = pd.DataFrame(columns = ['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'])
pv_glass_ia = pd.DataFrame(columns = ['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'])
pv_copper_ia = pd.DataFrame(columns = ['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'])
pv_aluminium_frames_ia = pd.DataFrame(columns = ['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'])
pv_encapsulant_ia = pd.DataFrame(columns = ['name', 'latitude (deg)', 'longitude (deg)','amount 1','amount 2','amount 3','amount 4','amount 5','amount 6','amount 7','amount 8','amount 9','amount 10','amount 11','amount 12','amount 13','amount 14','amount 15','amount 16','amount 17','amount 18','amount 19','amount 20','amount 21','amount 22','amount 23','amount 24','amount 25','amount 26','amount 27','amount 28'])






# Fill the data of name, latitude and longitude.

# In[587]:


pv_Modules_ia['name'], pv_Modules_ia['latitude (deg)'],pv_Modules_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_glass_ia['name'], pv_glass_ia['latitude (deg)'],pv_glass_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_copper_ia['name'], pv_copper_ia['latitude (deg)'],pv_copper_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_aluminium_frames_ia['name'], pv_aluminium_frames_ia['latitude (deg)'],pv_aluminium_frames_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_encapsulant_ia['name'], pv_encapsulant_ia['latitude (deg)'],pv_encapsulant_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 


# Add amounts.

# In[563]:


pv_Modules_ia.iloc[:,3:31] = cdte_Module_ia.iloc[:,3:31] + csi_Module_ia.iloc[:,3:31] 
pv_glass_ia.iloc[:,3:31] = csi_glass_ia.iloc[:,3:31] + cdte_glass_cdte_ia.iloc[:,3:31] 
pv_copper_ia.iloc[:,3:31] = csi_copper_ia.iloc[:,3:31] + cdte_copper_cdte_ia.iloc[:,3:31] 
pv_aluminium_frames_ia.iloc[:,3:31] = csi_aluminium_frames_ia.iloc[:,3:31] + cdte_aluminium_frames_cdte_ia.iloc[:,3:31] 
pv_encapsulant_ia.iloc[:,3:31] = csi_encapsulant_ia.iloc[:,3:31] + cdte_encapsulant_cdte_ia.iloc[:,3:31] 





# ## 2.5. Export the 'Ininital amounts' files

# In[588]:


pv_Modules_ia.to_csv('RELOG_import_data/pv_Modules_ia.csv')
pv_glass_ia.to_csv('RELOG_import_data/pv_glass_ia.csv')
pv_copper_ia.to_csv('RELOG_import_data/pv_copper_ia.csv')
pv_aluminium_frames_ia.to_csv('RELOG_import_data/pv_aluminium_frames_ia.csv')
pv_encapsulant_ia.to_csv('RELOG_import_data/pv_encapsulant_ia.csv')

csi_Module_ia.to_csv('RELOG_import_data/csi_Module_ia.csv')
csi_glass_ia.to_csv('RELOG_import_data/csi_glass_ia.csv')
csi_silicon_ia.to_csv('RELOG_import_data/csi_silicon_ia.csv')
csi_silver_ia.to_csv('RELOG_import_data/csi_silver_ia.csv')
csi_copper_ia.to_csv('RELOG_import_data/csi_copper_ia.csv')
csi_aluminium_frames_ia.to_csv('RELOG_import_data/csi_aluminium_frames_ia.csv')
csi_encapsulant_ia.to_csv('RELOG_import_data/csi_encapsulant_ia.csv')
csi_backsheet_ia.to_csv('RELOG_import_data/csi_backsheet_ia.csv')

cdte_Module_ia.to_csv('RELOG_import_data/cdte_Module_ia.csv')
cdte_cadmium_ia.to_csv('RELOG_import_data/cdte_cadmium_ia.csv')
cdte_tellurium_ia.to_csv('RELOG_import_data/cdte_tellurium_ia.csv')
cdte_glass_cdte_ia.to_csv('RELOG_import_data/cdte_glass_cdte_ia.csv')
cdte_aluminium_frames_cdte_ia.to_csv('RELOG_import_data/cdte_aluminium_frames_cdte_ia.csv')
cdte_copper_cdte_ia.to_csv('RELOG_import_data/cdte_copper_cdte_ia.csv')
cdte_encapsulant_cdte_ia.to_csv('RELOG_import_data/cdte_encapsulant_cdte_ia.csv')


# Remember that silver, silicon and backsheet are exclusively from cSi modules, likewise cadmium and tellurium are exclusive from CdTe. Further studies might not mix glass due to different compositions.

# ---
# ## 3. Make the recycling candidate file

# NOTE: Currently, I generated these files with the collection centers, I have to change it with the recycling centers.

# ### 3.1. States into region bins.

# In[18]:


from itertools import chain


# In[383]:


us_regions = {'New England' : set(['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']),
            'Middle Atlantic': set(['Delaware', 'the District of Columbia', 'Maryland', 'New Jersey', 'New York', 'Pennsylvania', 'Virginia', 'West Virginia']),
            'South Atlantic': set(['Georgia', 'North Carolina', 'South Carolina']),
            'Midwest': set(['Illinois', 'Indiana', 'Iowa', 'Kansas', 'Michigan', 'Minnesota', 'Missouri', 'Nebraska', 'North Dakota', 'Ohio', 'South Dakota', 'Wisconsin']),
            'Gulf': set(['Texas', 'Louisiana', 'Mississippi', 'Alabama', 'Florida', 'Arkansas', 'Kentucky', 'Tennessee']),
            'Southwest': set(['Nevada', 'Oklahoma', 'Utah']),
            'Mountain': set(['Arizona', 'Colorado', 'Idaho', 'Montana', 'New Mexico', 'Wyoming']),
            'Pacific Coast': set(['California', 'Oregon', 'Washington', 'Alaska', 'Hawaii'])}


# ### 3.2. Generate cost indexes

# Relative labor rate and productivity indexes in the
# chemical and allied products industries for the United States (1989). Source: PLANT DESIGN AND ECONOMICS FOR CHEMICAL ENGINEERS, Peter M. S.

# In[384]:


cost_index = {'Geographical area': ['New England', 'Middle Atlantic', 'South Atlantic', 'Midwest', 'Gulf', 'Southwest', 'Mountain', 'Pacific Coast'], 'Relative labor rate': [1.14, 1.06, 0.84, 1.03, 0.95, 0.88, 0.88, 1.22], 'Relative productivity factor': [0.95, 0.96, 0.91, 1.06, 1.22, 1.04, 0.97, 0.89]}
index_df = pd.DataFrame(data=cost_index)                                 


# In[385]:


index_df


# Now I need to get the factor normalized with California (Pacific Coast), I get this calculation also from the book "Plant design and economics for..."
# 
# NOTE: I have to calculate the price for CdTe in California as well,  this might be a problem if we estimate the price based on FS's which are based in Ohio.

# In[386]:


pc_labor_rate = index_df.loc[index_df['Geographical area'] == 'Pacific Coast']['Relative labor rate'].values 
pc_prod_factor = index_df.loc[index_df['Geographical area'] == 'Pacific Coast']['Relative productivity factor'].values 


# In[387]:


pc_prod_factor


# In[388]:


index_df['Relative labor rate CA'], index_df['Relative productivity factor CA'] = index_df['Relative labor rate']/pc_labor_rate, index_df['Relative productivity factor']/pc_prod_factor


# Now let's calculate the "Construction cost" or area factor:

# In[389]:


index_df['Area factor'] = index_df['Relative labor rate CA']/ index_df['Relative productivity factor CA']


# In[390]:


index_df


# In[391]:


GIS_usa = GIS[GIS.country == 'United States']
GIS_usa.reset_index(inplace=True)
GIS_usa = GIS_usa.iloc[0:134]


# Setup the template for the collection center file.

# In[412]:


candidate_locations = pd.DataFrame(columns=['name', 'latitude (deg)', 'longitude (deg)', 'area cost factor'])                


# I am going to correlate states and regions as well and then delete it, this is to add the area cost factors.

# In[413]:


candidate_locations['name'], candidate_locations['state'], candidate_locations['latitude (deg)'], candidate_locations['longitude (deg)'] = GIS_usa['location'], GIS_usa['state'], GIS_usa['long'], GIS_usa['lat']


# Make a dictionary of Geographical area (or regions) and area factors.

# In[414]:


index_dict = dict(zip(index_df['Geographical area'], index_df['Area factor']))


# In[415]:


index_dict


# In[416]:


us_regions.keys()


# In[417]:


for key in us_regions:
    candidate_locations.loc[candidate_locations['state'].isin(us_regions[key]), 'Region'] = key


# In[418]:


candidate_locations["area cost factor"] = candidate_locations["Region"].apply(lambda x: index_dict.get(x))


# Now we drop the state and Region columns:

# In[419]:


candidate_locations_clean = candidate_locations.drop(['state', 'Region'], axis=1)


# In[420]:


candidate_locations_clean


# In[423]:


candidate_locations_clean['latitude (deg)'] = candidate_locations_clean['latitude (deg)'].round(decimals=4)
candidate_locations_clean['longitude (deg)'] = candidate_locations_clean['longitude (deg)'].round(decimals=4)
candidate_locations_clean['area cost factor'] = candidate_locations_clean['area cost factor'].round(decimals=2)


# In[426]:


candidate_locations_clean.to_csv('RELOG_import_data/collection_centers.csv')


# In[427]:


# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#     print(candidate_locations)


# In[ ]:





# ---
# ## 4. Shankey Diagram

# For the Shankey Diagram, I need:
# 1) Get the waste (cSi + CdTe).
#     * Get the cSi waste and CdTe waste.
#     * Get the amount of each material in cSi and CdTe.
# 2) Add all those materials into material bins.
# 3) Pass them by an intermediate bin with the recycling process an d  their recycling yield.
# 4) Add all those materials and check how much of each could contribute to revenue based on their value.
# 

# ### 4.1. Get the waste

# In[ ]:


csi_waste = csi_Module['total waste'].sum()
cdte_waste = cdte_Module['total waste'].sum()
all_waste = csi_waste + cdte_waste
print(f'There are {all_waste:.2f} tonnes of PV waste (that\'s {all_waste/1000000:.2f} million metric tonnes).')
print(f'There are {csi_waste:.2f} tonnes of cSi, and {cdte_waste:.2f} tonnes of CdTe.')
perc_csi = csi_waste/all_waste
perc_cdte = cdte_waste/all_waste
print(f'Of all the waste, {perc_csi*100:.2f}% is cSi, and {perc_cdte*100:.2f}% is CdTe.')


# ### 4.2. Material bins

# In[ ]:


csi_waste = {'Modules' : csi_Module['total waste'].sum(),
            'Glass' : csi_glass['total waste'].sum(),
            'Silicon' : csi_silicon['total waste'].sum(),
            'Silver': csi_silver['total waste'].sum(),
            'Copper' : csi_copper['total waste'].sum(),
            'Aluminium frames': csi_aluminium_frames['total waste'].sum(),
            'Encapsulant': csi_encapsulant['total waste'].sum(),
            'Backsheet': csi_backsheet['total waste'].sum(),}


# ### 4.3. Recycling bins

# In[ ]:


#FRELP efficiencies unless indicated

csi_recycled = {'Modules' : csi_Module['total waste'].sum(),
            'Glass' : csi_glass['total waste'].sum()*0.98, 
            'Silicon' : csi_silicon['total waste'].sum()*0.95,
            'Silver': csi_silver['total waste'].sum()*0.95,
            'Copper' : csi_copper['total waste'].sum()*0.95,
            'Aluminium frames': csi_aluminium_frames['total waste'].sum(), # Assume 100% from the frames
            'Encapsulant': csi_encapsulant['total waste'].sum(), # Here the encapsulant is incinerated so, 100% goes out
            'Backsheet': csi_backsheet['total waste'].sum(),# Same as encapsulant
            'Landfill': csi_glass['total waste'].sum()*(1-0.98) + 
                csi_silicon['total waste'].sum()*(1-0.95) + 
                csi_silver['total waste'].sum()*(1-0.95) + 
                csi_copper['total waste'].sum()*(1-0.95),
            'Energy': csi_encapsulant['total waste'].sum()+csi_backsheet['total waste'].sum()} 


# In[ ]:


cdte_waste = {'Modules' : cdte_Module['total waste'].sum(),
            'Glass' : cdte_glass_cdte['total waste'].sum(),
            'Cadmium': cdte_cadmium['total waste'].sum(),
            'Tellurium': cdte_tellurium['total waste'].sum(),
            'Copper' : cdte_copper_cdte['total waste'].sum(), # No data about the copper recovery, so I assume the same as FRELP
            'Aluminium frames': cdte_aluminium_frames_cdte['total waste'].sum(),
            'Encapsulant': cdte_encapsulant_cdte['total waste'].sum(),} # Here there is no info so I assume the same as the glass


# In[ ]:


cdte_recycled['Landfill']


# In[ ]:


# First Solar efficiencies unless indicated

cdte_recycled = {'Modules' : cdte_Module['total waste'].sum(),
            'Glass' : cdte_glass_cdte['total waste'].sum()*0.9,
            'Cadmium': cdte_cadmium['total waste'].sum()*0.95,
            'Tellurium': cdte_tellurium['total waste'].sum()*0.95,
            'Copper' : cdte_copper_cdte['total waste'].sum()*0.95, # No data about the copper recovery, so I assume the same as FRELP
            'Aluminium frames': cdte_aluminium_frames_cdte['total waste'].sum(),
            'Encapsulant': cdte_encapsulant_cdte['total waste'].sum()*0.9,# Here there is no info so I assume the same as the glass
            'Landfill':cdte_glass_cdte['total waste'].sum()*(1-0.9) +
                cdte_cadmium['total waste'].sum()*(1-0.95) +
                cdte_tellurium['total waste'].sum()*(1-0.95) +
                cdte_copper_cdte['total waste'].sum()*(1-0.95) +
                cdte_encapsulant_cdte['total waste'].sum()*(1-0.9),
            } 


# In[ ]:


material_list_csi = ['glass', 'silicon', 'silver', 'copper', 'aluminium_frames', 'encapsulant', 'backsheet', 'Module']
material_list_cdte = ['cadmium', 'telluride', 'glass_cdte', 'aluminium_frames_cdte', 'Module', 'copper_cdte', 'encapsulant_cdte']


# ### 4.4. Generate figures

# In[ ]:


import plotly.graph_objects as go


# In[ ]:


if not os.path.exists("images"):
    os.mkdir("images")


# In[ ]:


my_colors = {'pvwaste':'rgba(255, 243, 217, 1)',
             'csi_blue': 'rgba(199, 219, 244,1)',
             'cdte_tiel': 'rgba(215, 250, 245, 1)',
             'product_green': 'rgba(217, 240, 217, 1)',
             'energy_yellow': 'rgba(252, 252, 202, 1)',
             'waste_red': 'rgba(247, 145, 116,1)',
             'worth_green': 'rgba(192, 232, 131,1)'}


# In[ ]:


fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 10,
      thickness = 20,
      line = dict(color = 'black', width = 0.5),
      label = ['PV Waste', 'cSi', 'CdTe', 
               'Glass', 'Silicon', 'Silver', 'Copper', 'Aluminum frames', 'Encapsulant', 'Backsheet', 
               'Glass', 'Cadmium', 'Tellurium', 'Copper', 'Aluminum frames', 'Encapsulant', 
               'cSi Recycling', 'CdTe Recycling', 
               'Glass scrap', 'Manufacturing grade silicon', 'Copper scrap', 'Silver scrap', 'Cadmium scrap', 'Tellurium scrap', 'Aluminum scrap', 'Landfill', 'Energy'],
      color = [my_colors['pvwaste'], my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], 
               my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'], 
               my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['waste_red'], my_colors['worth_green']]
),
    link = dict(
      source = [0, 0, 
                1, 1, 1, 1, 1, 1, 1, 
                2, 2, 2, 2, 2, 2, 
                3, 4, 5, 6, 7, 8, 9,
                10, 11, 12, 13, 14, 15,
                16,16,16,16,16,16,16,
                17,17,17,17,17,17, ], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [1, 2, 
                3, 4, 5, 6, 7, 8, 9, 
                10, 11, 12, 13, 14, 15,
                16, 16, 16, 16, 16, 16, 16,
                17, 17, 17, 17, 17, 17,
                18, 19, 20, 21, 24, 25, 26,
                18, 20, 22, 23, 24, 25],
      value = [csi_waste['Modules'], cdte_waste['Modules'], 
               csi_waste['Glass'], csi_waste['Silicon'], csi_waste['Silver'], csi_waste['Copper'], csi_waste['Aluminium frames'], csi_waste['Encapsulant'], csi_waste['Backsheet'], 
               cdte_waste['Glass'], cdte_waste['Cadmium'], cdte_waste['Tellurium'], cdte_waste['Copper'], cdte_waste['Aluminium frames'], cdte_waste['Encapsulant'],
               csi_waste['Glass'], csi_waste['Silicon'], csi_waste['Silver'], csi_waste['Copper'], csi_waste['Aluminium frames'], csi_waste['Encapsulant'], csi_waste['Backsheet'], 
               cdte_waste['Glass'], cdte_waste['Cadmium'], cdte_waste['Tellurium'], cdte_waste['Copper'], cdte_waste['Aluminium frames'], cdte_waste['Encapsulant'],
               csi_recycled['Glass'], csi_recycled['Silicon'], csi_recycled['Copper'], csi_recycled['Silver'], csi_recycled['Aluminium frames'], csi_recycled['Landfill'],csi_recycled['Energy'],
               cdte_recycled['Glass'], cdte_recycled['Copper'], cdte_recycled['Cadmium'], cdte_recycled['Tellurium'], cdte_recycled['Aluminium frames'], cdte_recycled['Landfill']],
      color = 'rgba(240, 240, 245, 0.65)'
  ))])

fig.update_layout(font_family="Times New Roman", font_size=10)
fig.write_image("images/sankey_labeled.svg")


# In[ ]:


fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 10,
      thickness = 20,
      line = dict(color = 'black', width = 0.5),
      label = ['PV Waste', 'cSi Recycling', 'CdTe Recycling', 
               'Glass scrap', 'Manufacturing grade silicon', 'Copper scrap', 'Silver scrap', 'Cadmium scrap', 'Tellurium scrap', 'Aluminum scrap', 'Landfill', 'Energy'],
      color = [my_colors['pvwaste'], my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['waste_red'], my_colors['worth_green']]
),
    link = dict(
      source = [0, 0, 
                1,1,1,1,1,1,1,
                2,2,2,2,2,2, ], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [1, 2,
                3, 4, 5, 6, 9, 10, 11,
                3, 5, 7, 8, 9, 10],
      value = [csi_waste['Modules'], cdte_waste['Modules'], 
               csi_recycled['Glass'], csi_recycled['Silicon'], csi_recycled['Copper'], csi_recycled['Silver'], csi_recycled['Aluminium frames'], csi_recycled['Landfill'],csi_recycled['Energy'],
               cdte_recycled['Glass'], cdte_recycled['Copper'], cdte_recycled['Cadmium'], cdte_recycled['Tellurium'], cdte_recycled['Aluminium frames'], cdte_recycled['Landfill']],
      color = 'rgba(240, 240, 245, 0.65)'
  ))])

fig.update_layout(font_family="Times New Roman", font_size=10)
fig.write_image("images/sankey_labeled_simplified.svg")


# In[ ]:





# In[ ]:


fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 10,
      thickness = 20,
      line = dict(color = 'black', width = 0.5),
      label = ['', '', '', 
               '', '', '', '', '', '', '', 
               '', '', '', '', '', '', 
               '', '', 
               '', '', '', '', '', '', '', '', ''],
      color = [my_colors['pvwaste'], my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], my_colors['csi_blue'], 
               my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'],my_colors['cdte_tiel'], 
               my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['waste_red'], my_colors['worth_green']]
),
    link = dict(
      source = [0, 0, 
                1, 1, 1, 1, 1, 1, 1, 
                2, 2, 2, 2, 2, 2, 
                3, 4, 5, 6, 7, 8, 9,
                10, 11, 12, 13, 14, 15,
                16,16,16,16,16,16,16,
                17,17,17,17,17,17, ], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [1, 2, 
                3, 4, 5, 6, 7, 8, 9, 
                10, 11, 12, 13, 14, 15,
                16, 16, 16, 16, 16, 16, 16,
                17, 17, 17, 17, 17, 17,
                18, 19, 20, 21, 24, 25, 26,
                18, 20, 22, 23, 24, 25],
      value = [csi_waste['Modules'], cdte_waste['Modules'], 
               csi_waste['Glass'], csi_waste['Silicon'], csi_waste['Silver'], csi_waste['Copper'], csi_waste['Aluminium frames'], csi_waste['Encapsulant'], csi_waste['Backsheet'], 
               cdte_waste['Glass'], cdte_waste['Cadmium'], cdte_waste['Tellurium'], cdte_waste['Copper'], cdte_waste['Aluminium frames'], cdte_waste['Encapsulant'],
               csi_waste['Glass'], csi_waste['Silicon'], csi_waste['Silver'], csi_waste['Copper'], csi_waste['Aluminium frames'], csi_waste['Encapsulant'], csi_waste['Backsheet'], 
               cdte_waste['Glass'], cdte_waste['Cadmium'], cdte_waste['Tellurium'], cdte_waste['Copper'], cdte_waste['Aluminium frames'], cdte_waste['Encapsulant'],
               csi_recycled['Glass'], csi_recycled['Silicon'], csi_recycled['Copper'], csi_recycled['Silver'], csi_recycled['Aluminium frames'], csi_recycled['Landfill'],csi_recycled['Energy'],
               cdte_recycled['Glass'], cdte_recycled['Copper'], cdte_recycled['Cadmium'], cdte_recycled['Tellurium'], cdte_recycled['Aluminium frames'], cdte_recycled['Landfill']],
      color = 'rgba(240, 240, 245, 0.65)'
  ))])

fig.update_layout(font_family="Times New Roman", font_size=10)
fig.write_image("images/sankey_mute.svg")


# In[ ]:


fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 10,
      thickness = 20,
      line = dict(color = 'black', width = 0.5),
      label = ['', '', '', 
               '', '', '', '', '', '', '', '', ''],
      color = [my_colors['pvwaste'], my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['waste_red'], my_colors['worth_green']]
),
    link = dict(
      source = [0, 0, 
                1,1,1,1,1,1,1,
                2,2,2,2,2,2, ], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [1, 2,
                3, 4, 5, 6, 9, 10, 11,
                3, 5, 7, 8, 9, 10],
      value = [csi_waste['Modules'], cdte_waste['Modules'], 
               csi_recycled['Glass'], csi_recycled['Silicon'], csi_recycled['Copper'], csi_recycled['Silver'], csi_recycled['Aluminium frames'], csi_recycled['Landfill'],csi_recycled['Energy'],
               cdte_recycled['Glass'], cdte_recycled['Copper'], cdte_recycled['Cadmium'], cdte_recycled['Tellurium'], cdte_recycled['Aluminium frames'], cdte_recycled['Landfill']],
      color = 'rgba(240, 240, 245, 0.65)'
  ))])

fig.update_layout(font_family="Times New Roman", font_size=10)
fig.write_image("images/sankey_muted_simplified.svg")


# In[ ]:


GIS_us


# In[ ]:


pv_waste_map = csi_Module[['FIPS']].copy()
pv_waste_map['total waste'] = csi_Module['total waste'] + cdte_Module['total waste']
pv_waste_map.to_csv('pv_waste_map.csv')

csi_waste_map = csi_Module[['FIPS', 'total waste']]
csi_waste_map.to_csv('csi_waste_map.csv')

cdte_waste_map = cdte_Module[['FIPS', 'total waste']]
cdte_waste_map.to_csv('cdte_waste_map.csv')


# 

# ---
# ## 5. Cloropeth map option 1 (still under construction)

# In[ ]:


from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("pv_waste_map.csv",
                   dtype={"FIPS": str})

import plotly.express as px

fig = px.choropleth_mapbox(df, geojson=counties, locations='FIPS', color='total waste',
                           color_continuous_scale="Viridis",
                           range_color=(8, 1200000), # min an max values of waste
                           mapbox_style="carto-positron",
                           zoom=2.5, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'total waste':'Accumulated waste'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.write_image("images/map_allPV_op1.svg")


# Cloropeth map option 2

# In[ ]:


from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("pv_waste_map.csv",
                   dtype={"FIPS": str})

import plotly.express as px

fig = px.choropleth(df, geojson=counties, locations='FIPS', color='total waste',
                           color_continuous_scale="Viridis",
                           range_color=(1000, 50000),
                           scope="usa",
                           labels={'total waste':'Total PV waste by 2050'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.write_image("images/map_allPV_op2.svg")


# In[ ]:


pv_waste_map.min()


# In[ ]:


pv_waste_map.max()


# In[ ]:


from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})

import plotly.express as px

fig = px.choropleth(df, geojson=counties, locations='fips', color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           labels={'unemp':'unemployment rate'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.write_image("images/map_allPV_op2.svg")


# In[ ]:




