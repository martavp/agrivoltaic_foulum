[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Agrivoltaic systems Foulum


This repository includes scripts to process, validate, and analyze the data collected at the Agrivoltaic demonstration site in Foulumgaard which is part of the [Hyperfarm project](https://hyperfarm.eu/).

The Agrivoltaic demonstration system is described in the pre-print ["Vertical Agrivoltaics in a Temperate Climate: Exploring Technical, Agricultural, Meteorological, and Social Dimensions"](https://www.researchsquare.com/article/rs-5358908/v1)

The script 'clean_data.py' retrieves raw data files from the weather stations and the inverters datalogger, creates a data file named 'clean_data.csv' and stores it in the folder 'resources'. 

The 'clean_data.csv' is also stored in [zenodo](https://zenodo.org/records/14017975)

Other scripts such as 'radiation_comparison.py' or 'efficiency_analysis.py' use the common data file 'clean_data.csv' to implement different analyses. 
