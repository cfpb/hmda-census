from census_functions import CensusTools

Censustool = CensusTools()

#Replace <year> with the year for which you want to generate the combined census file
Censustool.config_data["year"] = [2023]

# download census files
Censustool.get_ffiec_census_file(years=Censustool.config_data["year"], download=True, unzip=True, move=True)
print()
print("Done: get_ffiec_census_file")
print("-------")
print()


# # # #extract desired columns from census files
extracts_dict = Censustool.extract_census_fields(years=Censustool.config_data["year"]) #sep can be changed to comma for CSV output
print(extracts_dict.keys)
print()
print("Done: extract_census_fields")
print("-------")
print()


#download OMB MSA MD delineation files
# Censustool.get_census_omb_delineation_file(years=Censustool.config_data["year"])
print()
print("Done: get_census_omb_delineation_file")
print("-------")
print()

#Combine census and delineation files 
census_df_dict = Censustool.combine_omb_ffiec(years=Censustool.config_data["year"], sep="|")
print()
print("Done: combine_omb_ffiec")
print("-------")
print()
#The Combined census file will be created as ../output/output/ffiec_census_msamd_names_<year>.txt
print("Done")

	