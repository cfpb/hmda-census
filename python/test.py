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
	#
#["2015", "2014", "2013", "2008", "2006"] #breakpoint years for testing
#Censustool.get_ffiec_census_file(years=["2007", "2004", "2003"], download=True, unzip=True)
extracts_dict = Censustool.extract_census_fields(years=["2019"])
#Censustool.get_census_omb_delineation_file(years=Censustool.config_data["ALL_YEARS"])
Censustool.combine_omb_ffiec(years=["2019"])


Censustool.load_to_db()
