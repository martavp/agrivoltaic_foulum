[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Agrivoltaic systems Foulum


This repository includes scripts to process, validate, and analyze the data collected at the Agrivoltaics demonstration site in Foulumgaard which is part of the [Hyperfarm project](https://hyperfarm.eu/).

The script 'clean_data.py' retrieves raw data files from the weather stations and the inverters datalogger, creates a data file named 'clean_data.csv' and stores it in the folder 'resources'. 

Other scripts such as 'radiation_comparison.py' or 'efficiency_analysis.py' use the common data file 'clean_data.csv' to implement different analyses. 
