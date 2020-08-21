
# coding: utf-8

# In[2]:


import pandas as pd

#load FFIEC and Platform data files
FFIEC_GEO_FILE = "../data/census2018.csv"
PLATFORM_GEO_FILE = "../data/platform_geo_file_5_31_2019.txt"

platform_geo = pd.read_csv(PLATFORM_GEO_FILE, sep="|", dtype=object)
ffiec_df = pd.read_csv(FFIEC_GEO_FILE, header=None, dtype=object)


# In[3]:


#set up FFIEC data
#FFIEC Census data includes MD in the MSA field
col_names = {0:"hmda_year", 1:"msa", 2:"state", 3:"county", 4:"tract", 14:"total_persons", 
             20:"min_pop_pct", 915:"owner_occupied", 899:"1_4_units",580:"tract_mfi", 12:"tract_to_msa_mfi_pct",
            952:"median_age", 13:"ffiec_mfi"}

#get MSA, state, county, tract codes
ffiec_census_data = ffiec_df.iloc[:, [0,1,2,3,4,13,14,20,915,899,580,12,952]].copy()
ffiec_census_data.rename(columns=col_names, inplace=True)
ffiec_census_data.head()


# In[4]:


#create MSA to tract map from FFIEC file

print(len(ffiec_census_data), "total records")
print(len(ffiec_census_data.msa.unique()), "distinct MSA/MD records")
print(len(ffiec_census_data.state.unique()), "distinct State records")
print(len(ffiec_census_data.county.unique()), "distinct County records")
print(len(ffiec_census_data.tract.unique()), "distinct Tract records")
ffiec_census_data.head()


# In[5]:


#create MSA to tract map from Platform
print(len(platform_geo), "total records")
print(len(platform_geo["MSA/MD"].unique()), "distinct MSA/MD records")
print(len(platform_geo["State"].unique()), "distinct State records")
print(len(platform_geo["County"].unique()), "distinct county records")
print(len(platform_geo["Census Tract"].unique()), "distinct census tracts")

platform_geo.head()


# In[6]:


#compare all geographic sets between dataframes
#MSA/MD
platform_msas = set(platform_geo["MSA/MD"])
ffiec_msas = set(ffiec_census_data.msa)
print(platform_msas == ffiec_msas, "MSA/MD set comparison")

#State
platform_states = set(platform_geo["State"])
ffiec_states = set(ffiec_census_data.state)
print(platform_states == ffiec_states, "State set comparison")

#County
platform_counties = set(platform_geo["County"])
ffiec_counties = set(ffiec_census_data.county)
print(platform_counties == ffiec_counties, "County set comparison")

#tract
platform_tracts = set(platform_geo["Census Tract"])
ffiec_tracts = set(ffiec_census_data.tract)
print(platform_tracts == ffiec_tracts, "Tract set comparison")


# In[7]:


#MSA to state maps
for msa in set(platform_geo["MSA/MD"]):
    platform_states = set(platform_geo.State[platform_geo["MSA/MD"]==msa])
    ffiec_states = set(ffiec_census_data.state[ffiec_census_data.msa==msa])
    if platform_states != ffiec_states:
        print("MSA {msa} has mismatched state sets".format(msa))

#MSA to county maps
for msa in set(platform_geo["MSA/MD"]):
    platform_counties = set(platform_geo.County[platform_geo["MSA/MD"]==msa])
    ffiec_counties = set(ffiec_census_data.county[ffiec_census_data.msa==msa])
    if platform_counties != ffiec_counties:
        print("MSA {msa} has mismatched counties sets".format(msa))
        
#MSA to tract maps
for msa in set(platform_geo["MSA/MD"]):
    platform_tracts = set(platform_geo["Census Tract"][platform_geo["MSA/MD"]==msa])
    ffiec_tracts = set(ffiec_census_data.tract[ffiec_census_data.msa==msa])
    if platform_tracts != ffiec_tracts:
        print("MSA {msa} has mismatched tracts sets".format(msa))
        
#state to county maps
for state in set(platform_geo.State):
    platform_counties = set(platform_geo.County[platform_geo.State==state])
    ffiec_counties = set(ffiec_census_data.county[ffiec_census_data.state==state])
    if platform_counties != ffiec_counties:
        print("State {state} has mismatched county sets".format(state))
        
#state to tract maps
for state in set(platform_geo.State):
    platform_tracts = set(platform_geo["Census Tract"][platform_geo.State==state])
    ffiec_tracts = set(ffiec_census_data.tract[ffiec_census_data.state==state])
    if platform_tracts != ffiec_tracts:
        print("State {state} has mismatched tract sets".format(state))
        
#county to tract maps
for county in set(platform_geo.County):
    platform_tracts = set(platform_geo["Census Tract"][platform_geo.County==county])
    ffiec_tracts = set(ffiec_census_data.tract[ffiec_census_data.county==county])
    if platform_tracts != ffiec_tracts:
        print("County {county} has mismatched tract sets".format(county))
        
print("done")

