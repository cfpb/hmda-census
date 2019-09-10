
# coding: utf-8

# In[1]:


import pandas as pd
import urllib.request
import zipfile


# In[2]:


#Download ZIP archive from FFIEC Census site and extract it
ffiec_census_url = "https://www.ffiec.gov/Census/Census_Flat_Files/CENSUS2019.zip"
urllib.request.urlretrieve(ffiec_census_url, "../data/ffiec_census_2019.zip")
with zipfile.ZipFile("../data/ffiec_census_2019.zip", 'r') as zip_ref:
    zip_ref.extractall("../data/")


# In[3]:


#load FFIEC Census file and extract relevant fields and resave them
#MFI = median family income
ffiec_census_df = pd.read_csv("../data/Census2019.csv", header=None)
col_names = {0:"hmda_year", 
             1:"msa_md", 
             2:"state_fips", 
             3:"county_fips", 
             4:"census_tract", 
             12:"tract_to_msa_mfi_pct",
             13:"ffiec_mfi",
             14:"total_persons", 
             20:"minority_population_pct", 
             580:"tract_mfi",
             899:"total_1_4_family_units",
             915:"owner_occupied_units", 
             952:"median_housing_age"}

#get MSA, state, county, tract codes
ffiec_census_df = ffiec_census_df.iloc[:, [0,1,2,3,4,13,14,20,915,899,580,12,952]].copy()
ffiec_census_df.rename(columns=col_names, inplace=True)
print(len(ffiec_census_df))
ffiec_census_df.head()


# In[4]:


ffiec_census_df.to_csv("../output/ffiec_census_2019.txt", sep="|", index=False)

