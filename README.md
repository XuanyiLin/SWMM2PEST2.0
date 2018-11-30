## SWMM2PEST
SWMM2PEST is a scientific software for calibration.

## Purpose & Motivate
Due to the lack of automated parameter mapping and data conversion, engineers must manually prepare input files to execute Storm Water Management Model (SWMM) and Parameter ESTimation (PEST).
Most of the time and cost are waste when transferring data back and forth and reading files between two software.
Regarding this situation, SWMM2PEST is developed to automate the calibration process of SWMM by integrating the essential modules of PEST.

## Introduction
[SWMM2PEST 2.0](https://github.com/XuanyiLin/SWMM2PEST2.0) is a new version of [SWMM2PEST](https://github.com/SurajKamble/SWMM2PEST) developed in Python 3.5.4 and PyQt 5 and released in public domain. It fixed lots of bugs, added new features, rebuilt the framework and UI, and integrated SWMM 5.1.10 and PEST 14.2.

## References
SWMM: https://www.epa.gov/water-research/storm-water-management-model-swmm

PEST: http://www.pesthomepage.org/

## How to run
A. Run in Pycharm
1. Run MainFrame.py.
B. Run as Windows application
1. Download [SWMM2PEST](https://github.com/XuanyiLin/SWMM2PEST2.0/releases/download/V2.1/SWMM2PEST.V2.1.zip).
2. Unzip the file.
3. Run SWMM2PEST.exe.

## How to use
A. Input File Selection
1. Provide SWMM input file (.inp). 
2. Click "Start".
<br/><img height="280" src="https://github.com/XuanyiLin/SWMM2PEST2.0/blob/master/Images/1.png"/><br/>

B. Parameters Selection
1. Click on the Subcatchment or LID_Controls to display the parameter and their values. 
2. Select the parameters to be calibrated. Enter the lower and upper limits in the boxes below the parameters to be calibrated and check the "Calibrate" box.
3. Click "Run".
<br/><img height="350" src="https://github.com/XuanyiLin/SWMM2PEST2.0/blob/master/Images/2.png"/><br/>

C. Calibration 
1. Provide the file containing observed or field values for the selected output parameter. The field values’ time stamp must begin with start time of the output file. 
2. Provide the type of observation data.
3. Click "Run Calibration".
<br/><img height="250" src="https://github.com/XuanyiLin/SWMM2PEST2.0/blob/master/Images/3.png"/><br/>
## Demo
<br/><img height="350" src="https://github.com/XuanyiLin/SWMM2PEST2.0/blob/master/Images/Demo.gif"/><br/>

## Caveats
1. Do not include the parameter with a value of 0 to do the calibration. 0 can be in the calibration range.
2. The folder path of the input file cannot contain spaces.
3. Same parameters in SWMM input file and observation file must be in the same unit.
4. Make sure the observation data format is correct. each line in the observation data file should contain date (mm/dd/yyyy), time (hh:mm:ss) and value, e.g. 01/30/2018 06:59:00 0.0001.

## Project status
SWMM2PEST 2.0: June 2018

[SWMM2PEST](https://github.com/SurajKamble/SWMM2PEST): August 2017
## Contributing
Everyone is welcome to contribute to this project.

