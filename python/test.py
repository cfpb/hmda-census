import os
from os import path
from os import listdir
from os.path import isfile, join

import pandas as pd 
import psycopg2
import requests as re 

from census_functions import CensusTools

Censustool = CensusTools()

test_years = ["2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", 
 "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003"]

#download census files
#Censustool.get_ffiec_census_file(years=Censustool.config_data["ALL_YEARS"], download=True, unzip=False, move=False)

#Unzip Census files
#Censustool.get_ffiec_census_file(years=Censustool.config_data["ALL_YEARS"], download=False, unzip=True, move=False)

#move Census files and empty folders
#Censustool.get_ffiec_census_file(years=Censustool.config_data["ALL_YEARS"], download=False, unzip=False, move=True)

#extract desired columns from census files
#extracts_dict = Censustool.extract_census_fields(years=Censustool.config_data["ALL_YEARS"])

#download OMB MSA MD delineation files
#Censustool.get_census_omb_delineation_file(years=Censustool.config_data["ALL_YEARS"])

#combine OMB and FFIEC census data
#Censustool.combine_omb_ffiec(years=test_years)

#load combined data to database
Censustool.load_to_db(years=test_years)
