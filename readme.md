## HMDA Census Geographic and Demographic Data 

## Table of Contents
- [Repository Purpose and Scope](https://github.com/cfpb/hmda-census#repository-purpose)
- [Requirements and Setup](https://github.com/cfpb/hmda-census#requirements-and-setup-and-running-the-code)
- [Sources of Data](https://github.com/cfpb/hmda-census#sources-of-data)
- [Uses of Data](https://github.com/cfpb/hmda-census#uses-of-data)
- [HMDA Platform Census Files](https://github.com/cfpb/hmda-census#hmda-platform-census-files)

## Repository Purpose
- Provide an ETL for geographic and Census data used by the HMDA Platform
- Check to ensure the accuracy of Census data in the HMDA Platform


## Requirements and Setup and Running the Code

**Install Requirements**
The code is built in Python3.X which can be found at the link below. The following packages are also required and can be installed using the commands listed.
- [Python 3.6 or greater](https://www.python.org/downloads/)
- set up a virtual environment if desired: `virtualenv venv`
	- turn on virtual environment: `source venv/bin/activate`
	- turn off virtual environment: `deactivate`
- install requirements packages: `pip install -r requirements.txt`
- *Note: to load data files to a database, you must have one installed locally. This code has been tested with [PostgreSQL](https://www.postgresql.org/download/)*

### Creating Yearly Census File for the HMDA Platform

1. Update the `python/census_config.yaml` to include the relevant years census file in [msa_md_delinations section](https://github.com/cfpb/hmda-census/blob/master/python/census_config.yaml#L69).
1. Update the `year` variable in the `python/create_ffiec_census_file.py` file to be the year for which you want to generate the platform census file.
1. Run the `python/create_ffiec_census_file.py` file.
1. The file will be created in `output/` as `ffiec_census_msamd_names_<year>.txt`
1. Move the file in the HMDA-Platform repo as `common/src/main/resources/ffiec_census_<year>.txt`

### Working With the Scripts
[Configuration](https://github.com/cfpb/hmda-census/blob/master/python/census_config.yaml): Determines which years of data to use, allows selection of fields in both data files, and contains data specifications and URLs relevant.

The configuration is used in the [census_functions.py](https://github.com/cfpb/hmda-census/blob/master/python/census_functions.py) class. [The test.py](https://github.com/cfpb/hmda-census/blob/master/python/test.py) script contains examples that use the class to download, cut, merge, and load to database the resulting census data.

### Current issues:
- MSA to tract mapping verification needs to be updated for the new codebase
- MSA delineation files pre-2000 are in a different format that is yet to be parsed


## Sources of Data
The HMDA Platform uses data the combines elements of the FFIEC Census Flat File and the OMB MSA delineation files. The FFIEC Census file contains over 1,000 data elements, of which the HMDA Platform uses a small subset. The OMB MSA bulletines are primarily used for names.

The Office of Management and Budget produces MSA data. Updates can include changes to an MSA's boundaries or creation of new MSAs. These data have no regular publication cycle. HMDA Operations uses the MSA definitions in effect on 12/31 of the year preceding collection, this aligns with other Regulation C criteria. 
- [OMB Publications on MSA](https://www.census.gov/programs-surveys/metro-micro/about/omb-bulletins.html)
- [OMB Delineation Bulletins](https://www.census.gov/programs-surveys/metro-micro/about/omb-bulletins.html)   
- [OMB Delineation Definition 2010](https://www.govinfo.gov/content/pkg/FR-2010-06-28/pdf/2010-15605.pdf)

The Census delineation files are used to map names to MSA/MD geographies.
- [Census Publications on MSA](https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html)

The FFIEC produces an annual Census Flat File containing demographic data and a mapping of MSA data to Census tract. 
- [FFIEC Census Flat Files by Year](https://www.ffiec.gov/censusapp.htm) 
	- *Note: the Census Flat File is indexed starting at 1*

**Additional Census data is available, but not used in this project:**
The Census reference files contain MSA/MD, micropolitan statistical area definitions, names, and maps to county and tract codes.
- [Census API](https://www.census.gov/data/developers/data-sets.html)   
- [County FIPS and name list](https://www.census.gov/geographies/reference-files/2018/demo/popest/2018-fips.html)


## Uses of Data
The HMDA Platform uses data during data submission and publication. 

During submission Census data are used to verify the relationship between reported geographic identifiers for loans and applications.  

In publication the Census demographic and geographic data are used to add demographic information to LAR datasets. 
The variables added include:
- Total Population   
- Minority Population Percentage   
- FFIEC Median Family Income  
- Tract to MSA/MD Income Percentage  
- Number of Owner Occupied Units  
- Number of 1 to 4 Family Units   
- MSA (new in 2018, was previously submitted by FIs)

Census geographic data are used to map MSAs to county and tract areas in the Aggregate and Disclosure reports and for geographic lookup features in HMDA data tools web interfaces. 

[See here for the HMDA-Platform](https://github.com/cfpb/hmda-platform/blob/745f50bafd6a6dc23641b0275e00aea42ea503a4/common/src/main/scala/hmda/census/records/CensusRecords.scala#L56) logic mapping Census to LAR data.

**HMDA Publication Products**
- [Aggregate Reports](https://ffiec.cfpb.gov/data-publication/aggregate-reports): contain MSA level data on application and lending activity for all institutions reporting HMDA data.
- [Disclosure Reports](https://ffiec.cfpb.gov/data-publication/disclosure-reports): contain MSA level data on application and lending activity for a single institution.
- [LAR snapshot publication](https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset): contains the entire dataset of loans and applications submitted in accordance with Regulation C.

## HMDA Platform Census Files
- [Base resource folder](https://github.com/cfpb/hmda-platform/tree/master/common/src/main/resources)
- [Raw v2 2018 MSA data](https://github.com/cfpb/hmda-platform/tree/master/common/src/main/resources/census_2018_MSAMD_name.txt)






