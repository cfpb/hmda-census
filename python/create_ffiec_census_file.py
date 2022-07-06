from census_functions import CensusTools

Censustool = CensusTools()

#Replace <year> with the year for which you want to generate the combined census file
year = "<year>"

#download census files
Censustool.get_ffiec_census_file(years=Censustool.config_data[year], download=True, unzip=True, move=True)

#download OMB MSA MD delineation files
Censustool.get_census_omb_delineation_file(years=Censustool.config_data[year])

#Combine census and delineation files 
census_df_dict = Censustool.combine_omb_ffiec(years=Censustool.config_data[year], sep="|")

#The Combined census file will be created as ../output/output/ffiec_census_msamd_names_<year>.txt
