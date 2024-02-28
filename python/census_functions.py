### This is a code utility library that contains logic to download and combine the FFIEC Census flat file and
# Census/OMB delineation file for use with HMDA data.

import os
from os import path
from os import listdir
from os.path import isfile, join
import shutil

import pandas as pd
import psycopg2
import requests
import yaml
import zipfile


#handle in config load



class CensusTools(object):
	"""
	"""

	def __init__(self, config_file="python/census_config.yaml"):
		"""
		Sets up the configuration for file paths and download URLs
		"""

		with open(config_file, "r") as in_config:
			self.config_data = yaml.safe_load(in_config)
		
		print()
		for path in self.config_data["FOLDER_PATHS"]:
			if not os.path.exists(self.config_data[path]):
				print("creating {folder}".format(folder=self.config_data[path]))
				os.makedirs(self.config_data[path])

		self.db_params = { 
					"host":"localhost",
					"user":os.environ.get("USER"),
					"password":os.environ.get("PASSWORD"),
					"dbname": "hmda",
					"port": 5432,
					"sslmode": "disable"
					}



	def connect(self, params):
			"""
			Connects to a postgres database instance

			PARAMETERS:
			params: host, user, password, dbname, port, sslmode
			"""

			try:
				conn = psycopg2.connect(**params)
				return conn, conn.cursor()
			except psycopg2.Error as e:
				print("bad connection attempt, ", e)


	def get_ffiec_census_file(self, years=[], unzip=True, move=True, download=True):
		"""
		Retrieves Census flat file data from the FFIEC website.
		Each file is 1 year of data intended to be used with HMDA data.
		Files are available from 1990-2019. New files are typically published in the fall.

		PARAMETERS:
		years: a list of which years of data to download, unzip and rename
		unzip, if true: unzips all zip files in the DATA_PATH location
		move, if true: moves all files in the from sub folders to the main data folder
		"""
		print(years)
		if len(years) < 1:
			years = self.config_data["ALL_YEARS"]

		if download:

			base_url = self.config_data["FFIEC_CENSUS_BASE_URL"]
			for year in years:

				local_file_name = "ffiec_census_{year}.zip".format(year=year)
				print()
				print("getting data for {year}".format(year=year))

				if int(year) >= 2015:
					census_year_url = base_url + "CENSUS{year}.zip".format(year=year)

				elif int(year) == 2014:
					census_year_url = base_url + "CENSUS{year}.ZIP".format(year=year)

				elif int(year) in [2012, 2013]:
					census_year_url  = base_url + "Census{year}.zip".format(year=year)

				elif int(year) >= 2008:
					census_year_url = base_url + "census{year}.zip".format(year=year)

				else:
					census_year_url = base_url + "Zip%20Files/{year}.zip".format(year=year)

				if self.config_data["DEBUG"]:
					print("***census_year_url***")
					print(census_year_url)

				census_resp = requests.get(census_year_url)
				print("saving data for {year} as {name}".format(year=year, name=local_file_name))

				with open(self.config_data["CENSUS_PATH"] + local_file_name, "wb") as infile:
					infile.write(census_resp.content)


		if unzip:

			##get all files in data dir with .zip extension
			print()
			print("Unzipping files in {folder}".format(folder=self.config_data["CENSUS_PATH"]))
			census_files = [f for f in listdir(self.config_data["CENSUS_PATH"]) if isfile(join(self.config_data["CENSUS_PATH"], f))]
			census_files = [f for f in census_files if f[-4:] == ".zip"]
   
			if self.config_data["DEBUG"]:
				print()
				print("census files to unzip")
				print(census_files)

			#unzip all census files
			for file in census_files:
				if file[-8:-4] in years:
					with zipfile.ZipFile(self.config_data["CENSUS_PATH"] + file, 'r') as zip_ref:
						
						if self.config_data["DEBUG"]:
							print()
							print("files in archive:")
							print(zip_ref.namelist())
						
						for file in zip_ref.namelist(): #iterate over files in archive
							print()
							print("extracting data and docs for ", file)
							#handle txt file: extract and rename to census_dict_year.doc or census_dict_year.docx
							if file[-4:] in [".doc"]:
								new_name = "census_docs_{year}".format(year=file[-8:-4]) + file[-4:]
								new_name = new_name.lower()

								with open(self.config_data["CENSUS_DOCS"] + new_name, "wb") as outfile:
									outfile.write(zip_ref.read(file))

							elif file[-4:] in ["docx"]:
								new_name = "census_docs_{year}".format(year=file[-9:-5]) + file[-5:]
								new_name = new_name.lower()

								with open(self.config_data["CENSUS_DOCS"] + new_name, "wb") as outfile:
									outfile.write(zip_ref.read(file))

							#handle data file: extract and rename to census_data_year.DAT or census_data_year.csv
							elif file[-4:] in [".DAT", ".csv", ".dat"]:
								new_name = "census_data_{year}".format(year=file[-8:-4]) + file[-4:]
								new_name = new_name.lower()

								with open(self.config_data["CENSUS_PATH"] + new_name, "wb") as outfile:
									outfile.write(zip_ref.read(file))

							elif file[-4:] == ".zip":
								print("extracting nested zip archive")
								new_name = "census_data_{year}".format(year=file[-8:-4]) + file[-4:]
								new_name = new_name.lower()

								with open(self.config_data["CENSUS_PATH"] + new_name, "wb") as outfile:
									outfile.write(zip_ref.read(file))


		if move:

			#move all census files from their sub folders to the main folder
			#delete empty folder
			print()
			print("Moving all FFIEC Census files to {folder} and removing old sub folders".format(folder=self.config_data["CENSUS_PATH"]))
			directories = [f for f in listdir(self.config_data["CENSUS_PATH"]) if not isfile(join(self.config_data["CENSUS_PATH"], f))]
			
			if self.config_data["DEBUG"]:
				print("directories:", directories)

			#2017 has a sub archive that needs to be handled 
			try: #handle extra zip archive in 2017 data
				files_2017 = [f for f in listdir(self.config_data["CENSUS_PATH"] + folder) if isfile(join(self.config_data["CENSUS_PATH"] + folder, f))]
				for file_2017 in files_2017:
					shutil.move(self.config_data["CENSUS_PATH"] + folder + "/ffiec_census_2017/" + file_2017, self.config_data["CENSUS_PATH"])
				os.remove(self.config_data["CENSUS_PATH"] + "census_data_2017.zip")
				
			except:
				print("didn't move 2017 census folder properly")


			for folder in directories:
				files = [f for f in listdir(self.config_data["CENSUS_PATH"] + folder) if isfile(join(self.config_data["CENSUS_PATH"] + folder, f))]

				if self.config_data["DEBUG"]:
					print()
					print("files:", files)



				for file in files:
					#remove DS store instead of moving it
					if file == ".DS_Store":
						os.remove(self.config_data["CENSUS_PATH"] + folder + "/" + file)

					else:
						print()
						print("moving:", file)
						shutil.move(self.config_data["CENSUS_PATH"] + folder + "/" + file, self.config_data["CENSUS_PATH"])
					
					
					os.rmdir(self.config_data["CENSUS_PATH"] + folder)


	def extract_census_fields(self, years=[], sep=None, save_csv=True):

		"""
		Extracts the enumerated fields from an FFIEC Census data CSV
		Returns a pandas dataframe with the selected fields

		Notes: 
		- not all FFIEC census data is in CSV format and data contents may change between years
		- 2009 and earlier files are in .DAT format and require fixed width file loads
		
		
		PARAMETERS:
		field_dict: a name, field number dictionary. The keys will be used as column names, 
					the values will be used to select fields from the FFIEC Census file.
			- The data file documentation is not zero-indexed.
			- Pass in the index in the documentation. Do not adjust for zero-indexing, 
				that is handled in this code.

		census_files: the names of the census files used for the extracts
		data_path: the path to the census file to be used for extracts
		save_csv: write the extracts to a CSV file
		sep: separater character to use when writing file extracts
		"""
		if len(years) < 1:
			print()
			print("No year list passed, using ALL_YEARS from config file")
			years = self.config_data["ALL_YEARS"]

		if sep is None:
			sep = self.config_data["SEP"]

		if sep == "|":
			file_ending = "txt"
		else:
			file_ending = "csv"

		data_path = self.config_data["CENSUS_PATH"] #set path to data files

		field_dict_2022 = self.config_data["extract_fields_2022_on"] #fields to extract from file
		field_dict_2003 = self.config_data["extract_fields_2003_to_2021"] #fields to extract from file
		field_dict_2002 = self.config_data["extract_fields_2002_prior"] #fields to extract from file

		field_names_2022 = list(field_dict_2022.keys())
		field_names_2003 = list(field_dict_2003.keys())
		field_names_2002 = list(field_dict_2002.keys())

		field_nums_one_idx_2022 = list(field_dict_2022.values())
		field_nums_one_idx_2003 = list(field_dict_2003.values())
		field_nums_one_idx_2002 = list(field_dict_2002.values())

		field_nums_2022 = [int(num) - 1 for num in field_nums_one_idx_2022] #adjust for non-0 indexing in FFIEC file dictionary
		field_nums_2003 = [int(num) - 1 for num in field_nums_one_idx_2003] #adjust for non-0 indexing in FFIEC file dictionary
		field_nums_2002 = [int(num) - 1 for num in field_nums_one_idx_2002] #adjust for non-0 indexing in FFIEC file dictionary

		return_dict = {} #for returning year keyed dataframes of census data
		for year in years:
			#set file name
			print()
			print("processing data for {year}".format(year=year))
			#data are loaded as objects to preserve integrity of geographic identifiers with leading 0s
			if int(year) >= 2022:
				print("using CSV data file")
				census_data = pd.read_csv(data_path + "census_data_{year}.csv".format(year=year), 
										  usecols=field_nums_2022, 
										  header=None, 
										  dtype=object,
										  sep=",") #csv is the base format after extraction, don't change this unless you really mean it

				census_data = census_data[field_nums_2022]
				census_data.columns = field_names_2022
    
			elif int(year) >= 2012 and int(year) <= 2021:
				print("using CSV data file")
				census_data = pd.read_csv(data_path + "census_data_{year}.csv".format(year=year), 
										  usecols=field_nums_2003, 
										  header=None, 
										  dtype=object,
										  sep=",") #csv is the base format after extraction, don't change this unless you really mean it

				census_data = census_data[field_nums_2003]
				census_data.columns = field_names_2003

			else:
				#load fixed width spec for old FFIEC census data (only verified on 2006 year)
				print("using fixed width data file")
				if int(year) >= 2003:
					#set fixed width format spec
					fwf_spec = pd.read_csv(self.config_data["ffiec_census_2006_fwf_spec"])

				else:
					#set fixed width format spec
					fwf_spec = pd.read_csv(self.config_data["ffiec_census_2002_fwf_spec"])	

									
				census_data = pd.read_fwf(data_path + "census_data_{year}.dat".format(year=year), 
										  widths=fwf_spec["Length"], 
										  header=None, 
										  dtype=object)

				if int(year) >= 2022:
					#remove fields not in extract dictionary
					census_data = census_data[field_nums_2022]
					#set column names
					census_data.columns = field_names_2022
     
				elif int(year) >= 2003 and int(year) <= 2021 :
					#remove fields not in extract dictionary
					census_data = census_data[field_nums_2003]
					#set column names
					census_data.columns = field_names_2003

				else:
					#remove fields not in extract dictionary
					census_data = census_data[field_nums_2002]
					#set column names
					census_data.columns = field_names_2002
     
			print("Path: ", self.config_data["OUT_PATH"] + "census_data_extract_{year}.txt".format(year=year))
			if save_csv:
				census_data.to_csv(self.config_data["OUT_PATH"] + "census_data_extract_{year}.txt".format(year=year), 
								   index=False,
								   sep="|")
				census_data.to_csv(self.config_data["OUT_PATH"] + "census_data_extract_{year}.csv".format(year=year), 
								   index=False,
								   sep=",")
			return_dict[year] = census_data #add data extract to return dictionary

		if self.config_data["DEBUG"]:
			print()
			print("field names to extract")
			print(field_names_2002)
			print(field_names_2003)
			print(field_names_2022)
			print()
			print("field numbers from file schema (not 0 adjusted")
			print(field_nums_one_idx_2002)			
			print(field_nums_one_idx_2003)
			print(field_nums_one_idx_2022)

		return return_dict


	def get_census_omb_delineation_file(self, years=[], sep=None, convert=True):

		"""

		PARAMETERS:
		years: list of years for which to retrieve data files.
			Note: not all years have a distinct delineation file
		convert: if true, convert the file from XLS to CSV and trim unusable rows
		"""
		if len(years) < 1:
			print("no years passed in list, using config data for ALL YEARS")
			years = self.config_data["ALL_YEARS"]
		
		if sep is None:
			sep = self.config_data["SEP"]

		if sep == "|":
			file_ending = "txt"
		else:
			file_ending = "csv"

		for year in years:
			if int(year) < 2003:
				print()
				print("not yet configured for OMB delineation parsing prior to 2003")
				return

			local_file_name = "excel_delineation_{year}.xlsx".format(year=year) #set filename for writing to disk

			print()
			print("getting Census/OMB delineation data for {year}".format(year=year))

			#request data from site
			print("calling: \n {url}".format(url=self.config_data["msa_md_delineation"]["omb_{year}".format(year=str(year))]))
			delin_resp = requests.get(self.config_data["msa_md_delineation"]["omb_{year}".format(year=str(year))])

			print("saving data for {year} as {name}".format(year=year, name=local_file_name))

			print("Path: ",self.config_data["CENSUS_PATH"] + local_file_name)
			with open(self.config_data["CENSUS_PATH"] + local_file_name, "wb") as infile:
				infile.write(delin_resp.content)


			if convert:
				#configure Excel load based on OMB delineation year file
				sheet_name = self.config_data["omb_sheet_names"]["omb_{year}".format(year=year)]
				skip_rows = self.config_data["omb_skip_rows"]["omb_{year}".format(year=year)]

			
				#read Excel file
				print("local_file_name: ", local_file_name)
				data_xls = pd.read_excel(self.config_data["CENSUS_PATH"] + local_file_name, sheet_name, index_col=None,engine ="xlrd") #, engine = "xlrd" , openpyxl
				#save sheet as CSV
				data_xls.to_csv(self.config_data["CENSUS_PATH"] + "full_omb_delin_{year}.{end}".format(year=year, end=file_ending), 
								encoding='utf-8', 
								index=False,
								sep=sep)

				#load CSV to dataframe to extract needed columns
				census_df = pd.read_csv(self.config_data["CENSUS_PATH"] + "full_omb_delin_{year}.{end}".format(year=year, end=file_ending), 
										skiprows=skip_rows, 
										dtype=object, 
										sep=sep)


				if int(year) >= 2013:
					#create 5 digit county FIPS
					census_df["full_county_fips"] = census_df.apply(lambda x: x["FIPS State Code"] + x["FIPS County Code"], axis=1)

					#List3_2008
				else:
					#rename county FIPS column to match other Census OMB files
					census_df.rename(columns={"FIPS":"full_county_fips"}, inplace=True)

				#get single name for each Metropolitan or Micropolitan statistical area using:
				#MD name first and CBSA title second in precedence for determining MSA/MD name
				#CSA references were removed as they are above the MSA level used for HMDA work
				#Metropolitan Division Title, CBSA Title
				census_df["MSA/MD Name"] = census_df.apply(lambda x: x["CBSA Title"] if pd.notnull(x["CBSA Title"]) else "", axis=1)
				census_df["MSA/MD Name"] = census_df.apply(lambda x: str(x["Metropolitan Division Title"]) \
					if (pd.notnull(x["Metropolitan Division Title"]) and str(x["Metropolitan Division Title"]).strip() != "") 
					else x["MSA/MD Name"], axis=1)


				#Remove unneeded columns
				census_df = census_df[["CBSA Code", "full_county_fips", "MSA/MD Name"]]
				#write census omb names to disk
				census_df.to_csv(self.config_data["CENSUS_PATH"] + "msa_md_names_{year}.txt".format(year=year), 
								 index=False,
								 sep="|")
				census_df.to_csv(self.config_data["CENSUS_PATH"] + "msa_md_names_{year}.csv".format(year=year), 
								 index=False,
								 sep=",")

	def combine_omb_ffiec(self, years=[], sep=None, both=True):
		
		"""
		
		PARAMETERS:
		years: list of years for which to combine files

		"""
		if len(years) < 1:
			years = self.config_data["ALL_YEARS"]
			print("no year data passed in list, using config data for ALL YEARS")

		if sep is None:
			sep = self.config_data["SEP"]

		if sep == "|":
			file_ending = "txt"
		else:
			file_ending = "csv"
		

		return_dict = {} #year keyed dictionary to return combined Census data files

		for year in years:
			if int(year) < 2003:
				print()
				print("not yet configured for OMB delineation parsing prior to 2003")
				continue
			print()
			print("Combining FFIEC Census and OMB data for {year}".format(year=year))
			print(self.config_data["OUT_PATH"] + "census_data_extract_{year}.{end}".format(year=year, end=file_ending))
			
   			#load FFIEC Census File Cut
			ffiec_census_df = pd.read_csv(self.config_data["OUT_PATH"] + "census_data_extract_{year}.{end}".format(year=year, end=file_ending), 
										  dtype=object,
										  sep=sep,
										  keep_default_na=False)

			#load MSA/MD name file
			msa_md_name_df = pd.read_csv(self.config_data["CENSUS_PATH"] + "msa_md_names_{year}.{end}".format(year=year, end=file_ending), 
										 dtype=object,
										 sep=sep,
										 keep_default_na=False)
			
			#Create 5 digit county FIPS in FFIEC file
			ffiec_census_df["full_county_fips"] = ffiec_census_df.apply(lambda x: str(x.State) + str(x.County), 
																		axis=1)
			print(ffiec_census_df.head())
			if self.config_data["DEBUG"]:
				print()
				print(ffiec_census_df.columns)
				print(msa_md_name_df.columns)

			#Merge FFIEC Census data cut with MSA/MD name file to add MSA/MD names
			ffiec_census_df = ffiec_census_df.merge(msa_md_name_df, 
													how="left", 
													on="full_county_fips")

			#set columns for output
			ffiec_census_df = ffiec_census_df[self.config_data["OUT_COLUMNS"].keys()]

			#Write file to disk
			print("Path: ",self.config_data["OUT_PATH"] + "ffiec_census_msamd_names_{year}.{end}".format(year=year, end=file_ending))
			print()
   
			# if 'MSA/MD' == "99999", set 'MSA/MD Name' to empty string
			ffiec_census_df.loc[(ffiec_census_df['MSA/MD'] == "99999"), 'MSA/MD Name'] = ""  # added 2/8/24
			ffiec_census_df.loc[(ffiec_census_df['Median Age'] == "2002"), 'Median Age'] = "6"  # added 2/8/24   

			ffiec_census_df.to_csv(self.config_data["OUT_PATH"] + "ffiec_census_msamd_names_{year}.{end}".format(year=year, end=file_ending), 
								   index=False, 
								   sep=sep)

			#map FIPS State Code to letter code in column "State" for MSA/MD description file	
			ffiec_census_df["State"] = ffiec_census_df["State"].map(self.config_data["state_codes_rev"])

			ffiec_census_df["MSA/MD Name"] = ffiec_census_df["MSA/MD Name"].apply(lambda x: str(x).strip())

			msa_md_desc_df = ffiec_census_df[self.config_data["msa_name_cols"]][(ffiec_census_df["MSA/MD"]!="99999")&
																				(ffiec_census_df["MSA/MD Name"]!="")&
																				(ffiec_census_df["MSA/MD Name"]!="nan")].copy()
   

			#remove duplicates. These are the records for county and tract that need to be removed from the MSA/MD list
			msa_md_desc_df.columns = self.config_data["msa_md_desc_out_cols"]
			msa_md_desc_df.drop_duplicates(inplace=True)
			msa_md_desc_df.to_csv(self.config_data["OUT_PATH"] + "msa_md_description_{year}.{end}".format(year=year, end=file_ending), 
								   index=False, 
								   sep=sep)

			if both:
				msa_md_desc_df.to_csv(self.config_data["OUT_PATH"] + "msa_md_description_{year}.csv".format(year=year), 
									   index=False, 
									   sep=",")

			return_dict[year] = ffiec_census_df #add combined census data to return dict for handoff

			if self.config_data["DEBUG"]:
				print(ffiec_census_df.head())
				print()
				print(msa_md_name_df.head())
				print()

		return return_dict

	def load_to_db(self, schema="census", years=["2019"], sep=None, encoding="latin1"):
		"""
		"""

		if sep is None:
			sep = self.config_data["SEP"]

		for year in years:
			with open(self.config_data["census_load_sql"]) as in_sql:
				census_load_sql = in_sql.read()

			sql_field_base = "{field} {type}"
			sql_def_lines = []

			#format SQL column names and data types
			for key, value in self.config_data["OUT_COLUMNS"].items():

				field_name = key.lower().replace("/", "_").replace(" ", "_").replace("%","pct")
				new_line = sql_field_base.format(field=field_name, type=value)
				sql_def_lines.append(new_line)

			sql_def_lines = ",\n".join(sql_def_lines)

			#set table and data reference for year
			table = "ffiec_census_{year}".format(year=year)

			data_file = self.config_data["OUT_PATH"] + "ffiec_census_msamd_names_{year}.csv".format(year=year)
			data_file = os.path.abspath(data_file)

			if self.config_data["DEBUG"]:
				print(census_load_sql.format(fields_definition=sql_def_lines, schema=schema, table=table, 
				data_path_and_filename=data_file ,encoding=encoding, sep=sep))


			conn, cur = self.connect(self.db_params)
			cur.execute(census_load_sql.format(fields_definition=sql_def_lines, schema=schema, table=table, 
				data_path_and_filename=data_file ,encoding=encoding, sep=sep))

			conn.close()

			


