#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

import fiona
import geopandas as gp
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import collections
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point, Polygon

get_ipython().run_line_magic('matplotlib', 'inline')


# ### Load all file scenarios

# The files I am going to load are the ones showed in the table below. This is to know which file correspond to what. I have not added the dates in the file name since they are autogenerated and it is a sanity check for me, but in reality the dates (numbers in front of the file name scenario) don't matter.
# ![scenarios_info.png](scenarios_info.png)

# In[3]:


cwd = os.getcwd()


# #### NAICS locations

# ##### Manufacturing NAICS

# In[44]:


man_min_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_min_v3', 'plants.csv'))
man_min_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_min_v3', 'products.csv'))
man_min_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_min_v3', 'transportation.csv'))
man_min_naics_pl_emissions = 0 # dummy
man_min_naics_pl_outputs = 0 # dummy
man_min_naics_tr_emissionsn = 0 # dummy


# In[45]:


man_med_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_med_v3', 'plants.csv'))
man_med_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_med_v3', 'products.csv'))
man_med_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_med_v3', 'transportation.csv'))
man_med_naics_pl_emissions = 0 # dummy
man_med_naics_pl_outputs = 0 # dummy
man_med_naics_tr_emissionsn = 0 # dummy


# In[48]:


man_max_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_max_v3', 'plants.csv'))
man_max_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_max_v3', 'products.csv'))
man_max_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230313_Manufacturing_max_v3', 'transportation.csv'))
man_max_naics_pl_emissions = 0 # dummy
man_max_naics_pl_outputs = 0 # dummy
man_max_naics_tr_emissionsn = 0 # dummy 


# ##### Recycling NAICS
# ###### *NOTE: The plant outputs file has a typo, "oputputs". I did not fix it because realized it after I run all scenarios. Just watch out and write it wrongly, this is for all OCD's in the world, I am truly sorry.*

# In[85]:


rec_min_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_min_v5', 'plants.csv'))
rec_min_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_min_v5', 'products.csv'))
rec_min_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_min_v5', 'transportation.csv'))
rec_min_naics_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_min_v5', 'plant_emissions.csv'))
rec_min_naics_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_min_v5', 'plant_oputputs.csv'))
rec_min_naics_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_min_v5', 'transportation_emissions.csv'))


# In[86]:


rec_med_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_med_v5', 'plants.csv'))
rec_med_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_med_v5', 'products.csv'))
rec_med_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_med_v5', 'transportation.csv'))
rec_med_naics_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_med_v5', 'plant_emissions.csv'))
rec_med_naics_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_med_v5', 'plant_oputputs.csv'))
rec_med_naics_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_med_v5', 'transportation_emissions.csv'))


# In[87]:


rec_max_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_max_v5', 'plants.csv'))
rec_max_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_max_v5', 'products.csv'))
rec_max_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_max_v5', 'transportation.csv'))
rec_max_naics_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_max_v5', 'plant_emissions.csv'))
rec_max_naics_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_max_v5', 'plant_oputputs.csv'))
rec_max_naics_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230314_Recycling_max_v5', 'transportation_emissions.csv'))


# In[88]:


rec_midsuper_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_midsuper_v5', 'plants.csv'))
rec_midsuper_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_midsuper_v5', 'products.csv'))
rec_midsuper_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_midsuper_v5', 'transportation.csv'))
rec_midsuper_naics_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_midsuper_v5', 'plant_emissions.csv'))
rec_midsuper_naics_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_midsuper_v5', 'plant_oputputs.csv'))
rec_midsuper_naics_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_midsuper_v5', 'transportation_emissions.csv'))


# In[89]:


rec_super_naics_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_super_v5', 'plants.csv'))
rec_super_naics_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_super_v5', 'products.csv'))
rec_super_naics_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_super_v5', 'transportation.csv'))
rec_super_naics_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_super_v5', 'plant_emissions.csv'))
rec_super_naics_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_super_v5', 'plant_oputputs.csv'))
rec_super_naics_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230315_Recycling_super_v5', 'transportation_emissions.csv'))


# #### 40209 locations

# ##### Manufacturing 40209 communities

# In[90]:


man_min_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_min_v6', 'plants.csv'))
man_min_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_min_v6', 'products.csv'))
man_min_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_min_v6', 'transportation.csv'))
man_min_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_min_v6', 'plant_emissions.csv'))
man_min_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_min_v6', 'plant_oputputs.csv'))
man_min_40209_tr_emissionsn = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_min_v6', 'transportation_emissions.csv'))


# In[91]:


man_med_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_med_v6', 'plants.csv'))
man_med_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_med_v6', 'products.csv'))
man_med_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_med_v6', 'transportation.csv'))
man_med_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_med_v6', 'plant_emissions.csv'))
man_med_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_med_v6', 'plant_oputputs.csv'))
man_med_40209_tr_emissionsn = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_med_v6', 'transportation_emissions.csv'))


# In[92]:


man_max_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_max_v6', 'plants.csv'))
man_max_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_max_v6', 'products.csv'))
man_max_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_max_v6', 'transportation.csv'))
man_max_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_max_v6', 'plant_emissions.csv'))
man_max_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_max_v6', 'plant_oputputs.csv'))
man_max_40209_tr_emissionsn = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Manufacturing_max_v6', 'transportation_emissions.csv'))


# ##### Recycling 40209 communities

# In[93]:


rec_min_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_min_v6', 'plants.csv'))
rec_min_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_min_v6', 'products.csv'))
rec_min_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_min_v6', 'transportation.csv'))
rec_min_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_min_v6', 'plant_emissions.csv'))
rec_min_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_min_v6', 'plant_oputputs.csv'))
rec_min_40209_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_min_v6', 'transportation_emissions.csv'))


# In[94]:


rec_med_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_med_v6', 'plants.csv'))
rec_med_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_med_v6', 'products.csv'))
rec_med_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_med_v6', 'transportation.csv'))
rec_med_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_med_v6', 'plant_emissions.csv'))
rec_med_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_med_v6', 'plant_oputputs.csv'))
rec_med_40209_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_med_v6', 'transportation_emissions.csv'))


# In[95]:


rec_max_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_max_v6', 'plants.csv'))
rec_max_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_max_v6', 'products.csv'))
rec_max_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_max_v6', 'transportation.csv'))
rec_max_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_max_v6', 'plant_emissions.csv'))
rec_max_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_max_v6', 'plant_oputputs.csv'))
rec_max_40209_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_max_v6', 'transportation_emissions.csv'))


# In[96]:


rec_midsuper_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_midsuper_v6', 'plants.csv'))
rec_midsuper_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_midsuper_v6', 'products.csv'))
rec_midsuper_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_midsuper_v6', 'transportation.csv'))
rec_midsuper_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_midsuper_v6', 'plant_emissions.csv'))
rec_midsuper_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_midsuper_v6', 'plant_oputputs.csv'))
rec_midsuper_40209_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_midsuper_v6', 'transportation_emissions.csv'))


# In[97]:


rec_super_40209_plants = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_super_v6', 'plants.csv'))
rec_super_40209_products = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_super_v6', 'products.csv'))
rec_super_40209_transportation = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_super_v6', 'transportation.csv'))
rec_super_40209_pl_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_super_v6', 'plant_emissions.csv'))
rec_super_40209_pl_outputs = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_super_v6', 'plant_oputputs.csv'))
rec_super_40209_tr_emissions = pd.read_csv(os.path.join(cwd, 'scenarios', '20230316_Recycling_super_v6', 'transportation_emissions.csv'))


# ### Prepare files to plot

# In[98]:


facility = ['man', 'rec']
factor = ['min', 'med', 'max', 'midsuper', 'super']
location = ['naics', '40209']
output_type = ['plants', 'products', 'transportation', 'pl_emissions', 'pl_outputs', 'tr_emissions']
simulation_years=26


# In[99]:


print('There are {} chosen locations for rec_min_naics_plants.'.format(len(rec_min_naics_plants)/simulation_years))
print('There are {} chosen locations for rec_med_naics_plants.'.format(len(rec_med_naics_plants)/simulation_years))
print('There are {} chosen locations for rec_max_naics_plants.'.format(len(rec_max_naics_plants)/simulation_years))
print('There are {} chosen locations for rec_midsuper_naics_plants.'.format(len(rec_midsuper_naics_plants)/simulation_years))
print('There are {} chosen locations for rec_super_naics_plants.'.format(len(rec_super_naics_plants)/simulation_years))


# In[100]:


print('There are {} chosen locations for rec_min_naics_plants.'.format(len(rec_min_40209_plants)/simulation_years))
print('There are {} chosen locations for rec_med_naics_plants.'.format(len(rec_med_40209_plants)/simulation_years))
print('There are {} chosen locations for rec_max_naics_plants.'.format(len(rec_max_40209_plants)/simulation_years))
print('There are {} chosen locations for rec_midsuper_naics_plants.'.format(len(rec_midsuper_40209_plants)/simulation_years))
print('There are {} chosen locations for rec_super_naics_plants.'.format(len(rec_super_40209_plants)/simulation_years))


# In[120]:


rec_min_40209_plants_nm = rec_min_40209_plants[rec_min_40209_plants['location name'] == 'San Juan, New Mexico']
rec_med_40209_plants_nm = rec_med_40209_plants[rec_med_40209_plants['location name'] == 'San Juan, New Mexico']
rec_max_40209_plants_nm = rec_max_40209_plants[rec_max_40209_plants['location name'] == 'San Juan, New Mexico']
rec_midsuper_40209_plants_nm = rec_midsuper_40209_plants[rec_midsuper_40209_plants['location name'] == 'San Juan, New Mexico']
rec_super_40209_plants_nm = rec_super_40209_plants[rec_super_40209_plants['location name'] == 'San Juan, New Mexico']


# In[121]:


rec_midsuper_40209_plants_nm.keys()


# In[140]:


x_axis_years = [2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,2050]


# In[174]:


from itertools import cycle

sns.set_palette('Set2')
sns.set_style({"xtick.direction": "in","ytick.direction": "in"})
ls = ['-','--',':','-.','-','--',':','-.','-','--',':','-.','-','--',':','-.','-','--',':','-.','-','--',':','-.']
linecycler = cycle(ls)

fig, ax = plt.subplots(sharey=True)

rec_min_40209_plants_nm_plot = sns.lineplot(data=rec_min_40209_plants_nm, x='year', y='total cost ($)', ax=ax, label='0.5', markers=True,linestyle=next(linecycler))
rec_med_40209_plants_nm_plot = sns.lineplot(data=rec_med_40209_plants_nm, x='year', y='total cost ($)',ax=ax, label='1',  markers=True, linestyle=next(linecycler))
rec_max_40209_plants_nm_plot = sns.lineplot(data=rec_max_40209_plants_nm, x='year', y='total cost ($)',ax=ax, label='2',  markers=True, linestyle=next(linecycler))
rec_midsuper_40209_plants_nm_plot = sns.lineplot(data=rec_midsuper_40209_plants_nm, x='year', y='total cost ($)', ax=ax, label='5', linestyle=next(linecycler))
rec_midsuper_40209_plants_nm_plot = sns.lineplot(data=rec_super_40209_plants_nm, x='year', y='total cost ($)',ax=ax, label='10',  markers=True, linestyle=next(linecycler))
ax.set(yscale='log')
ax.set_xticks(range(len(x_axis_years)))
ax.set_xticklabels(x_axis_years)
ax.tick_params(axis='x', rotation=45)
ax.set_xlabel('Year')
ax.set_ylabel('Total costs ($)')
ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_title('40209 Recycling Plants')
plt.margins(x=0)
plt.show()


# 

# In[176]:


from itertools import cycle

sns.set_palette('Set2')
sns.set_style({"xtick.direction": "in","ytick.direction": "in"})
ls = ['-','--',':','-.','-','--',':','-.','-','--',':','-.','-','--',':','-.','-','--',':','-.','-','--',':','-.']
linecycler = cycle(ls)

fig, ax = plt.subplots(sharey=True)

rec_min_40209_plants_nm_plot = sns.lineplot(data=rec_min_40209_plants_nm, x='year', y='utilization factor (%)', ax=ax, label='0.5', markers=True,linestyle=next(linecycler))
rec_med_40209_plants_nm_plot = sns.lineplot(data=rec_med_40209_plants_nm, x='year', y='utilization factor (%)',ax=ax, label='1',  markers=True, linestyle=next(linecycler))
rec_max_40209_plants_nm_plot = sns.lineplot(data=rec_max_40209_plants_nm, x='year', y='utilization factor (%)',ax=ax, label='2',  markers=True, linestyle=next(linecycler))
rec_midsuper_40209_plants_nm_plot = sns.lineplot(data=rec_midsuper_40209_plants_nm, x='year', y='utilization factor (%)', ax=ax, label='5', linestyle=next(linecycler))
rec_midsuper_40209_plants_nm_plot = sns.lineplot(data=rec_super_40209_plants_nm, x='year', y='utilization factor (%)',ax=ax, label='10',  markers=True, linestyle=next(linecycler))
ax.set(yscale='log')
ax.set_xticks(range(len(x_axis_years)))
ax.set_xticklabels(x_axis_years)
ax.tick_params(axis='x', rotation=45)
ax.set_xlabel('Year')
ax.set_ylabel('Utilization factor ($)')
ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_title('40209 Recycling Plants')
plt.margins(x=0)
plt.show()


# Notes: This plot shows that the plant is always at 100% capacity once the waste starts receiving waste. Interestingly, it looks like the waste takes longer to be processed when the plant is expensive.

# In[180]:


rec_midsuper_40209_plants


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


# Plot base map
world = gp.read_file(gp.datasets.get_path("naturalearth_lowres"))
ax = world.plot(color="white", edgecolor="0.5", figsize=(14, 7))
ax.set_ylim([23, 50])
ax.set_xlim([-128, -65])

# Draw transportation lines
data = pd.read_csv(f"output/{simulation}/transportation.csv")
lines = [
    [
        (
            row["source longitude (deg)"],
            row["source latitude (deg)"],
        ),
        (
            row["destination longitude (deg)"],
            row["destination latitude (deg)"],
        ),
    ]
    for (index, row) in data.iterrows()
]
ax.add_collection(
    collections.LineCollection(
        lines,
        linewidths=0.01,
        zorder=1,
        alpha=0.5,
        color="0.7",
    )
)

# Draw source points
points = gp.points_from_xy(
    data["source longitude (deg)"],
    data["source latitude (deg)"],
)
gp.GeoDataFrame(data, geometry=points).plot(ax=ax, color="0.5", markersize=1)

# Draw destination points
points = gp.points_from_xy(
    data["destination longitude (deg)"],
    data["destination latitude (deg)"],
)
gp.GeoDataFrame(data, geometry=points).plot(ax=ax, color="red", markersize=50)

