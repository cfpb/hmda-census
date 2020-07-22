### This is a code utility library that contains logic to download and combine the FFIEC Census flat file and
# Census/OMB delineation file for use with HMDA data.

import os
from os import path
from os import listdir
from os.path import isfile, join
import shutil

import pandas as pd
import requests
import yaml
import zipfile


#handle in config load



class CensusTools(object):
	"""
	"""

	def __init__(self, config_file="census_config.yaml"):
		"""
		Sets up the configuration for file paths and download URLs
		"""

		with open(config_file, "r") as in_config:
			self.config_data = yaml.safe_load(in_config)
		
		print()
		for path in self.config_data["FOLDER_PATHS"]:
			print("creating {folder}".format(folder=self.config_data[path]))
			if not os.path.exists(self.config_data[path]):
				os.makedirs(self.config_data[path])



	def get_ffiec_census_file(self, years=[2019], unzip=True, move=True):
		"""
		Retrieves Census flat file data from the FFIEC website.
		Each file is 1 year of data intended to be used with HMDA data.
		Files are available from 1990-2019. New files are typically published in the fall.

		PARAMETERS:
		years: a list of which years of data to download
		unzip, if true: unzips all zip files in the DATA_PATH location
		move, if true: moves all files in the from sub folders to the main data folder
		"""

		base_url = self.config_data["FFIEC_CENSUS_BASE_URL"]
		for year in years:
			local_file_name = "ffiec_census_{year}.zip".format(year=year)
			print()
			print("getting data for {year}".format(year=year))

			if year >= 2008:
				census_resp = requests.get(base_url + "CENSUS{year}.zip".format(year=year))
			else:
				census_resp = requests.get(base_url + "Zip%20Files/{year}.zip".format(year=year))

			print("saving data for {year} as {name}".format(year=year, name=local_file_name))

			with open(self.config_data["CENSUS_PATH"] + local_file_name, "wb") as infile:
				infile.write(census_resp.content)


		if unzip:

			##get all files in data dir with .zip extension
			print()
			print("Unzipping files in {folder}".format(folder=self.config_data["CENSUS_PATH"]))
			census_files = [f for f in listdir(self.config_data["CENSUS_PATH"]) if isfile(join(self.config_data["CENSUS_PATH"], f))]
			census_files = [f for f in census_files if f[-4:]==".zip"]
			
			#unzip all census files
			for file in census_files:
				with zipfile.ZipFile(self.config_data["CENSUS_PATH"] + file, 'r') as zip_ref:
					zip_ref.extractall(self.config_data["CENSUS_PATH"])

		if move:

			#move all census files from their sub folders to the main folder
			#delete empty folder
			print()
			print("Moving all FFIEC Census files to {folder} and removing old sub folders".format(folder=self.config_data["CENSUS_PATH"]))
			directories = [f for f in listdir(self.config_data["CENSUS_PATH"]) if not isfile(join(self.config_data["CENSUS_PATH"], f))]
			for folder in directories:
				files = [f for f in listdir(self.config_data["CENSUS_PATH"] + folder) if isfile(join(self.config_data["CENSUS_PATH"] + folder, f))]
				for file in files:
					print(file)
					shutil.move(self.config_data["CENSUS_PATH"] + folder + "/" + file, self.config_data["CENSUS_PATH"])
					os.rmdir(self.config_data["CENSUS_PATH"] + folder)


	def get_census_fields(self, census_file="census2019.csv", sep=",", save_csv=True):

		"""
		Extracts the enumerated fields from an FFIEC Census data CSV
		Returns a pandas dataframe with the selected fields

		Notes: 
		- not all FFIEC census data is in CSV format and data contents may change between years
		 
		
		
		PARAMETERS:
		field_dict: a name, field number dictionary. The keys will be used as column names, 
					the values will be used to select fields from the FFIEC Census file.
			- The data file documentation is not zero-indexed.
			- Pass in the index in the documentation. Do not adjust for zero-indexing, 
				that is handled in this code.

		census_file: the name of the census file used for the extract
		data_path: the path to the census file to be used for extract
		save_csv: write the extract to a CSV file
		sep: separater character to use when writing file extract
		"""

		data_path = self.config_data["CENSUS_PATH"] #set path to data files
		field_dict = self.config_data["extract_fields"] #fields to extract from file

		field_names = list(field_dict.keys())
		field_nums = list(field_dict.values())

		field_nums = [num - 1 for num in field_nums] #adjust for non-0 indexing in FFIEC file dictionary

		if self.config_data["DEBUG"]:
			print()
			print("field names to extract")
			print(field_names)
			print()
			print("field numbers to extract")
			print(field_nums)

		#data are loaded as objects to preserve integrity of geographic identifiers with leading 0-s
		census_data = pd.read_csv(data_path+census_file, usecols=field_nums, names=field_names, header=None, dtype=object)

		if save_csv:
			census_data.to_csv(self.config_data["OUT_PATH"] + census_file[:-4] + "_extract.csv", sep=sep, index=False)

		return census_data


	def get_census_omb_delineation_file(self, year="2019"):

		"""
		"""
		
		local_file_name = "delineation_{year}.xls".format(year=year) #set filename for writing to disk

		print()
		print("getting Census/OMB delineation data for {year}".format(year=year))

		#request data from site
		print("calling: \n {url}".format(url=self.config_data["census_{year}".format(year=year)]["msa_md_name_file"]))
		delin_resp = requests.get(self.config_data["census_{year}".format(year=year)]["msa_md_name_file"])

		print("saving data for {year} as {name}".format(year=year, name=local_file_name))

		with open(self.config_data["CENSUS_PATH"] + local_file_name, "wb") as infile:
			infile.write(delin_resp.content)


