@echo off

rem Intermediate files are deleted

del in.dat
del out.dat

rem First the model is run under calibration conditions

copy in1.dat in.dat > nul
twoline > nul
copy out.dat out1.dat > nul

rem Next the model is run under predictive conditions

copy in2.dat in.dat > nul
twoline > nul
copy out.dat out2.dat > nul

