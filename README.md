## SWMM2PEST
SWMM2PEST is a scientific software that used for calibration.

## Purpose & Motivate
Due to the lack of automated parameter mapping and data conversion, engineers must manually prepare input files to execute Storm Water Management Model (SWMM) and Parameter ESTimation (PEST).
Most of the time and cost are waste when transferring data back and forth and reading files between two software.
Regarding this situation, SWMM2PEST is developed to automate the calibration process of SWMM by integrating the essential modules of PEST.

## Introduction
SWMM2PEST 2.0 is a new version of SWMM2PEST developed in Python and PyQt and released in public domain. It fixes lots of bugs, adds new features, rebuilds the framework and UI, and integrates SWMM 5.1.10 and PEST 14.2.

## References
SWMM: https://www.epa.gov/water-research/storm-water-management-model-swmm

PEST: http://www.pesthomepage.org/

## How to use
A. Input File Selection
1. Provide SWMM input file (.inp). 
2. Click "Start".

B. Parameters Selection
1. Click on the Subcatchment or LID_Controls to display the parameter and their values. 
2. Select the parameters to be calibrated. Enter the lower and upper limits in the boxes below the parameters to be calibrated and check the "Calibration" box.
3. Click "Run".

C. Calibration 
1. Provide the file containing observed or field values for the selected output parameter. The field values’ time stamp must begin with start time of the output file. 
2. Provide the type of observation data.
3. Click "Run Calibration".

## Caveats
1. Do not include the parameter with a value of 0 to do the calibration.
2. The folder path of the input file cannot contain spaces.
3. Same parameters in SWMM input file and observation file must be in the same unit.
4. Make sure the numbers of observation data is equal to that of SWMM output data. (If the time interval of observation data is every 5 minutes, then rename 'swmm5_110Biocell.exe' (located in swmm folder) to 'swmm5110.exe'.)

## Project status
SWMM2PEST 2.0: June 2018

SWMM2PEST: August 2017
## Contributing
Everyone is welcome to contribute to this project.