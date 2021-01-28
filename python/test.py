import os
from os import path
from os import listdir
from os.path import isfile, join

import pandas as pd 
import psycopg2
import requests as re 

from census_functions import CensusTools

Censustool = CensusTools()
#Censustool.config_data["ALL_YEARS"] = 2018
#download census files
Censustool.get_ffiec_census_file(years=Censustool.config_data["ALL_YEARS"], download=True, unzip=False, move=False)

#Unzip Census files
#Censustool.get_ffiec_census_file(years=Censustool.config_data["ALL_YEARS"], download=False, unzip=True, move=False)
#2017 is zipped twice, the second call unzips the sub archive
#Censustool.get_ffiec_census_file(years=["2017"], download=False, unzip=True, move=False)

#move Census files and empty folders
#Censustool.get_ffiec_census_file(years=Censustool.config_data["ALL_YEARS"], download=False, unzip=False, move=True)

#extract desired columns from census files
#extracts_dict = Censustool.extract_census_fields(years=Censustool.config_data["ALL_YEARS"]) #sep can be changed to comma for CSV output

#download OMB MSA MD delineation files
Censustool.get_census_omb_delineation_file(years=Censustool.config_data["ALL_YEARS"])

#combine OMB and FFIEC census data and create MSA/MD name description files
census_df_dict = Censustool.combine_omb_ffiec(years=Censustool.config_data["ALL_YEARS"], sep=",")
census_df_dict = Censustool.combine_omb_ffiec(years=Censustool.config_data["ALL_YEARS"], sep="|")

#load combined data to database
#Censustool.load_to_db(years=Censustool.config_data["ALL_YEARS"])
