from census_functions import CensusTools

Censustool = CensusTools()

#Replace 2022 with the year for which you want to generate the combined census file
year = "2022"

#download census files
Censustool.get_ffiec_census_file(years=[2022], download=True, unzip=True, move=True)

Censustool.extract_census_fields(years=[2022], sep='|', save_csv=True)
Censustool.extract_census_fields(years=[2022], sep=',', save_csv=True)
#download OMB MSA MD delineation files
Censustool.get_census_omb_delineation_file(years=[2022])

#Combine census and delineation files 
census_df_dict = Censustool.combine_omb_ffiec(years=[2022], sep="|")

#The Combined census file will be created as ../output/output/ffiec_census_msamd_names_2022.txt
