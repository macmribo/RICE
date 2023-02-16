#!/usr/bin/env python
# coding: utf-8

# # Data Preprocess 1

# This journal describes how to prepare the data to run the RELOG scenarios. He we will cover:
# 1. Waste files generation. Correlates latitude and longitude with a region and state. Takes PV ICE-generated data file and creates individual waste files based on the type of waste.
# 2. Make initial amounts file. Using the previously generated files, we show how to make an 'Initial amounts file' so it is in RELOG input data format. 
# 3. Make recycling candidates files. Generate the PV recycling plant candidates files using the correct area cost factor.
# 4. Continue to RELOG case-builder.
# 5. Make a sankey diagram from section 1.
# 6. Render a cloropeth map from section 2 (not finished!)
# 
# A continuation of this journal can be found in [Data Preprocess 2](./data_preprocess_2.ipynb).
# 
# ***NOTE:** All quantities are given in **metric tonnes**.*

# ## 0. Load necessary libraries

# In[2]:


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
# ## 1. Waste files generation

# ### 1.1. Get the GIS locations from the latitude and longitude

# Load the GIS file.

# In[3]:


GIS = pd.read_excel('Geo_data/gis_centroid_n.xlsx') # Read the GIS excel file.
GIS # Prints first five rows.


# The generated file has four columns, with longitude, latitude PCA id and country. This does not tell us much about their actual location so we can use the following gunction to create additional columns to the GIS file with the actual location names.

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
    #row['city'] = city
    row['county'] = county
    row['state'] = state
    row['country'] = country
    #row['location'] = county_state
    return row


# Generate a GIS file with the name of the locations, this will be useful for section 2, 3 and 4. Where the location names matter to assign area cost factors and to locate waste in a map. I would recommend running this function once, saving the output, and then, when needed, just read the generated csv.

# #### 1.1.1 Generaye GIS file — ONLY RUN ONCE! Skip to section 1.1.2. if you already generated the file

# In[4]:


get_ipython().run_cell_magic('time', '', '# This one takes around two minutes. Apply the previous function to obtain the names of the locations.\nGIS = GIS.apply(city_state_country, axis=1)\nGIS.head()')


# There is one county in California that shows empty. Let's add the corresponding county. Doing a quick maps  search, I saw that the [35.120104, -117.159039](https://www.google.com/maps/place/35%C2%B007'12.4%22N+117%C2%B009'32.5%22W/@35.6668582,-117.0465162,8.1z/data=!4m5!3m4!1s0x0:0xf02b1d027b57f1cb!8m2!3d35.120104!4d-117.159039) overlaps with [San Bernardino County](https://www.google.com/maps/place/San+Bernardino+County,+CA/@34.9743906,-117.1874339,10.12z/data=!4m5!3m4!1s0x80c52a8ae8311be5:0xa438bdbc918edca!8m2!3d34.9592083!4d-116.419389). The are in [33.031747, -116.717606](https://www.google.com/maps/place/33%C2%B001'54.3%22N+116%C2%B043'03.4%22W/@33.0171076,-116.9113049,9.82z/data=!4m5!3m4!1s0x0:0xb56a6fffc57eaadd!8m2!3d33.031747!4d-116.717606) corresponds to [San Diego County](https://www.google.com/maps/place/San+Diego+County,+CA/@33.016828,-117.4064529,9z/data=!3m1!4b1!4m5!3m4!1s0x80dbeb3023ff601d:0x350dfd2beb800728!8m2!3d33.0933809!4d-116.6081653). Let's add thesevalues to the empty county fields.

# In[5]:


GIS[(GIS.county == '') & (GIS.country == 'United States')] # Select the rows we need.


# Now let's use the `id` column to spot the right item and add the corresponding counties.

# In[6]:


GIS.loc[GIS.id == 'p10', 'county'] = 'San Bernardino'
GIS.loc[GIS.id == 'p11', 'county'] = 'San Diego'


# In[7]:


GIS.head()


# Let's now save the file, so we don't have to do this ever again. Hooray!

# In[8]:


GIS.to_csv('Geo_data/gis_region_names.csv')


# #### 1.1.2. Load GIS file — RUN THIS ONE IF YOU ALREADY GENERATED THIS FILE

# Run this cell if you already generated the `gis_region_names.csv` file.

# We no filter the GIS data so there's only USA.

# In[9]:


GIS = pd.read_csv('Geo_data/gis_region_names.csv')
GIS_us = GIS[GIS.country == 'United States']
GIS_us.reset_index(inplace=True)
GIS_us = GIS_us.iloc[0:134]
GIS_us.to_csv('Geo_data/GIS_us_collection_centers_only.csv')


# Now that we have the data we need, I am going to separate the `long` and `lat`, and the `id` into their own dataframes for easier handling.

# In[10]:


GIS_us_long_lat = GIS_us[['long', 'lat']]
GIS_us_id = GIS_us[['id']]


# ### 1.2. Correlate GIS longitude and latitude with FIPS codes for the map diagram and EJ API queries

# This is more GIS data pre processing, it is not needed to get the waste files but will be helpful to obtain a cloropeth map with the waste, and the dataframe that with the Energy Justice metrics.

# #### 1.2.1. Obtain GIS data with FIPS codes

# In[11]:


fips_county_codes = []
fips_state_codes = []


# **NOTE:** Run only once and skip to section 1.2.2, to just load this data.

# In[12]:


get_ipython().run_cell_magic('time', '', "# Code from https://gis.stackexchange.com/questions/294641/python-code-for-transforming-lat-long-into-fips-codes\nimport requests\nimport urllib\n\n#Encode parameters \nfor lon, lat in GIS_us_long_lat.itertuples(index=False):\n    params = urllib.parse.urlencode({'latitude': lat, 'longitude':lon, 'format':'json'})\n    #Contruct request URL\n    url = 'https://geo.fcc.gov/api/census/block/find?' + params\n\n    #Get response from API\n    response = requests.get(url)\n\n    #Parse json in response\n    data = response.json()\n    fips_county_codes.append(data['County']['FIPS'])\n    fips_state_codes.append(data['State']['FIPS'])\n    #Print FIPS code")


# In[14]:


GIS_us_long_lat.loc[:, 'fips_county'] = fips_county_codes
GIS_us_long_lat.loc[:, 'fips_state'] = fips_state_codes


# In[16]:


GIS_us_long_lat.head()


# In[17]:


GIS_us_long_lat.to_csv('Geo_data/GIS_us_long_lat.csv') # Save file


# #### 1.2.2. Load GIS with FIPS data

# In[19]:


GIS_us_long_lat = pd.read_csv('Geo_data/GIS_us_long_lat.csv') # Load file


# ### 1.3. Separate the PV ICE output and create individual material file

# Here I create a path to the folder where we saved the waste files generated by PV ICE. There are two folders in `PV_ICE_raw_outputs`, `Ordered` and `Unordered`. The unordered file contains the PV ICE output with the unordered generated data. For the purpose of this journal we will be looking at the `Ordered` folder. 
# 
# If you generated your own PV ICE scenarios, I recommend creating its own folder inside `PV_ICE_raw_outputs` and change the `pv_ice_simulation` variable with the name of the file you are going to use for your own simulation. If the folder does not exists, it will create one!

# In[44]:


pv_ice_simulation = 'Ordered'


# In[45]:


cwd = os.getcwd() # Get the current path
pvice_input_folder = os.path.join(cwd, 'PV_ICE_raw_outputs', pv_ice_simulation)


# Check if the path exists, if not, it will create the path with necessary folders.

# In[46]:


#python program to check if a directory exists
import os

# Check whether the specified path exists or not
isExist = os.path.exists(pvice_input_folder)
if isExist:
    print("The path already exists!")
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(pvice_input_folder)
    print("The new directory is created!")


# This is to make the output file.

# In[54]:


cwd = os.getcwd()
pvice_output_folder = os.path.join(cwd, 'PV_ICE_separate_outputs', pv_ice_simulation)


# In[55]:


#python program to check if a directory exists
import os

# Check whether the specified path exists or not
isExist = os.path.exists(pvice_output_folder)
if isExist:
    print("The path already exists!")
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(pvice_output_folder)
   print("The new directory is created!")


# Read the cSi and CdTe waste files, respectively.

# In[57]:


csi_eol = pd.read_csv(os.path.join(pvice_input_folder, 'PVICE_RELOG_PCA_cSi_WasteEOL.csv'), index_col='year')
cdte_eol = pd.read_csv(os.path.join(pvice_input_folder, 'PVICE_RELOG_PCA_CdTe_WasteEOL.csv'), index_col='year')


# In[58]:


print('We have %s collection centers.' % len(GIS_us))


# Now I need to select the columns and separate them by material, then add a column identifying the locations. Ideally, I need to populate a table for each material.

# In[59]:


material_list_csi = ['glass', 'silicon', 'silver', 'copper', 'aluminium_frames', 'encapsulant', 'backsheet', 'Module']
material_list_cdte = ['cadmium', 'tellurium', 'glass_cdte', 'aluminium_frames_cdte', 'Module', 'copper_cdte', 'encapsulant_cdte']


# In[30]:


nums = np.arange(1,42)
years = np.arange(2010,2051)
years_dict = {nums[i]: years[i] for i in range(len(nums))}


# In[31]:


mats = ['csi', 'cdte']


# Generate waste files separated by technology and material.

# In[60]:


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
            globals()['%s_%s' % (y, x)].to_csv(os.path.join(pvice_output_folder, '{}_wasteEOL_{}.csv'.format(y, x)), index=False)
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
            globals()['%s_%s' % (y, x)].to_csv(os.path.join(pvice_output_folder, '{}_wasteEOL_{}.csv'.format(y, x)), index=False)
            
            


# ## 2. Initial amounts file generation

# Here I will be generating the file that has the waste initial amounts according to RELOG's template (Initial amounts - Template.csv).
# ![image.png](images/Initial_amounts_temp.png)
# 
# I have two options:
# 1) Add at the wastes and then do the processing to create ONE template of initial amounts.
# 2) Create THREE templates, two with CdTe and cSi separated, and then create another one summing the previous two.
# 
# I am going to do option 2, that way if we decide to generate a separate RELOG scenario with one or the other technology, we have already separate files. I am also  going to create the files for individual materials in case they update the software so we also have material timeseries.

# ### 2.1. Load the waste files that we just generated.

# **LOAD OPTION 1:** If you have run Section 1 cells, fetch the data as csi_Module and cdte_Module. I make a copy of these files since I will be changing them considerably.

# In[121]:


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


# **LOAD OPTION 2:** If you haven't run Section 1 cells, use function load_csv with the corresponding file name.

# In[122]:


# Uncomment if you need this option
# csi_Module_ia = pd.read_csv('csi_wasteEOL_Module.csv')
# csi_glass_ia = pd.read_csv('csi_wasteEOL_glass.csv')
# csi_silicon_ia = pd.read_csv('csi_wasteEOL_silicon.csv')
# csi_silver_ia = pd.read_csv('csi_wasteEOL_silver.csv')
# csi_copper_ia = pd.read_csv('csi_wasteEOL_copper.csv')
# csi_aluminium_frames_ia = pd.read_csv('csi_wasteEOL_aluminium_frames.csv')
# csi_encapsulant_ia = pd.read_csv('csi_wasteEOL_encapsulant.csv')
# csi_backsheet_ia = pd.read_csv('csi_wasteEOL_backsheet.csv')

# cdte_Module_ia = pd.read_csv('cdte_wasteEOL_Module.csv')
# cdte_cadmium_ia = pd.read_csv('cdte_wasteEOL_cadmium.csv')
# cdte_tellurium_ia = pd.read_csv('cdte_wasteEOL_tellurium.csv')
# cdte_glass_cdte_ia = pd.read_csv('cdte_wasteEOL_glass_cdte.csv')
# cdte_aluminium_frames_cdte_ia = pd.read_csv('cdte_wasteEOL_aluminium_frames_cdte.csv')
# cdte_copper_cdte_ia = pd.read_csv('cdte_wasteEOL_copper_cdte.csv')
# cdte_encapsulant_cdte_ia = pd.read_csv('cdte_wasteEOL_encapsulant_cdte.csv')


# ### 2.2. Drop unnecessary columns

# Drop columns: 0, 2010 (there is no waste here), FIPS, 45, longitude, latitude and total waste columns. Then I insert the 'name' row and then move longitude and latitude rows

# In[123]:


csi_Module_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_glass_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_silicon_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_silver_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_copper_ia.drop([0, 2010, 'FIPS', 45,46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_aluminium_frames_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_encapsulant_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
csi_backsheet_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.


# In[124]:


cdte_Module_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_cadmium_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_tellurium_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_glass_cdte_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.)
cdte_aluminium_frames_cdte_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_copper_cdte_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.
cdte_encapsulant_cdte_ia.drop([0, 2010, 'FIPS', 45, 46, 'total waste', 'latitude', 'longitude'], axis=1, inplace= True) # Run this one only once or it will throw an error.


# ### 2.3. Add the name locations, latitude and longitude with the right names to the right position.

# I take the location file from GIS.

# In[125]:


GIS_usa = GIS[GIS.country == 'United States']
GIS_usa.reset_index(inplace=True)
GIS_usa = GIS_usa.iloc[0:134] # I slice it until 142 because the next locations are not in ReEDS.


# In[126]:


csi_Module_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_Module_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_Module_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_glass_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_glass_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_glass_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_silicon_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_silicon_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_silicon_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_silver_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_silver_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_silver_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_copper_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_copper_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_copper_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_aluminium_frames_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_aluminium_frames_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_aluminium_frames_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_encapsulant_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_encapsulant_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_encapsulant_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

csi_backsheet_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
csi_backsheet_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
csi_backsheet_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 


# In[127]:


cdte_Module_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_Module_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_Module_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_cadmium_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_cadmium_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_cadmium_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_tellurium_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_tellurium_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_tellurium_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_glass_cdte_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_glass_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_glass_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_aluminium_frames_cdte_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_aluminium_frames_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_aluminium_frames_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_copper_cdte_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_copper_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_copper_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 

cdte_encapsulant_cdte_ia.insert(0, 'name', GIS_usa[['county']]) # Run this one only once or it will throw an error.
cdte_encapsulant_cdte_ia.insert(1, 'latitude (deg)', GIS_usa[['lat']]) 
cdte_encapsulant_cdte_ia.insert(2, 'longitude (deg)', GIS_usa[['long']]) 


# #### 2.3.1 Add accumulated waste until year 2023

# Since I am studying from 2023 onward with RELOG, I add the waste generated from 2011 until 2023. I am considering doing this from 2025 since a lot pf places don't start having enough amount of waste until then.

# In[128]:


csi_Module_ia_sumyears = csi_Module_ia.loc[:, 2011:2023].sum(axis=1)
csi_glass_ia_sumyears = csi_glass_ia.loc[:, 2011:2023].sum(axis=1)
csi_silicon_ia_sumyears = csi_silicon_ia.loc[:, 2011:2023].sum(axis=1)
csi_silver_ia_sumyears = csi_silver_ia.loc[:, 2011:2023].sum(axis=1)
csi_copper_ia_sumyears = csi_copper_ia.loc[:, 2011:2023].sum(axis=1)
csi_aluminium_frames_ia_sumyears = csi_aluminium_frames_ia.loc[:, 2011:2023].sum(axis=1)
csi_encapsulant_ia_sumyears = csi_encapsulant_ia.loc[:, 2011:2023].sum(axis=1)
csi_backsheet_ia_sumyears = csi_backsheet_ia.loc[:, 2011:2023].sum(axis=1)


cdte_Module_ia_sumyears = cdte_Module_ia.loc[:, 2011:2023].sum(axis=1)
cdte_cadmium_ia_sumyears = cdte_cadmium_ia.loc[:, 2011:2023].sum(axis=1)
cdte_tellurium_ia_sumyears = cdte_tellurium_ia.loc[:, 2011:2023].sum(axis=1)
cdte_glass_cdte_ia_sumyears = cdte_glass_cdte_ia.loc[:, 2011:2023].sum(axis=1)
cdte_aluminium_frames_cdte_ia_sumyears = cdte_aluminium_frames_cdte_ia.loc[:, 2011:2023].sum(axis=1)
cdte_copper_cdte_ia_sumyears = cdte_copper_cdte_ia.loc[:, 2011:2023].sum(axis=1)
cdte_encapsulant_cdte_ia_sumyears = cdte_encapsulant_cdte_ia.loc[:, 2011:2023].sum(axis=1)


# Drop columns 2011 to 2023.

# In[129]:


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

# In[130]:


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


# #### 2.3.2. Change years for amounts

# Change the column names as 'amount 1', 'amount 2', etc. I am not sure if it matters, but I am going to do it just in case!
# From 2023 to 2050, we have a total of 28 amounts.

# In[134]:


num_years = 28 # simulation years, change for the amount of years we are simulating


# In[135]:


column_names = ['name', 'latitude (deg)', 'longitude (deg)']


# In[136]:


for year in range(num_years):
    amounts = f'amount {year+1}'
    column_names.append(amounts)


# In[137]:


csi_Module_ia.set_axis(column_names, axis=1, inplace=True)
csi_glass_ia.set_axis(column_names, axis=1, inplace=True)
csi_silicon_ia.set_axis(column_names, axis=1, inplace=True)
csi_silver_ia.set_axis(column_names, axis=1, inplace=True)
csi_copper_ia.set_axis(column_names, axis=1, inplace=True)
csi_aluminium_frames_ia.set_axis(column_names, axis=1, inplace=True)
csi_encapsulant_ia.set_axis(column_names, axis=1, inplace=True)
csi_backsheet_ia.set_axis(column_names, axis=1, inplace=True)

cdte_Module_ia.set_axis(column_names, axis=1, inplace=True)
cdte_cadmium_ia.set_axis(column_names, axis=1, inplace=True)
cdte_tellurium_ia.set_axis(column_names, axis=1, inplace=True)
cdte_glass_cdte_ia.set_axis(column_names, axis=1, inplace=True)
cdte_aluminium_frames_cdte_ia.set_axis(column_names, axis=1, inplace=True)
cdte_copper_cdte_ia.set_axis(column_names, axis=1, inplace=True)
cdte_encapsulant_cdte_ia.set_axis(column_names, axis=1, inplace=True)


# ### 2.4. Create new PV datasets that add cSi and CdTe 

# Here I add cSi and CdTe modules as one, and common materials as one.

# In[138]:


pv_Modules_ia = pd.DataFrame(columns = column_names)
pv_glass_ia = pd.DataFrame(columns = column_names)
pv_copper_ia = pd.DataFrame(columns = column_names)
pv_aluminium_frames_ia = pd.DataFrame(columns = column_names)
pv_encapsulant_ia = pd.DataFrame(columns = column_names)


# Fill the data of name, latitude and longitude.

# In[139]:


pv_Modules_ia['name'], pv_Modules_ia['latitude (deg)'],pv_Modules_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_glass_ia['name'], pv_glass_ia['latitude (deg)'],pv_glass_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_copper_ia['name'], pv_copper_ia['latitude (deg)'],pv_copper_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_aluminium_frames_ia['name'], pv_aluminium_frames_ia['latitude (deg)'],pv_aluminium_frames_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 
pv_encapsulant_ia['name'], pv_encapsulant_ia['latitude (deg)'],pv_encapsulant_ia['longitude (deg)'] = csi_Module_ia[['name']], csi_Module_ia[['latitude (deg)']],csi_Module_ia[['longitude (deg)']] 


# Add amounts.

# In[142]:


pv_Modules_ia.iloc[:,3::] = cdte_Module_ia.iloc[:,3::] + csi_Module_ia.iloc[:,3::] 
pv_glass_ia.iloc[:,3::] = csi_glass_ia.iloc[:,3::] + cdte_glass_cdte_ia.iloc[:,3::] 
pv_copper_ia.iloc[:,33::] = csi_copper_ia.iloc[:,3::] + cdte_copper_cdte_ia.iloc[:,3::] 
pv_aluminium_frames_ia.iloc[:,3::] = csi_aluminium_frames_ia.iloc[:,3::] + cdte_aluminium_frames_cdte_ia.iloc[:,3::] 
pv_encapsulant_ia.iloc[:,3::] = csi_encapsulant_ia.iloc[:,33::] + cdte_encapsulant_cdte_ia.iloc[:,3::] 




# ### 2.5. Export the 'Ininital amounts' files

# In[148]:


simulation = 'Ordered'


# In[150]:


cwd = os.getcwd()
RELOG_PV_ICE_import_data = os.path.join(cwd, 'RELOG_import_data', simulation)


# In[151]:





# In[152]:


#python program to check if a directory exists
import os

# Check whether the specified path exists or not
isExist = os.path.exists(RELOG_PV_ICE_import_data)
if isExist:
    print("The path already exists!")
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(RELOG_PV_ICE_import_data)
    print("The new directory is created!")


# In[237]:


pv_Modules_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data, 'pv_Modules_ia.csv'), index=False)
pv_glass_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'pv_glass_ia.csv'), index=False)
pv_copper_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'pv_copper_ia.csv'), index=False)
pv_aluminium_frames_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'pv_aluminium_frames_ia.csv'), index=False)
pv_encapsulant_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'pv_encapsulant_ia.csv'), index=False)

csi_Module_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_Module_ia.csv'), index=False)
csi_glass_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_glass_ia.csv'), index=False)
csi_silicon_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_silicon_ia.csv'), index=False)
csi_silver_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_silver_ia.csv'), index=False)
csi_copper_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_copper_ia.csv'), index=False)
csi_aluminium_frames_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_aluminium_frames_ia.csv'), index=False)
csi_encapsulant_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_encapsulant_ia.csv'), index=False)
csi_backsheet_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'csi_backsheet_ia.csv'), index=False)

cdte_Module_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_Module_ia.csv'), index=False)
cdte_cadmium_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_cadmium_ia.csv'), index=False)
cdte_tellurium_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_tellurium_ia.csv'), index=False)
cdte_glass_cdte_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_glass_cdte_ia.csv'), index=False)
cdte_aluminium_frames_cdte_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_aluminium_frames_cdte_ia.csv'), index=False)
cdte_copper_cdte_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_copper_cdte_ia.csv'), index=False)
cdte_encapsulant_cdte_ia.to_csv(os.path.join(RELOG_PV_ICE_import_data,'cdte_encapsulant_cdte_ia.csv'), index=False)


# Remember that silver, silicon and backsheet are exclusively from cSi modules, likewise cadmium and tellurium are exclusive from CdTe. Further studies might not mix glass due to different compositions.

# #### The file I used for the baseline RELOG scenario is `pv_Modules_ia.csv`.

# ---
# ## 3. Recycling candidate file generation

# Here we need to format the candidate location file as RELOG format. We are going to use Iloeje's file. This file was downloaded from [Iloeje's RELOG protocol](https://gcc02.safelinks.protection.outlook.com/?url=https%3A%2F%2Fzenodo.org%2Frecord%2F7093835&data=05%7C01%7CMacarena.MendezRibo%40nrel.gov%7Cff06eb8094844577193c08daf5ad67c6%7Ca0f29d7e28cd4f5484427885aee7c080%7C0%7C0%7C638092422384595963%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&sdata=WSieyEH9ngwW08cjlpBDggXqMZKiTjn9rrnFYbGGPac%3D&reserved=0) named 'CandidateLocations.csv', the file is not the same for 'conservative' and 'optimistic'. 
# Although this file is technically already with the right format, the area cost factor is set for Georgia with 96 locations (conservative) and New Mexico with 109 locations(optimistic), so we have to choose one of these files, and set it for California, because it is where we made the Recycling Plant's calculations. I choose the New Mexico file because it has more candidate locations to choose from.

# ### 3.1. Generate cost indexes

# In[154]:


from itertools import chain


# Here I selected US regions based on relative labor rate and productivity indexes in the chemical and allied products industries for the United States (1989). Source: PLANT DESIGN AND ECONOMICS FOR CHEMICAL ENGINEERS, Peter M. S.
# 

# In[155]:


us_regions = {'New England' : set(['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']),
            'Middle Atlantic': set(['Delaware', 'the District of Columbia', 'Maryland', 'New Jersey', 'New York', 'Pennsylvania', 'Virginia', 'West Virginia']),
            'South Atlantic': set(['Georgia', 'North Carolina', 'South Carolina']),
            'Midwest': set(['Illinois', 'Indiana', 'Iowa', 'Kansas', 'Michigan', 'Minnesota', 'Missouri', 'Nebraska', 'North Dakota', 'Ohio', 'South Dakota', 'Wisconsin']),
            'Gulf': set(['Texas', 'Louisiana', 'Mississippi', 'Alabama', 'Florida', 'Arkansas', 'Kentucky', 'Tennessee']),
            'Southwest': set(['Nevada', 'Oklahoma', 'Utah']),
            'Mountain': set(['Arizona', 'Colorado', 'Idaho', 'Montana', 'New Mexico', 'Wyoming']),
            'Pacific Coast': set(['California', 'Oregon', 'Washington', 'Alaska', 'Hawaii'])}


# Map the cost indices with relative labor rates and productivity factors.

# In[203]:


cost_index = {'Geographical area': ['New England', 'Middle Atlantic', 'South Atlantic', 'Midwest', 'Gulf', 'Southwest', 'Mountain', 'Pacific Coast'], 'Relative labor rate': [1.14, 1.06, 0.84, 1.03, 0.95, 0.88, 0.88, 1.22], 'Relative productivity factor': [0.95, 0.96, 0.91, 1.06, 1.22, 1.04, 0.97, 0.89]}
index_df = pd.DataFrame(data=cost_index)                                 


# In[204]:


index_df


# Now I need to get the factor normalize these factors for California (Pacific Coast), I get this calculation also from the book "Plant design and economics for..."
# 
# **NOTE:** I have to calculate the price for CdTe in California as well,  this might be a problem if we estimate the price based on FS's which are based in Ohio.

# In[205]:


pc_labor_rate = index_df.loc[index_df['Geographical area'] == 'Pacific Coast']['Relative labor rate'].values 
pc_prod_factor = index_df.loc[index_df['Geographical area'] == 'Pacific Coast']['Relative productivity factor'].values 


# In[206]:


index_df['Relative labor rate CA'], index_df['Relative productivity factor CA'] = index_df['Relative labor rate']/pc_labor_rate, index_df['Relative productivity factor']/pc_prod_factor


# Now let's calculate the "Construction cost" or area factor:

# In[207]:


index_df['Area factor'] = index_df['Relative labor rate CA']/ index_df['Relative productivity factor CA']


# In[209]:


index_df


# ### 3.3. Load the candidate location file and adjust area factors

# Load the Recycling plant's candidate locations. The candidate locations are based on the Recycling plants from [Iloeje et al.](https://www.sciencedirect.com/science/article/pii/S2589004222011026), the file can be downloaded [here](https://zenodo.org/record/7093835#.Y-PlXsHMKek).
# 
# **NOTE:** This version uses the states in 'name' to define the area cost factor. Unfortunately, sometimes we do not have this information, and we will need tatitude and longitude to define the state and then map the area cost factor. For this version, refer to section 3.3.2.

# #### 3.3.1. Version 1: When we have the state in the column 'name'

# In[218]:


cadidate_loc = pd.read_csv(os.path.join('RELOG_import_data', 'CandidateLocations_op_NM.csv'))


# In[219]:


cadidate_loc.head()


# Let's create a new column with states so we can map the area cost factor with the right area.

# In[220]:


cadidate_loc['State'] = cadidate_loc['name'].str.rsplit(', ').str[-1] 


# In[221]:


cadidate_loc.head()


# ##### Adjust area factors

# Since the loaded candidate locations are related to a plant build in New Mexico (that's why its area factor is 1), we need to adjust the area cost factors to the plant we modeled, which is based in California.

# Make a dictionary of Geographical area (or regions) and area factors.

# In[222]:


index_dict = dict(zip(index_df['Geographical area'], index_df['Area factor']))


# In[223]:


index_dict


# In[224]:


us_regions.keys()


# In[225]:


for key in us_regions:
    cadidate_loc.loc[cadidate_loc['State'].isin(us_regions[key]), 'Region'] = key


# In[226]:


cadidate_loc.head()


# In[227]:


cadidate_loc["area cost factor"] = cadidate_loc["Region"].apply(lambda x: index_dict.get(x))


# Now we drop the state and Region columns:

# In[228]:


candidate_loc_clean = cadidate_loc.drop(['State', 'Region'], axis=1)


# In[229]:


candidate_loc_clean.head()


# Now let's round the numbers to reasonable amounts.

# In[230]:


candidate_loc_clean['latitude (deg)'] = candidate_loc_clean['latitude (deg)'].round(decimals=4)
candidate_loc_clean['longitude (deg)'] = candidate_loc_clean['longitude (deg)'].round(decimals=4)
candidate_loc_clean['area cost factor'] = candidate_loc_clean['area cost factor'].round(decimals=2)


# In[231]:


candidate_loc_clean.head()


# In[232]:


candidate_loc_clean.to_csv(os.path.join('RELOG_import_data', 'CandidateLocations_CA.csv'), index=False)


# #### 3.3.2. Version 2: When we don't have the state defined in the name

# Sometimes, our data might be given in `longitude` and `latitude` only, that means we have to use these to fins the corresponding state, and then use the mapping method we used in section 3.3.1. Luckily, in section 1 we defined a function that does exactly that! Here is the function in case you did not run those cells (I have also modified it to be in line with the file):

# In[191]:


def city_state_country_2(row):
    # I map latitude and longitude with actual names of those places.
    coord = f"{row['latitude (deg)']}, {row['longitude (deg)']}"
    location = geolocator.reverse(coord, exactly_one=True)
    address = location.raw['address']
    city = address.get('city', '')
    county = address.get('county', '')
    state = address.get('state', '')
    country = address.get('country', '')
    county_state = address.get('county', 'state')
    #row['city'] = city
    #row['county'] = county
    row['state'] = state
    #row['country'] = country
    #row['location'] = county_state
    return row


# Let's load the file that does not have the state in the `name` columns, which is, in fact the latest version from Iloeje's paper. This file can be accessed through the shared ANL Box file.

# In[192]:


cadidate_loc_2 = pd.read_csv(os.path.join('RELOG_import_data', 'Candidate locations - Battery Project.csv'))


# Let's apply that function:

# In[194]:


cadidate_loc_2 = cadidate_loc_2.apply(city_state_country_2, axis=1)


# The next step is to generate the area cost index relative to New York. Unfortunately, it seems that this file has area codes at a county level, which makes it a bit more complicated. I will have to ask ANL what to do here.

# TO BE CONTINUED

# ---
# #### 3.3.3. If no file is given, these cells shows how to set up the dataframe in RELOG format

# Setup the template for the collection center file.

# In[ ]:


candidate_locations = pd.DataFrame(columns=['name', 'latitude (deg)', 'longitude (deg)', 'area cost factor'])                


# I am going to correlate states and regions as well and then delete it, this is to add the area cost factors.

# In[ ]:


candidate_locations['name'], candidate_locations['state'], candidate_locations['latitude (deg)'], candidate_locations['longitude (deg)'] = GIS_usa['location'], GIS_usa['state'], GIS_usa['long'], GIS_usa['lat']


# ## 4. Go to RELOG case-builder

# Now you know how to generate the two files needed as inputs for RELOG. Go to RELOG web-based [case builder](https://relog.axavier.org/casebuilder) to setup the .json simulation file. For this baseline scenario I have used the files [pv_Modules_ia.csv](PV_Recycling_Plant/data/RELOG_import_data/Ordered/pv_Modules_ia.csv) as **collection center inputs** and [CandidateLocations_CA](PV_Recycling_Plant/data/RELOG_import_data/CandidateLocations_CA.csv) and **candidate locations**.
# 
# Remember that to be able to run a proper simulation you need to make sure that:
# * The PV_ICE output files have the same studied years than the one set in the case-builder. In this example we have 28 years.
# * You know the recycling plant's efficiencies (i.e. how much material is recovered per tonne processed).
# * You have the capacity and cost data of your plant.
# 
# 

# ---
# ## 5. Sankey Diagram

# For the Sankey Diagram, I need:
# 1) Get the waste (cSi + CdTe).
#     * Get the cSi waste and CdTe waste.
#     * Get the amount of each material in cSi and CdTe.
# 2) Add all those materials into material bins.
# 3) Pass them by an intermediate bin with the recycling process an d  their recycling yield.
# 4) Add all those materials and check how much of each could contribute to revenue based on their value.
# 
# **Note:** To visualize the Sankey diagram in Jupyter, you may need to add the plotly extension, you can install it by running this line in the terminal: `jupyter labextension install plotlywidget`. [Source]().

# ### 5.0. Load the waste files if you haven't run the previous cells

# In[ ]:


# Uncomment if you need this option

csi_Module = pd.read_csv('csi_wasteEOL_Module.csv')
csi_aluminium_frames = pd.read_csv('csi_wasteEOL_aluminium_frames.csv')
csi_backsheet = pd.read_csv('csi_wasteEOL_backsheet.csv')
csi_copper = pd.read_csv('csi_wasteEOL_copper.csv')
csi_encapsulant = pd.read_csv('csi_wasteEOL_encapsulant.csv')
csi_glass = pd.read_csv('csi_wasteEOL_glass.csv')
csi_silicon = pd.read_csv('csi_wasteEOL_silicon.csv')
csi_silver = pd.read_csv('csi_wasteEOL_silver.csv')



cdte_Module = pd.read_csv('cdte_wasteEOL_Module.csv')
cdte_aluminium_frames_cdte = pd.read_csv('cdte_wasteEOL_aluminium_frames_cdte.csv')
cdte_cadmium = pd.read_csv('cdte_wasteEOL_cadmium.csv')
cdte_copper_cdte = pd.read_csv('cdte_wasteEOL_copper_cdte.csv')
cdte_encapsulant_cdte = pd.read_csv('cdte_wasteEOL_encapsulant_cdte.csv')
cdte_glass_cdte = pd.read_csv('cdte_wasteEOL_glass_cdte.csv')
cdte_tellurium = pd.read_csv('cdte_wasteEOL_tellurium.csv')


# ### 5.1. Get all waste

# In[ ]:


csi_waste = csi_Module['total waste'].sum()
cdte_waste = cdte_Module['total waste'].sum()
all_waste = csi_waste + cdte_waste
print(f'There are {all_waste:.2f} tonnes of PV waste (that\'s {all_waste/1000000:.2f} million metric tonnes).')
print(f'There are {csi_waste:.2f} tonnes of cSi, and {cdte_waste:.2f} tonnes of CdTe.')
perc_csi = csi_waste/all_waste
perc_cdte = cdte_waste/all_waste
print(f'Of all the waste, {perc_csi*100:.2f}% is cSi, and {perc_cdte*100:.2f}% is CdTe.')


# In[ ]:


# Option for one year, just change the year to the one you need

csi_waste_2050 = csi_Module['2050'].sum()
cdte_waste_2050 = cdte_Module['2050'].sum()
all_waste_2050 = csi_waste_2050 + cdte_waste_2050
print(f'There are {all_waste_2050:.2f} tonnes of PV waste (that\'s {all_waste_2050/1000000:.2f} million metric tonnes).')
print(f'There are {csi_waste_2050:.2f} tonnes of cSi, and {cdte_waste_2050:.2f} tonnes of CdTe.')
perc_csi_2050 = csi_waste_2050/all_waste_2050
perc_cdte_2050 = cdte_waste_2050/all_waste_2050
print(f'Of all the waste, {perc_csi_2050*100:.2f}% is cSi, and {perc_cdte_2050*100:.2f}% is CdTe.')


# ### 5.2. Waste material bins

# #### 5.2.1. cSi

# In[ ]:


csi_waste = {'Modules' : csi_Module['total waste'].sum(),
            'Glass' : csi_glass['total waste'].sum(),
            'Silicon' : csi_silicon['total waste'].sum(),
            'Silver': csi_silver['total waste'].sum(),
            'Copper' : csi_copper['total waste'].sum(),
            'Aluminium frames': csi_aluminium_frames['total waste'].sum(),
            'Encapsulant': csi_encapsulant['total waste'].sum(),
            'Backsheet': csi_backsheet['total waste'].sum(),}


# In[ ]:



csi_waste_2050 = {'Modules' : csi_Module['2050'].sum(),
            'Glass' : csi_glass['2050'].sum(),
            'Silicon' : csi_silicon['2050'].sum(),
            'Silver': csi_silver['2050'].sum(),
            'Copper' : csi_copper['2050'].sum(),
            'Aluminium frames': csi_aluminium_frames['2050'].sum(),
            'Encapsulant': csi_encapsulant['2050'].sum(),
            'Backsheet': csi_backsheet['2050'].sum(),}


# #### 5.2.2. CdTe

# In[ ]:


cdte_waste = {'Modules' : cdte_Module['total waste'].sum(),
            'Glass' : cdte_glass_cdte['total waste'].sum(),
            'Cadmium': cdte_cadmium['total waste'].sum(),
            'Tellurium': cdte_tellurium['total waste'].sum(),
            'Copper' : cdte_copper_cdte['total waste'].sum(), # No data about the copper recovery, so I assume the same as FRELP
            'Aluminium frames': cdte_aluminium_frames_cdte['total waste'].sum(),
            'Encapsulant': cdte_encapsulant_cdte['total waste'].sum(),} # Here there is no info so I assume the same as the glass


# In[ ]:


# Option for one year, just change the year to the one you need

cdte_waste_2050 = {'Modules' : cdte_Module['2050'].sum(),
            'Glass' : cdte_glass_cdte['2050'].sum(),
            'Cadmium': cdte_cadmium['2050'].sum(),
            'Tellurium': cdte_tellurium['2050'].sum(),
            'Copper' : cdte_copper_cdte['2050'].sum(), # No data about the copper recovery, so I assume the same as FRELP
            'Aluminium frames': cdte_aluminium_frames_cdte['2050'].sum(),
            'Encapsulant': cdte_encapsulant_cdte['2050'].sum(),} # Here there is no info so I assume the same as the glass


# ### 5.3. Recycling bins <a id='#Section4.3'></a>

# #### 5.3.1. cSi

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
            'Energy': csi_encapsulant['total waste'].sum()+csi_backsheet['total waste'].sum()} # Amount of waste that is burned and returned as energy 


# In[ ]:


# Option for one year, just change the year to the one you need

csi_recycled_2050 = {'Modules' : csi_Module['2050'].sum(),
            'Glass' : csi_glass['2050'].sum()*0.98, 
            'Silicon' : csi_silicon['2050'].sum()*0.95,
            'Silver': csi_silver['2050'].sum()*0.95,
            'Copper' : csi_copper['2050'].sum()*0.95,
            'Aluminium frames': csi_aluminium_frames['2050'].sum(), # Assume 100% from the frames
            'Encapsulant': csi_encapsulant['2050'].sum(), # Here the encapsulant is incinerated so, 100% goes out
            'Backsheet': csi_backsheet['2050'].sum(),# Same as encapsulant
            'Landfill': csi_glass['2050'].sum()*(1-0.98) + 
                csi_silicon['2050'].sum()*(1-0.95) + 
                csi_silver['2050'].sum()*(1-0.95) + 
                csi_copper['2050'].sum()*(1-0.95),
            'Energy': csi_encapsulant['2050'].sum()+csi_backsheet['2050'].sum()} 


# #### 5.3.2. CdTe

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


# Option for one year, just change the year to the one you need

cdte_recycled_2050 = {'Modules' : cdte_Module['2050'].sum(),
            'Glass' : cdte_glass_cdte['2050'].sum()*0.9,
            'Cadmium': cdte_cadmium['2050'].sum()*0.95,
            'Tellurium': cdte_tellurium['2050'].sum()*0.95,
            'Copper' : cdte_copper_cdte['2050'].sum()*0.95, # No data about the copper recovery, so I assume the same as FRELP
            'Aluminium frames': cdte_aluminium_frames_cdte['2050'].sum(),
            'Encapsulant': cdte_encapsulant_cdte['2050'].sum()*0.9,# Here there is no info so I assume the same as the glass
            'Landfill':cdte_glass_cdte['2050'].sum()*(1-0.9) +
                cdte_cadmium['2050'].sum()*(1-0.95) +
                cdte_tellurium['2050'].sum()*(1-0.95) +
                cdte_copper_cdte['2050'].sum()*(1-0.95) +
                cdte_encapsulant_cdte['2050'].sum()*(1-0.9),
            } 


# In[ ]:





# In[ ]:





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


material_list_csi = ['glass', 'silicon', 'silver', 'copper', 'aluminium_frames', 'encapsulant', 'backsheet', 'Module']
material_list_cdte = ['cadmium', 'telluride', 'glass_cdte', 'aluminium_frames_cdte', 'Module', 'copper_cdte', 'encapsulant_cdte']


# #### 5.4.1. Sankey Option 1 - Labeled

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
fig.write_image("images/sankey/sankey_labeled.svg")


# #### 5.4.2. Sankey Option 2 - Labeled simplified

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
fig.write_image("images/sankey/sankey_labeled_simplified.svg")


# #### 5.4.3. Sankey Option 3 - Muted

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
fig.write_image("images/sankey/sankey_muted.svg")
#fig.write_image("images/sankey_mute.svg")


# #### 5.4.4. Sankey Option 4 - Muted simplified

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
fig.write_image("images/sankey/sankey_muted_simplified.svg")


# In[ ]:


# Figure for one year 

fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 10,
      thickness = 20,
      line = dict(color = 'black', width = 0.5),
      label = ['', '', '', 
               '', '', '', '', '', '', '', '', ''],
      color = [my_colors['pvwaste'], my_colors['csi_blue'], my_colors['cdte_tiel'], 
               my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['product_green'], my_colors['waste_red'], my_colors['worth_green']],
      hovertemplate= 'Node value is %{value}'
    ),
    link = dict(
      source = [0, 0, 
                1,1,1,1,1,1,1,
                2,2,2,2,2,2, ], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [1, 2,
                3, 4, 5, 6, 9, 10, 11,
                3, 5, 7, 8, 9, 10],
      value = [csi_waste_2050['Modules'], cdte_waste_2050['Modules'], 
               csi_recycled_2050['Glass'], csi_recycled_2050['Silicon'], csi_recycled_2050['Copper'], csi_recycled_2050['Silver'], csi_recycled_2050['Aluminium frames'], csi_recycled_2050['Landfill'],csi_recycled_2050['Energy'],
               cdte_recycled_2050['Glass'], cdte_recycled_2050['Copper'], cdte_recycled_2050['Cadmium'], cdte_recycled_2050['Tellurium'], cdte_recycled_2050['Aluminium frames'], cdte_recycled_2050['Landfill']],
      color = 'rgba(240, 240, 245, 0.65)',
      hovertemplate= 'Link value is %{value}' 
  ))])

fig.update_layout(font_family="Times New Roman", font_size=10)
fig.write_image("images/sankey/sankey_muted_simplified_2050.png")
fig.show()


# In[ ]:





# ---
# ## 6. Cloropeth map option 1 (still under construction)

# In[ ]:


pv_waste_map = csi_Module[['FIPS']].copy()
pv_waste_map['total waste'] = csi_Module['total waste'] + cdte_Module['total waste']
pv_waste_map.to_csv('images/cloropeth/pv_waste_map.csv')

csi_waste_map = csi_Module[['FIPS', 'total waste']]
csi_waste_map.to_csv('images/cloropeth/csi_waste_map.csv')

cdte_waste_map = cdte_Module[['FIPS', 'total waste']]
cdte_waste_map.to_csv('images/cloropeth/cdte_waste_map.csv')


# In[ ]:


from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("images/cloropeth/pv_waste_map.csv",
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
fig.write_image("images/cloropeth/map_allPV_op1.svg")


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
fig.write_image("images/cloropeth/map_allPV_op2.svg")


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
fig.write_image("images/cloropeth/map_allPV_op2.svg")


# In[ ]:




