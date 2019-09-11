
# coding: utf-8

# In[1]:


import os
from os import path
    
import pandas as pd
import urllib.request
import zipfile


# In[2]:


if not os.path.exists("../data/"):
    os.mkdir("../data/")
    
if not os.path.exists("../output/"):
    os.mkdir("../output/")


# In[3]:


#Set resource URLs for downloading
ffiec_census_url = "https://www.ffiec.gov/Census/Census_Flat_Files/CENSUS2019.zip"
census_delineation_url = "https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2018/delineation-files/list1_Sep_2018.xls"


# In[4]:


#Download Census delineation file to get MSA/MD names
urllib.request.urlretrieve(census_delineation_url, "../data/census_delineation.xls")

data_xls = pd.read_excel('../data/census_delineation.xls', 'List 1', index_col=None)
data_xls.to_csv("../data/census_delineation.csv", encoding='utf-8', index=False)
census_df = pd.read_csv("../data/census_delineation.csv", skiprows=2, dtype=object)
census_df["full_county_fips"] = census_df.apply(lambda x: x["FIPS State Code"] + x["FIPS County Code"], axis=1)

#get single name for each Metropolitan or Micropolitan statistical area using CSA over CBSA Title
census_df["MSA/MD Name"] = census_df.apply(lambda x: 
                                   x["CSA Title"] if pd.notnull(x["CSA Title"]) else x["CBSA Title"], axis=1)
census_df = census_df[["CBSA Code", "full_county_fips", "MSA/MD Name"]]
census_df.head(1)


# In[5]:


#Download ZIP archive from FFIEC Census site and extract it
urllib.request.urlretrieve(ffiec_census_url, "../data/ffiec_census_2019.zip")
with zipfile.ZipFile("../data/ffiec_census_2019.zip", 'r') as zip_ref:
    zip_ref.extractall("../data/")


# In[6]:


#load FFIEC Census file and extract relevant fields and resave them
#MFI = median family income
ffiec_census_df = pd.read_csv("../data/Census2019.csv", header=None, dtype=object)
col_names = {0:"hmda_year", 
             1:"msa_md", 
             2:"state_fips", 
             3:"county_fips", 
             4:"census_tract", 
             6:"small_county_flag",
             12:"tract_to_msa_mfi_pct",
             13:"ffiec_mfi",
             14:"total_persons", 
             20:"minority_population_pct", 
             580:"tract_mfi",
             899:"total_1_4_family_units",
             915:"owner_occupied_units", 
             952:"median_housing_age"}

#field order for platform:
#0, 1, 2, 3, 4, 13, 14, 20, 915, 899, 580, 12, 952, 6, msamd_name

#get MSA, state, county, tract codes
ffiec_census_df = ffiec_census_df.iloc[:, [0,1,2,3,4,13,14,20,915,899,580,12,952,6]].copy()
ffiec_census_df.rename(columns=col_names, inplace=True)
print(len(ffiec_census_df))
ffiec_census_df.head()


# In[7]:


#Join MSA/MD name to ffiec_census_df using 5 digit county FIPS
ffiec_census_df["full_county_fips"] = ffiec_census_df.apply(lambda x: x.state_fips + x.county_fips, axis=1)
ffiec_census_df = ffiec_census_df.merge(census_df, how="left", on="full_county_fips")
ffiec_census_df = ffiec_census_df[['hmda_year', 'msa_md', 'state_fips', 'county_fips', 'census_tract',
       'ffiec_mfi', 'total_persons', 'minority_population_pct',
       'owner_occupied_units', 'total_1_4_family_units', 'tract_mfi',
       'tract_to_msa_mfi_pct', 'median_housing_age', 'small_county_flag', 'MSA/MD Name']].copy()
ffiec_census_df.head()


# In[8]:


#set header to platform names
platform_census_header = "Collection Year|MSA/MD|State|County|Census Tract|FFIEC Median Family Income|Population|Minority Population %|Number of Owner Occupied Units |Number of 1 to 4 Family Units |Tract MFI|Tract to MSA Income %|Median Age|Small County|MSA/MD Name"
platform_census_header = platform_census_header.split("|")
ffiec_census_df.columns = platform_census_header
ffiec_census_df.head()


# In[9]:


ffiec_census_df.to_csv("../output/ffiec_census_2019.txt", sep="|", index=False)

