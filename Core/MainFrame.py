# MainFrame.py
#
# Project: SWMM2PEST
# Version: 2.0
# Date:   06/04/2018 (version 2.0; author: X.Lin)
#         07/16/2017 (version 1.0; author: S.Kamble)
#
# This is the main frame of SWMM2PEST.It contains main classes and functions.
#

import sys
import os
from numpy import linspace
import spotpy
import pyqtgraph as pg
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, qApp
from Core.ReadSections import ReadSections
from Core.WriteSections import write_sections
from Core.UpdateParameter import UpdateParameter
from Core.ObservationData import ObservationData
from Py_UI_Files import NewFileUI,MainFrameUI, HelpWindowUI, PestCalibrationUI
from Py_UI_Files.FormUI import *


class PestThread(QThread): # Separate thread that calls pest and runs it in the background

    def __init__(self, pst_fname):
        QThread.__init__(self)
        self.pst_fname = pst_fname

    def __del__(self):
        self.wait()

    def run_pest_command(self, pst_fname):
        print("In run pest thread")
        cmd_line = "pest14\\pest.exe " + pst_fname  # Set Command line
        print(cmd_line)
        os.system(cmd_line)

    def run(self):
        self.run_pest_command(self.pst_fname)

class SwmmThread(QThread): # Separate thread that calls swmm and runs it in the background

    def __init__(self, inp_fname):
        QThread.__init__(self)
        self.inp_fname = inp_fname

    def __del__(self):
        self.wait()

    def run_swmm_command(self, inp_fname):
        print("In run swmm thread")
        cmd_line = "swmm\\swmm5.exe " + inp_fname +" temp.rpt" # Set Command line
        print(cmd_line)
        os.system(cmd_line)

    def run(self):
        self.run_swmm_command(self.inp_fname)



class MainFrame(QMainWindow, NewFileUI.Ui_MainWindow): # This class contains all the functionalities required for the UI

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.btnBrowse.clicked.connect(self.openFileDialog) # Connect SWMM input file
        # self.outputBrowse.clicked.connect(self.outputFileDialog) # Connect SWMM output file
        self.startButton.clicked.connect(self.startMainFrame) # Connect Main Frame
        self.mainFrame = None
        self.window = None
        self.subcatchments_data = []
        self.current_sub = None
        self.inp_fname=''
        self.out_fname=''
        # self.lineEdit_inputFile.setText('C:/2009Q1/groof09Q1.inp')

        self.observation_fname=''

    def openFileDialog(self): # Select SWMM Input file
        fname = QFileDialog.getOpenFileName(self, 'Select input file')
        if str(fname[0][-4:]) == ".inp":
            self.inp_fname = fname[0]
            self.lineEdit_inputFile.setText(self.inp_fname)

    def openObservationFile(self):  # Select Observation data file
        observation_fname = QFileDialog.getOpenFileName(self, 'Select Observation File')
        if str(observation_fname[0][-4:]) == ".txt":
            self.observation_fname = observation_fname[0]
            self.pestCalibrationWindow.lineEdit_observationFile.setText(self.observation_fname)

    def startMainFrame(self): # Go to Main Frame
        self.inp_fname=self.lineEdit_inputFile.text()
        if self.inp_fname!='':
            update_out_fname=UpdateParameter()
            self.out_fname=update_out_fname.updateReportFile(self.inp_fname)
            self.loadMainFrame()


    def loadHelpWindow(self): # Display Help Window
        self.helpWindow = LoadHelpWindow() # Class LoadHelpWindow

    def loadPestCalibrationWindow(self): #Display Pest Calibration Window
        # save Sub and LID data before Calibration
        # save LID data (lower limit, upper limit,Fixed, None)
        self.saveLIDParametersValue()
        # save Current Subcatchment data (lower limit, upper limit,Fixed, None)
        self.saveSubParametersValue()
        # After save all parameters, write tpl file
        write_sections_data = write_sections(self.subcatchments_data, self.lid_controls_data)  # Create and Write tpl file
        write_sections_data.write_template_data(self.subcatchments_data)
        
        self.pestCalibrationWindow= LoadPestCalibrationWindow() # Class LoadPestCalibrationWindow
        self.pestCalibrationWindow.observationBrowse.clicked.connect(self.openObservationFile)
        self.pestCalibrationWindow.runCalibrationButton.clicked.connect(self.readOutputFile)

    def loadNewFile(self):
        self.show() #Display NewFile

    def loadMainFrame(self):# Loads second window after getting SWMM input file and output file
        self.mainFrame = LoadMainFrame() # Show Main Frame # Class LoadMainFrame
        self.hide()  # Hide NewFile

        self.mainFrame.actionExit.triggered.connect(qApp.quit) # Connect Exit Actions
        self.mainFrame.actionGuide.triggered.connect(self.loadHelpWindow) # Connect Help Actions
        self.mainFrame.actionRun_Pest_Calibration.triggered.connect(self.loadPestCalibrationWindow)
        # self.mainFrame.actionTest.triggered.connect(self.saveLIDParametersValue)
        self.mainFrame.actionNew.triggered.connect(self.loadNewFile)

        read_file = ReadSections() # Class ReadSections Instantiation

        all_data = read_file.read_subcatchment_data(self.inp_fname) # Read data from SWMM input file

        self.subcatchments_data = all_data[0] # Get subcatchments
        subcatchments_listItems = []

        for i in range(len(self.subcatchments_data)):
            subcatchments_listItems.append(QtWidgets.QListWidgetItem(self.subcatchments_data[i].name))

        for i in range(len(subcatchments_listItems)):
            self.mainFrame.listSubcatchments.addItem(subcatchments_listItems[i]) # Display subcatchment name in Main Frame

        self.mainFrame.listSubcatchments.itemClicked[QtWidgets.QListWidgetItem].connect(self.clickedSlotSub) # Connect subcatchment Action

        self.lid_controls_data = all_data[1] # Get Lid Controls
        # Initiate LID UI Forms for reading and saving (lower limit,upper limit, Fixed info, None info)
        self.InitiateLIDUIFrom()
        # Initiate Current Subcatchment UI Forms for reading and saving (lower limit,upper limit, Fixed info, None info)
        self.InitiateSubUIForm()

        self.loadLIDControlsUI() # Display LID Controls in UI
        self.run_swmm()

    def readOutputFile(self):

        observationType=self.pestCalibrationWindow.comboBox_ODT.currentText()
        print(observationType)
        if observationType=='Total Evaporation(in/hr)':
            index_needed=2
        elif observationType=='Surface Infiltration(in/hr)':
            index_needed=3
        elif observationType=='Pavement Perc(in/hr)':
            index_needed=4
        elif observationType == 'Soil Perc(in/hr)':
            index_needed =5
        elif observationType=='Storage Exfil(in/hr)':
            index_needed=6
        elif observationType=='Surface Runoff(in/hr)':
            index_needed=7
        elif observationType=='Drain Outflow(in/hr)':
            index_needed=8
        elif observationType=='Surface Level(inches)':
            index_needed=9
        elif observationType == 'Pavement Level(inches)':
            index_needed =10
        elif observationType=='Soil Moisture content':
            index_needed=11
        elif observationType=='Storage Level (inches)':
            index_needed=12

        index_needed += 1
        self.observationType=observationType #record the observationType
        with open(self.out_fname, 'r') as out_file:
            lines = out_file.readlines()

        for line_num in range(len(lines)):
            if lines[line_num].startswith("-------"):
                start_line = line_num + 1
        split_lines = lines[start_line].split(" ")
        self.writeInsFile(lines, start_line, index_needed - 1)

    def writeInsFile(self, lines, start_line, index):    # Write Instruction file based on the output parameter selected

        ins_lines = "pif #\n#-------#\n"
        self.ins_fname = self.out_fname[:-3] + "ins"
        print("In writeInsFile")
        obs_name = ""

        if index == 2:
            obs_name = "tevap"
            location_start = 44
            location_end = 51
        if index == 3:
            obs_name = "sinfil"
            location_start = 55
            location_end = 61
        if index == 4:
            obs_name = "pperc"
            location_start = 65
            location_end = 71
        if index == 5:
            obs_name = "sperc"
            location_start = 75
            location_end = 81
        if index == 6:
            obs_name = "stexfil"
            location_start = 85
            location_end = 91
        if index == 7:
            obs_name = "srunoff"
            location_start = 94
            location_end = 100
        if index == 8:
            obs_name = "dflow"
            location_start = 104
            location_end = 110
        if index == 9:
            obs_name = "sulevel"
            location_start = 114
            location_end = 120
        if index == 10:
            obs_name = "plevel"
            location_start = 124
            location_end = 130
        if index == 11:
            obs_name = "smoist"
            location_start = 134
            location_end = 140
        if index == 12:
            obs_name = "stlevel"
            location_start = 144
            location_end = 149

        print("After Switch Case")

        line_num = start_line

        self.out_lines = lines[start_line:]

        self.output_location_start = location_start
        self.output_location_end = location_end

        # Output values before calibration:

        self.output_values_before_calibration = []

        for line in self.out_lines:
            self.output_values_before_calibration.append(line[location_start:(location_end+1)])

        # print(self.output_values_before_calibration)

        temp = []

        for i in self.output_values_before_calibration:
            try:
                print(i)
                temp.append(float(i.strip()))
            except Exception:
                print('\nERROR in mainFrame.py_temp.append(float(i.strip()))\n')

        print("out of for loop")
        self.output_values_before_calibration = temp
        # print(self.output_values_before_calibration)
        self.obs_name = obs_name

        while line_num < len(lines):
            # date (SWMM output file)
            dstamp = lines[line_num].split()[0]
            dstamp = dstamp.split("/")[0] + dstamp.split("/")[1]+ dstamp.split("/")[2]

            # time (SWMM output file)
            tstamp = lines[line_num].split()[1]
            tstamp = tstamp.split(":")[0] + tstamp.split(":")[1]

            # print(dstamp + tstamp)
            # obs_name += tstamp

            line = "l1  [" + obs_name + dstamp + tstamp + "]" + str(location_start) + ":" + str(location_end) + "\n"

            ins_lines += line

            line_num += 1
        # print(ins_lines)

        with open(self.ins_fname, 'w') as f:
            f.write(ins_lines)

        self.createControlFile()

    def createControlFile(self):     # Create control file(.pst) based on all the data provided

        # get observation file name
        obs_fname=self.observation_fname

        '''
        Read observation file
        '''

        observationData=ObservationData()
        observationData.readObsFile(obs_fname)
        self.measured_data = observationData.getAllValue()

        '''
        Add control data
        '''

        '''
        pcf	
        * control data
        restart	estimation
           15   580    1     0     1
            1     1 single point 1 0 0
          5.0   2.0   0.3    0.01  10
          5.0   5.0   0.001
          0.1
           30  0.01     4     3  0.01     3
            1     1     1
        
        '''

        '''
        * control data
        RSTFLE PESTMODE
        NPAR NOBS NPARGP NPRIOR NOBSGP [MAXCOMPDIM] [DERZEROLIM]
        NTPLFLE NINSFLE PRECIS DPOINT [NUMCOM JACFILE MESSFILE] [OBSREREF]
        RLAMBDA1 RLAMFAC PHIRATSUF PHIREDLAM NUMLAM [JACUPDATE] [LAMFORGIVE] [DERFORGIVE]
        RELPARMAX FACPARMAX FACORIG [IBOUNDSTICK UPVECBEND] [ABSPARMAX]
        PHIREDSWH [NOPTSWITCH] [SPLITSWH] [DOAUI] [DOSENREUSE] [BOUNDSCALE]
        NOPTMAX PHIREDSTP NPHISTP NPHINORED RELPARSTP NRELPAR [PHISTOPTHRESH] [LASTRUN] [PHIABANDON]
        ICOV ICOR IEIG [IRES] [JCOSAVE] [VERBOSEREC] [JCOSAVEITN] [REISAVEITN] [PARSAVEITN] [PARSAVERUN]
        
        '''
        control_file_data = "pcf\n* control data\nrestart estimation\n"
        all_selected_pars = []

        for sub in self.subcatchments_data:
            all_selected_pars.extend(sub.get_all_selected_pars())

        all_selected_pars.extend(self.lid_controls_data.get_all_selected_pars())
        num_of_pars = len(all_selected_pars)
        # print(obs_data[:50])
        # make number of observation data equal to number of output data
        num_of_obs = len(self.out_lines)

        control_file_data += "   " + str(num_of_pars) + "    " + str(num_of_obs) + "    " + "1    0    1\n"
        control_file_data +=  "    1     1 single point 1 0 0\n"
        control_file_data += "  5.0   2.0   0.3    0.01  10\n"
        control_file_data += "  5.0   5.0   0.001\n"
        control_file_data += "  0.1\n"
        control_file_data += "   30  0.01     4     3  0.01     3\n"
        control_file_data += "    1     1     1\n"
        '''
        Parameter data
        '''
        control_file_data += "* parameter groups\nparagroup  relative 0.01  0.0  switch  2.0 parabolic\n\n"

        control_file_data += "* parameter data\n"
        #  ldu_wdth  fixed  factor   90.1   30.0  110.0  paragroup  1.0   0.0  1

        for par in all_selected_pars:

            par_short_name = par.get_short_name()[1:-1]

            par_val = par.get_value()
            par_low_limit = par.get_lower_limit()
            par_up_limit = par.get_upper_limit()

            control_file_data += par_short_name + "           "

            if par.is_checked_fixed:
                control_file_data += "fixed"
            if par.is_checked_none:
                control_file_data += "none"

            control_file_data += "  factor    " + par_val + "    " + par_low_limit + "    " + \
                par_up_limit + "    paragroup  1.0  0.0  1\n"

        '''
        Observation data
        '''
        control_file_data += "* observation groups\nobsgroup\n\n"
        control_file_data += "* observation data\n"
        line_num = 0
        lines = self.out_lines
        obs_name = self.obs_name
        obs_lines = ""

        while line_num < len(lines):
            # date (SWMM output file)
            dstamp = lines[line_num].split()[0]
            dstamp = dstamp.split("/")[0] + dstamp.split("/")[1] +dstamp.split("/")[2]
            # time (SWMM output file)
            tstamp = lines[line_num].split()[1]
            tstamp = tstamp.split(":")[0] + tstamp.split(":")[1]
            # get observed value
            obs_value=observationData.getObservationValue(dstamp,tstamp)
            if obs_value=="":
                print("ERROR, not find the observed value of specific time")

            line = obs_name + dstamp + tstamp + "               " + obs_value + "    1.0  obsgroup" "\n"
            obs_lines += line
            line_num += 1
        control_file_data += obs_lines + "\n"

        '''
        Model Command Line Section
        '''

        control_file_data += "* model command line\n"

        self.rpt_fname = self.inp_fname[:-3] + "rpt"
        self.out_fname1 = self.inp_fname[:-3] + "out"
        command_line_data = "swmm\\swmm5.exe " + self.inp_fname + " " + self.rpt_fname + " " + self.out_fname1 + "\n\n"

        control_file_data += command_line_data

        '''
        Model Input Output Data Section
        '''

        control_file_data += "* model input/output\n"
        self.tpl_fname = self.inp_fname[:-3] + "tpl"
        control_file_data += self.tpl_fname + " " + self.inp_fname + "\n"
        control_file_data += self.ins_fname + " " + self.out_fname + "\n\n"
        control_file_data += "* prior information\n\n"
        self.control_fname = self.inp_fname[:-3] + "pst"

        with open(self.control_fname, 'w') as f:
            f.write(control_file_data)

        # self.mainFrame.pushButtonRunPEST.clicked.connect(self.run_pest)
        self.run_pest()

    def run_swmm(self):     # Run SWMM

        self.swmm_thread = SwmmThread(self.inp_fname)
        self.swmm_thread.start()
        print("After calling swmm thread")
        import time
        time.sleep(1)

    # Run PEST and check if PEST ran successfully or not.
    # If yes, display a graph for Measured values Vs. Output values before calibration Vs. Output values after calibration.
    # Get the output values before calibration from the .txt before running PEST and get the output values after calibration
    # from the .txt after running PEST.
    def run_pest(self):     # Run PEST when button clicked

        self.pest_thread = PestThread(self.control_fname)
        # print(self.measured_data)
        self.pest_thread.start()
        print("After calling pest thread")
        self.pest_thread.finished.connect(self.finished_pest_thread)

    def finished_pest_thread(self):     # After running PEST
        # print(self.output_values_before_calibration)

        with open(self.out_fname, 'r') as out_file:
            out_lines = out_file.readlines()

        for line_num in range(len(out_lines)):
            if out_lines[line_num].startswith("-------"):
                start_line = line_num + 1

        out_lines = out_lines[start_line:]

        self.output_values_after_calibration = []  # Output values after calibration:

        for line in out_lines:
            self.output_values_after_calibration.append(line[self.output_location_start:(self.output_location_end + 1)])

        self.plot_graphs()

    def plot_graphs(self):     # Display graphs
        temp = []
        for i in self.output_values_after_calibration:
            temp.append(float((i.strip()).replace(' ','')))

        self.output_values_after_calibration = temp

        temp1 = []

        for i in self.measured_data:
            temp1.append(float(i.strip()))

        self.measured_data = temp1

        print("Measured data: ")
        print(self.measured_data)
        print("Before calibration: ")
        print(self.output_values_before_calibration)
        print("After calibration: ")
        print(self.output_values_after_calibration)

        self.measured_data = self.measured_data[:len(self.output_values_after_calibration)]
        # print(len(self.measured_data))
        # print(len(self.output_values_after_calibration))

        x = linspace(min(self.measured_data), max(self.measured_data), len(self.measured_data))

        self.win = pg.GraphicsWindow(title="Output Graphs",size=(1200,600)) #Set main window
        self.win.setBackground(pg.mkColor('w')) #Set background

        # r_squared1 = self.r_squared(self.output_values_before_calibration, self.measured_data)
        NS1=spotpy.objectivefunctions.nashsutcliffe(self.output_values_before_calibration, self.measured_data)
        r_squared1 =spotpy.objectivefunctions.rsquared(self.output_values_before_calibration, self.measured_data)
        label_r_squared1="R squared= "+str(r_squared1) +"<Br/>"
        label_NSE1='Nash-Sutcliffe efficiency= '+str(NS1)+"<Br/>"
        label_bottom1='<Br/>Time Series<Br/><Br/>'+label_r_squared1+label_NSE1
        # print(NS1)
        p = self.win.addPlot() #Plot 1st Graph
        p.setLabel('top','Measured data Vs. Output data<Br/>',color='000000',size='8pt')
        p.setTitle('Before Calibration<Br/>',color='000000',size='10pt')
        p.addLegend(offset=(30,30))
        # p.setLabel("left", "Drain Outflow", color='000000')
        p.setLabel("left", self.observationType, color='000000') # Y label
        # p.setLabel("bottom", "Time Series", color='000000')
        p.setLabel("bottom", text=label_bottom1, color='000000', size='8pt') # X label
        p.plot(self.measured_data, pen=pg.mkPen('b', width=2), name="Measured data")
        p.plot(self.output_values_before_calibration, pen=pg.mkPen('r', width=2), name="Output before calibration")

        r_squared2 = spotpy.objectivefunctions.rsquared(self.output_values_after_calibration, self.measured_data)
        NS2=spotpy.objectivefunctions.nashsutcliffe(self.output_values_after_calibration, self.measured_data)
        label_r_squared2 = "R squared= " + str(r_squared2)+"<Br/>"
        label_NSE2='Nash-Sutcliffe efficiency= '+str(NS2)+"<Br/>"
        label_bottom2='<Br/>Time Series<Br/><Br/>'+label_r_squared2+label_NSE2
        # print(NS2)
        p1 = self.win.addPlot() #Plot 2nd Graph
        p1.setLabel('top', 'Measured data Vs. Output data<Br/>', color='000000', size='8pt')
        p1.setTitle("After Calibration<Br/>", color='000000', size='10pt')
        p1.addLegend(offset=(30,30))
        p1.setLabel("left", self.observationType, color='000000') # Y label
        # p1.setLabel("bottom", "Time Series", color='000000')
        p1.setLabel('bottom', text=label_bottom2, color='000000', size='8pt') # X label
        p1.plot(self.measured_data, pen=pg.mkPen('b', width=2), name="Measured data")
        p1.plot(self.output_values_after_calibration, pen=pg.mkPen('g', width=2), name="Output after calibration")


    def loadLIDControlsUI(self):

        if self.lid_controls_data.has_surface_layer: # Display Surface if LID Controls included it
            self.mainFrame.listLID_Controls.addItem(QtWidgets.QListWidgetItem("Surface"))

        if self.lid_controls_data.has_pavement_layer:# Display Pavement if LID Controls included it
            self.mainFrame.listLID_Controls.addItem(QtWidgets.QListWidgetItem("Pavement"))

        if self.lid_controls_data.has_soil_layer:# Display Soil if LID Controls included it
            self.mainFrame.listLID_Controls.addItem(QtWidgets.QListWidgetItem("Soil"))

        if self.lid_controls_data.has_storage_layer:# Display Storage if LID Controls included it
            self.mainFrame.listLID_Controls.addItem(QtWidgets.QListWidgetItem("Storage"))

        if self.lid_controls_data.has_underdrain_system:# Display Drain if LID Controls included it
            self.mainFrame.listLID_Controls.addItem(QtWidgets.QListWidgetItem("Drain"))

        if self.lid_controls_data.has_drainmat_system:# Display DrainMat if LID Controls included it
            self.mainFrame.listLID_Controls.addItem(QtWidgets.QListWidgetItem("DrainMat"))

        self.mainFrame.listLID_Controls.itemClicked[QtWidgets.QListWidgetItem].connect(self.clickedSlotLID_Controls)

    def clickedSlotLID_Controls(self, item):
        self.displaySubAndLIDWindow(item, "LID_Controls")

    def clickedSlotSub(self, item):
        # self.current_sub=None
        for i in range(len(self.subcatchments_data)):
            if self.subcatchments_data[i].name==item.text():
                self.current_sub=self.subcatchments_data[i]

        self.displaySubAndLIDWindow(item, "Sub")

    def createLineEdit(self, item):
        line_edit = cQLineEdit(self)

        line_edit.setText(item.value)
        line_edit.setMinimumWidth(185)
        line_edit.setMaximumWidth(185)
        line_edit.setReadOnly(True)
        return line_edit

    def InitiateLIDUIFrom(self):
        # Initialize layer's UI Form
        if self.lid_controls_data.has_surface_layer:  # If LID Controls included surface
            self.surface_layer_storage_depth_form = Ui_Form()
            self.surface_layer_vegetative_cover_fraction_line_edit_form = Ui_Form()
            self.surface_layer_roughness_line_edit_form = Ui_Form()
            self.surface_layer_slope_line_edit_form = Ui_Form()
            self.surface_layer_swale_side_slope_line_edit_form = Ui_Form()

        if self.lid_controls_data.has_pavement_layer:  # If LID Controls included pavement layer
            self.pavement_layer_thickness_line_edit_form = Ui_Form()
            self.pavement_layer_void_ratio_line_edit_form = Ui_Form()
            self.pavement_layer_impervious_surface_fraction_line_edit_form = Ui_Form()
            self.pavement_layer_permeability_line_edit_form = Ui_Form()
            self.pavement_layer_clogging_factor_line_edit_form = Ui_Form()

        if self.lid_controls_data.has_soil_layer:  # If LID Controls included soil
            self.soil_layer_thickness_line_edit_form = Ui_Form()
            self.soil_layer_porosity_line_edit_form = Ui_Form()
            self.soil_layer_field_capacity_line_edit_form = Ui_Form()
            self.soil_layer_wilting_point_line_edit_form = Ui_Form()
            self.soil_layer_conductivity_line_edit_form = Ui_Form()
            self.soil_layer_slope_line_edit_form = Ui_Form()
            self.soil_layer_suction_head_line_edit_form = Ui_Form()

        if self.lid_controls_data.has_storage_layer:  # If LID Controls included storage
            self.storage_layer_height_line_edit_form = Ui_Form()
            self.storage_layer_void_ratio_line_edit_form = Ui_Form()
            self.storage_layer_filtration_rate_line_edit_form = Ui_Form()
            self.storage_layer_clogging_factor_line_edit_form = Ui_Form()

        if self.lid_controls_data.has_underdrain_system:  # If LID Controls included underdrain_system
            self.drain_coefficient_line_edit_form = Ui_Form()
            self.drain_exponent_line_edit_form = Ui_Form()
            self.drain_offset_height_line_edit_form = Ui_Form()
            self.drain_delay_line_edit_form = Ui_Form()

        if self.lid_controls_data.has_drainmat_system:  # If LID Controls included DrainMat
            self.drainmat_thickness_line_edit_form = Ui_Form()
            self.drainmat_void_fraction_line_edit_form = Ui_Form()
            self.drainmat_roughness_line_edit_form = Ui_Form()

    def InitiateSubUIForm(self): # Initialize Subcatchment's UI Form
        for i in range(len(self.subcatchments_data)):
            self.subcatchments_data[i].area_line_edit_form = Ui_Form()
            self.subcatchments_data[i].percent_impervious_line_edit_form = Ui_Form()
            self.subcatchments_data[i].width_line_edit_form = Ui_Form()
            self.subcatchments_data[i].percent_slope_line_edit_form = Ui_Form()
            self.subcatchments_data[i].n_imperv_line_edit_form = Ui_Form()
            self.subcatchments_data[i].n_perv_line_edit_form = Ui_Form()
            self.subcatchments_data[i].storage_depth_imperv_line_edit_form = Ui_Form()
            self.subcatchments_data[i].storage_depth_perv_line_edit_form = Ui_Form()
            self.subcatchments_data[i].percent_zero_impervious_line_edit_form = Ui_Form()
            self.subcatchments_data[i].suction_line_edit_form = Ui_Form()
            self.subcatchments_data[i].hydraulic_conductivity_line_edit_form = Ui_Form()
            self.subcatchments_data[i].initial_moisture_deficit_line_edit_form = Ui_Form()
            if self.subcatchments_data[i].control_name != '':
                self.subcatchments_data[i].number_replicate_units_line_edit_form = Ui_Form()
                self.subcatchments_data[i].area_each_unit_line_edit_form = Ui_Form()
                self.subcatchments_data[i].top_width_overland_flow_surface_line_edit_form = Ui_Form()
                self.subcatchments_data[i].percent_initially_saturated_line_edit_form = Ui_Form()
                self.subcatchments_data[i].percent_impervious_area_treated_line_edit_form = Ui_Form()
                self.subcatchments_data[i].send_outflow_pervious_area_line_edit_form = Ui_Form()

    def saveParameterValues(self, parameter):    # Save upper and lower limit of the parameter value whenever changed
        #Subcatchment Parameters
        if parameter.name=='area':
            tempFormUI=self.current_sub.area_line_edit_form
        elif parameter.name=='impervious_percent':
            tempFormUI = self.current_sub.percent_impervious_line_edit_form
        elif parameter.name=='width':
            tempFormUI = self.current_sub.width_line_edit_form
        elif parameter.name=='percent_slope':
            tempFormUI = self.current_sub.percent_slope_line_edit_form
        elif parameter.name=='n_imperv':
            tempFormUI = self.current_sub.n_imperv_line_edit_form
        elif parameter.name=='n_perv':
            tempFormUI = self.current_sub.n_perv_line_edit_form
        elif parameter.name=='imperv_storage_depth':
            tempFormUI = self.current_sub.storage_depth_imperv_line_edit_form
        elif parameter.name=='perv_storage_depth':
            tempFormUI = self.current_sub.storage_depth_perv_line_edit_form
        elif parameter.name=='percent_zero_impervious':
            tempFormUI = self.current_sub.percent_zero_impervious_line_edit_form
        elif parameter.name=='suction':
            tempFormUI = self.current_sub.suction_line_edit_form
        elif parameter.name=='hydraulic_conductivity':
            tempFormUI = self.current_sub.hydraulic_conductivity_line_edit_form
        elif parameter.name=='initial_moisture_deficit':
            tempFormUI = self.current_sub.initial_moisture_deficit_line_edit_form
        elif parameter.name=='number_replicate_units':
            tempFormUI = self.current_sub.number_replicate_units_line_edit_form
        elif parameter.name=='area_each_unit':
            tempFormUI = self.current_sub.area_each_unit_line_edit_form
        elif parameter.name=='top_width_overland_flow_surface':
            tempFormUI = self.current_sub.top_width_overland_flow_surface_line_edit_form
        elif parameter.name=='percent_initially_saturated':
            tempFormUI = self.current_sub.percent_initially_saturated_line_edit_form
        elif parameter.name=='percent_impervious_area_treated':
            tempFormUI = self.current_sub.percent_impervious_area_treated_line_edit_form
        elif parameter.name=='send_outflow_pervious_area':
            tempFormUI = self.current_sub.send_outflow_pervious_area_line_edit_form

        #LID Controls Parameters

        if parameter.name=='surface_layer_storage_depth':
            tempFormUI = self.surface_layer_storage_depth_form
        elif parameter.name=='surface_layer_vegetative_cover_fraction':
            tempFormUI = self.surface_layer_vegetative_cover_fraction_line_edit_form
        elif parameter.name=='surface_layer_roughness':
            tempFormUI = self.surface_layer_roughness_line_edit_form
        elif parameter.name=='surface_layer_slope':
            tempFormUI = self.surface_layer_slope_line_edit_form
        elif parameter.name=='surface_layer_swale_side_slope':
            tempFormUI = self.surface_layer_swale_side_slope_line_edit_form
        elif parameter.name=='pavement_layer_thickness':
            tempFormUI = self.pavement_layer_thickness_line_edit_form
        elif parameter.name=='pavement_layer_void_ratio':
            tempFormUI = self.pavement_layer_void_ratio_line_edit_form
        elif parameter.name=='pavement_layer_impervious_surface_fraction':
            tempFormUI = self.pavement_layer_impervious_surface_fraction_line_edit_form
        elif parameter.name=='pavement_layer_permeability':
            tempFormUI = self.pavement_layer_permeability_line_edit_form
        elif parameter.name=='pavement_layer_clogging_factor':
            tempFormUI = self.pavement_layer_clogging_factor_line_edit_form
        elif parameter.name=='soil_layer_thickness':
            tempFormUI = self.soil_layer_thickness_line_edit_form
        elif parameter.name=='soil_layer_porosity':
            tempFormUI = self.soil_layer_porosity_line_edit_form
        elif parameter.name=='soil_layer_field_capacity':
            tempFormUI = self.soil_layer_field_capacity_line_edit_form
        elif parameter.name=='soil_layer_wilting_point':
            tempFormUI = self.soil_layer_wilting_point_line_edit_form
        elif parameter.name=='soil_layer_conductivity':
            tempFormUI = self.soil_layer_conductivity_line_edit_form
        elif parameter.name=='soil_layer_slope':
            tempFormUI = self.soil_layer_slope_line_edit_form
        elif parameter.name=='soil_layer_suction_head':
            tempFormUI = self.soil_layer_suction_head_line_edit_form
        elif parameter.name=='storage_layer_height':
            tempFormUI = self.storage_layer_height_line_edit_form
        elif parameter.name=='storage_layer_void_ratio':
            tempFormUI = self.storage_layer_void_ratio_line_edit_form
        elif parameter.name=='storage_layer_filtration_rate':
            tempFormUI = self.storage_layer_filtration_rate_line_edit_form
        elif parameter.name=='storage_layer_clogging_factor':
            tempFormUI = self.storage_layer_clogging_factor_line_edit_form
        elif parameter.name=='drain_coefficient':
            tempFormUI = self.drain_coefficient_line_edit_form
        elif parameter.name=='drain_exponent':
            tempFormUI = self.drain_exponent_line_edit_form
        elif parameter.name=='drain_offset_height':
            tempFormUI = self.drain_offset_height_line_edit_form
        elif parameter.name=='drain_delay':
            tempFormUI = self.drain_delay_line_edit_form
        elif parameter.name=='drainmat_thickness':
            tempFormUI = self.drainmat_thickness_line_edit_form
        elif parameter.name=='drainmat_void_fraction':
            tempFormUI = self.drainmat_void_fraction_line_edit_form
        elif parameter.name=='drainmat_roughness':
            tempFormUI = self.drainmat_roughness_line_edit_form

        lower_limit = tempFormUI.lineEdit_LowerLimit.text()
        upper_limit = tempFormUI.lineEdit_UpperLimit.text()
        is_checked_fixed = tempFormUI.checkBox_Fixed.checkState()
        is_checked_none = tempFormUI.checkBox_None.checkState()

        # if 'calibrate' box checked, then 'fixed' box will be unchecked
        # if is_checked_none == True or 1:
        #     is_checked_fixed = 0
        #     tempFormUI.checkBox_Fixed.setChecked(False)
        # if is_checked_none== False or 0 or '':
        #     is_checked_fixed = 1
        #     tempFormUI.checkBox_Fixed.setChecked(True)

        if (self.current_sub is not None) and (parameter.name in vars(self.current_sub).keys()):

            vars(vars(self.current_sub)[parameter.name])['lower_limit'] = lower_limit
            vars(vars(self.current_sub)[parameter.name])['upper_limit'] = upper_limit

            vars(vars(self.current_sub)[parameter.name])['is_checked_fixed'] = is_checked_fixed
            vars(vars(self.current_sub)[parameter.name])['is_checked_none'] = is_checked_none
        if parameter.name in vars(self.lid_controls_data).keys():

            vars(vars(self.lid_controls_data)[parameter.name])['lower_limit'] = lower_limit
            vars(vars(self.lid_controls_data)[parameter.name])['upper_limit'] = upper_limit

            vars(vars(self.lid_controls_data)[parameter.name])['is_checked_fixed'] = is_checked_fixed
            vars(vars(self.lid_controls_data)[parameter.name])['is_checked_none'] = is_checked_none
            # print('This is Test', parameter.name, ' ', ' low ', lower_limit, ' upper ', upper_limit,' fixed ',is_checked_fixed,' none ',is_checked_none)

    def readParameterValues(self, parameter):# Read upper and lower limit, fixed and none settings of the parameter value
        # Subcatchment Parameters
        if parameter.name == 'area':
            tempFormUI = self.current_sub.area_line_edit_form
        elif parameter.name == 'impervious_percent':
            tempFormUI = self.current_sub.percent_impervious_line_edit_form
        elif parameter.name == 'width':
            tempFormUI = self.current_sub.width_line_edit_form
        elif parameter.name == 'percent_slope':
            tempFormUI = self.current_sub.percent_slope_line_edit_form
        elif parameter.name == 'n_imperv':
            tempFormUI = self.current_sub.n_imperv_line_edit_form
        elif parameter.name == 'n_perv':
            tempFormUI = self.current_sub.n_perv_line_edit_form
        elif parameter.name == 'imperv_storage_depth':
            tempFormUI = self.current_sub.storage_depth_imperv_line_edit_form
        elif parameter.name == 'perv_storage_depth':
            tempFormUI = self.current_sub.storage_depth_perv_line_edit_form
        elif parameter.name == 'percent_zero_impervious':
            tempFormUI = self.current_sub.percent_zero_impervious_line_edit_form
        elif parameter.name == 'suction':
            tempFormUI = self.current_sub.suction_line_edit_form
        elif parameter.name == 'hydraulic_conductivity':
            tempFormUI = self.current_sub.hydraulic_conductivity_line_edit_form
        elif parameter.name == 'initial_moisture_deficit':
            tempFormUI = self.current_sub.initial_moisture_deficit_line_edit_form
        elif parameter.name == 'number_replicate_units':
            tempFormUI = self.current_sub.number_replicate_units_line_edit_form
        elif parameter.name == 'area_each_unit':
            tempFormUI = self.current_sub.area_each_unit_line_edit_form
        elif parameter.name == 'top_width_overland_flow_surface':
            tempFormUI = self.current_sub.top_width_overland_flow_surface_line_edit_form
        elif parameter.name == 'percent_initially_saturated':
            tempFormUI = self.current_sub.percent_initially_saturated_line_edit_form
        elif parameter.name == 'percent_impervious_area_treated':
            tempFormUI = self.current_sub.percent_impervious_area_treated_line_edit_form
        elif parameter.name == 'send_outflow_pervious_area':
            tempFormUI = self.current_sub.send_outflow_pervious_area_line_edit_form

        # LID Controls Parameters
        if parameter.name == 'surface_layer_storage_depth':
            tempFormUI = self.surface_layer_storage_depth_form
        elif parameter.name == 'surface_layer_vegetative_cover_fraction':
            tempFormUI = self.surface_layer_vegetative_cover_fraction_line_edit_form
        elif parameter.name == 'surface_layer_roughness':
            tempFormUI = self.surface_layer_roughness_line_edit_form
        elif parameter.name == 'surface_layer_slope':
            tempFormUI = self.surface_layer_slope_line_edit_form
        elif parameter.name == 'surface_layer_swale_side_slope':
            tempFormUI = self.surface_layer_swale_side_slope_line_edit_form
        elif parameter.name == 'pavement_layer_thickness':
            tempFormUI = self.pavement_layer_thickness_line_edit_form
        elif parameter.name == 'pavement_layer_void_ratio':
            tempFormUI = self.pavement_layer_void_ratio_line_edit_form
        elif parameter.name == 'pavement_layer_impervious_surface_fraction':
            tempFormUI = self.pavement_layer_impervious_surface_fraction_line_edit_form
        elif parameter.name == 'pavement_layer_permeability':
            tempFormUI = self.pavement_layer_permeability_line_edit_form
        elif parameter.name == 'pavement_layer_clogging_factor':
            tempFormUI = self.pavement_layer_clogging_factor_line_edit_form
        elif parameter.name == 'soil_layer_thickness':
            tempFormUI = self.soil_layer_thickness_line_edit_form
        elif parameter.name == 'soil_layer_porosity':
            tempFormUI = self.soil_layer_porosity_line_edit_form
        elif parameter.name == 'soil_layer_field_capacity':
            tempFormUI = self.soil_layer_field_capacity_line_edit_form
        elif parameter.name == 'soil_layer_wilting_point':
            tempFormUI = self.soil_layer_wilting_point_line_edit_form
        elif parameter.name == 'soil_layer_conductivity':
            tempFormUI = self.soil_layer_conductivity_line_edit_form
        elif parameter.name == 'soil_layer_slope':
            tempFormUI = self.soil_layer_slope_line_edit_form
        elif parameter.name == 'soil_layer_suction_head':
            tempFormUI = self.soil_layer_suction_head_line_edit_form
        elif parameter.name == 'storage_layer_height':
            tempFormUI = self.storage_layer_height_line_edit_form
        elif parameter.name == 'storage_layer_void_ratio':
            tempFormUI = self.storage_layer_void_ratio_line_edit_form
        elif parameter.name == 'storage_layer_filtration_rate':
            tempFormUI = self.storage_layer_filtration_rate_line_edit_form
        elif parameter.name == 'storage_layer_clogging_factor':
            tempFormUI = self.storage_layer_clogging_factor_line_edit_form
        elif parameter.name == 'drain_coefficient':
            tempFormUI = self.drain_coefficient_line_edit_form
        elif parameter.name == 'drain_exponent':
            tempFormUI = self.drain_exponent_line_edit_form
        elif parameter.name == 'drain_offset_height':
            tempFormUI = self.drain_offset_height_line_edit_form
        elif parameter.name == 'drain_delay':
            tempFormUI = self.drain_delay_line_edit_form
        elif parameter.name == 'drainmat_thickness':
            tempFormUI = self.drainmat_thickness_line_edit_form
        elif parameter.name == 'drainmat_void_fraction':
            tempFormUI = self.drainmat_void_fraction_line_edit_form
        elif parameter.name == 'drainmat_roughness':
            tempFormUI = self.drainmat_roughness_line_edit_form


        if (self.current_sub is not None) and (parameter.name in vars(self.current_sub).keys()):
            lower_limit=vars(vars(self.current_sub)[parameter.name])['lower_limit']
            upper_limit=vars(vars(self.current_sub)[parameter.name])['upper_limit']

            is_checked_fixed=vars(vars(self.current_sub)[parameter.name])['is_checked_fixed']
            is_checked_none=vars(vars(self.current_sub)[parameter.name])['is_checked_none']

            tempFormUI.lineEdit_LowerLimit.setText(lower_limit)
            tempFormUI.lineEdit_UpperLimit.setText(upper_limit)
            if is_checked_fixed==0:
                tempFormUI.checkBox_Fixed.setChecked(False)
            else:
                tempFormUI.checkBox_Fixed.setChecked(True)
            if is_checked_none==0:
                tempFormUI.checkBox_None.setChecked(False)
            else:
                tempFormUI.checkBox_None.setChecked(True)

        if parameter.name in vars(self.lid_controls_data).keys():
            lower_limit=vars(vars(self.lid_controls_data)[parameter.name])['lower_limit']
            upper_limit=vars(vars(self.lid_controls_data)[parameter.name])['upper_limit']

            is_checked_fixed=vars(vars(self.lid_controls_data)[parameter.name])['is_checked_fixed']
            is_checked_none=vars(vars(self.lid_controls_data)[parameter.name])['is_checked_none']

            tempFormUI.lineEdit_LowerLimit.setText(lower_limit)
            tempFormUI.lineEdit_UpperLimit.setText(upper_limit)
            if is_checked_fixed==0:
                tempFormUI.checkBox_Fixed.setChecked(False)
            else:
                tempFormUI.checkBox_Fixed.setChecked(True)
            if is_checked_none==0:
                tempFormUI.checkBox_None.setChecked(False)
            else:
                tempFormUI.checkBox_None.setChecked(True)

    def saveSubParametersValue(self): # Save all Subcatchments' values ( limit,upper,fixed,none)
        if self.current_sub!=None:
            self.saveParameterValues(self.current_sub.area)
            self.saveParameterValues(self.current_sub.impervious_percent)
            self.saveParameterValues(self.current_sub.width)
            self.saveParameterValues(self.current_sub.percent_slope)
            self.saveParameterValues(self.current_sub.n_imperv)
            self.saveParameterValues(self.current_sub.n_perv)
            self.saveParameterValues(self.current_sub.imperv_storage_depth)
            self.saveParameterValues(self.current_sub.perv_storage_depth)
            self.saveParameterValues(self.current_sub.percent_zero_impervious)
            self.saveParameterValues(self.current_sub.suction)
            self.saveParameterValues(self.current_sub.hydraulic_conductivity)
            self.saveParameterValues(self.current_sub.initial_moisture_deficit)
            if self.current_sub.control_name != '':
                self.saveParameterValues(self.current_sub.number_replicate_units)
                self.saveParameterValues(self.current_sub.area_each_unit)
                self.saveParameterValues(self.current_sub.top_width_overland_flow_surface)
                self.saveParameterValues(self.current_sub.percent_initially_saturated)
                self.saveParameterValues(self.current_sub.percent_impervious_area_treated)
                self.saveParameterValues(self.current_sub.send_outflow_pervious_area)

    def saveLIDParametersValue(self):
        if self.lid_controls_data.has_surface_layer: # If LID Controls included surface
            self.saveParameterValues(self.lid_controls_data.surface_layer_storage_depth)
            self.saveParameterValues(self.lid_controls_data.surface_layer_vegetative_cover_fraction)
            self.saveParameterValues(self.lid_controls_data.surface_layer_roughness)
            self.saveParameterValues(self.lid_controls_data.surface_layer_slope)
            self.saveParameterValues(self.lid_controls_data.surface_layer_swale_side_slope)

        if self.lid_controls_data.has_pavement_layer:# If LID Controls included pavement layer
            self.saveParameterValues(self.lid_controls_data.pavement_layer_thickness)
            self.saveParameterValues(self.lid_controls_data.pavement_layer_void_ratio)
            self.saveParameterValues(self.lid_controls_data.pavement_layer_impervious_surface_fraction)
            self.saveParameterValues(self.lid_controls_data.pavement_layer_permeability)
            self.saveParameterValues(self.lid_controls_data.pavement_layer_clogging_factor)

        if self.lid_controls_data.has_soil_layer:# If LID Controls included soil
            self.saveParameterValues(self.lid_controls_data.soil_layer_thickness)
            self.saveParameterValues(self.lid_controls_data.soil_layer_porosity)
            self.saveParameterValues(self.lid_controls_data.soil_layer_field_capacity)
            self.saveParameterValues(self.lid_controls_data.soil_layer_wilting_point)
            self.saveParameterValues(self.lid_controls_data.soil_layer_conductivity)
            self.saveParameterValues(self.lid_controls_data.soil_layer_slope)
            self.saveParameterValues(self.lid_controls_data.soil_layer_suction_head)

        if self.lid_controls_data.has_storage_layer:# If LID Controls included storage
            self.saveParameterValues(self.lid_controls_data.storage_layer_height)
            self.saveParameterValues(self.lid_controls_data.storage_layer_void_ratio)
            self.saveParameterValues(self.lid_controls_data.storage_layer_filtration_rate)
            self.saveParameterValues(self.lid_controls_data.storage_layer_clogging_factor)

        if self.lid_controls_data.has_underdrain_system:# If LID Controls included underdrain_system

            self.saveParameterValues(self.lid_controls_data.drain_coefficient)
            self.saveParameterValues(self.lid_controls_data.drain_exponent)
            self.saveParameterValues(self.lid_controls_data.drain_offset_height)
            self.saveParameterValues(self.lid_controls_data.drain_delay)

        if self.lid_controls_data.has_drainmat_system:# If LID Controls included DrainMat
            self.saveParameterValues(self.lid_controls_data.drainmat_thickness)
            self.saveParameterValues(self.lid_controls_data.drainmat_void_fraction)
            self.saveParameterValues(self.lid_controls_data.drainmat_roughness)

    def readSubParametersValue(self):
        self.readParameterValues(self.current_sub.area)
        self.readParameterValues(self.current_sub.impervious_percent)
        self.readParameterValues(self.current_sub.width)
        self.readParameterValues(self.current_sub.percent_slope)
        self.readParameterValues(self.current_sub.n_imperv)
        self.readParameterValues(self.current_sub.n_perv)
        self.readParameterValues(self.current_sub.imperv_storage_depth)
        self.readParameterValues(self.current_sub.perv_storage_depth)
        self.readParameterValues(self.current_sub.percent_zero_impervious)
        self.readParameterValues(self.current_sub.suction)
        self.readParameterValues(self.current_sub.hydraulic_conductivity)
        self.readParameterValues(self.current_sub.initial_moisture_deficit)
        if self.current_sub.control_name != '':
            self.readParameterValues(self.current_sub.number_replicate_units)
            self.readParameterValues(self.current_sub.area_each_unit)
            self.readParameterValues(self.current_sub.top_width_overland_flow_surface)
            self.readParameterValues(self.current_sub.percent_initially_saturated)
            self.readParameterValues(self.current_sub.percent_impervious_area_treated)
            self.readParameterValues(self.current_sub.send_outflow_pervious_area)

    def readLIDParametersValue(self):
        if self.lid_controls_data.has_surface_layer: # If LID Controls included surface
            self.readParameterValues(self.lid_controls_data.surface_layer_storage_depth)
            self.readParameterValues(self.lid_controls_data.surface_layer_vegetative_cover_fraction)
            self.readParameterValues(self.lid_controls_data.surface_layer_roughness)
            self.readParameterValues(self.lid_controls_data.surface_layer_slope)
            self.readParameterValues(self.lid_controls_data.surface_layer_swale_side_slope)

        if self.lid_controls_data.has_pavement_layer:# If LID Controls included pavement layer
            self.readParameterValues(self.lid_controls_data.pavement_layer_thickness)
            self.readParameterValues(self.lid_controls_data.pavement_layer_void_ratio)
            self.readParameterValues(self.lid_controls_data.pavement_layer_impervious_surface_fraction)
            self.readParameterValues(self.lid_controls_data.pavement_layer_permeability)
            self.readParameterValues(self.lid_controls_data.pavement_layer_clogging_factor)

        if self.lid_controls_data.has_soil_layer:# If LID Controls included soil
            self.readParameterValues(self.lid_controls_data.soil_layer_thickness)
            self.readParameterValues(self.lid_controls_data.soil_layer_porosity)
            self.readParameterValues(self.lid_controls_data.soil_layer_field_capacity)
            self.readParameterValues(self.lid_controls_data.soil_layer_wilting_point)
            self.readParameterValues(self.lid_controls_data.soil_layer_conductivity)
            self.readParameterValues(self.lid_controls_data.soil_layer_slope)
            self.readParameterValues(self.lid_controls_data.soil_layer_suction_head)

        if self.lid_controls_data.has_storage_layer:# If LID Controls included storage
            self.readParameterValues(self.lid_controls_data.storage_layer_height)
            self.readParameterValues(self.lid_controls_data.storage_layer_void_ratio)
            self.readParameterValues(self.lid_controls_data.storage_layer_filtration_rate)
            self.readParameterValues(self.lid_controls_data.storage_layer_clogging_factor)

        if self.lid_controls_data.has_underdrain_system:# If LID Controls included underdrain_system

            self.readParameterValues(self.lid_controls_data.drain_coefficient)
            self.readParameterValues(self.lid_controls_data.drain_exponent)
            self.readParameterValues(self.lid_controls_data.drain_offset_height)
            self.readParameterValues(self.lid_controls_data.drain_delay)

        if self.lid_controls_data.has_drainmat_system:# If LID Controls included DrainMat
            self.readParameterValues(self.lid_controls_data.drainmat_thickness)
            self.readParameterValues(self.lid_controls_data.drainmat_void_fraction)
            self.readParameterValues(self.lid_controls_data.drainmat_roughness)

    def displaySubAndLIDWindow(self, item, type_of): # Load the parameters window for subcatchments and LID controls

        if type_of == "LID_Controls":
            for i in reversed(range(self.mainFrame.formLayout_LID.count())):  # clear formLayout_LID
                self.mainFrame.formLayout_LID.itemAt(i).widget().setParent(None)

            # save LID data (lower limit, upper limit,Fixed, None)
            self.saveLIDParametersValue()

            # read LID data (lower limit, upper limit,Fixed, None)
            self.readLIDParametersValue()

            # Connect LID Controls type action
            if item.text() == "Surface":
                surface_layer_storage_depth_line_edit = self.createLineEdit(self.lid_controls_data.surface_layer_storage_depth)
                surface_layer_vegetative_cover_fraction_line_edit = self.createLineEdit(self.lid_controls_data.surface_layer_vegetative_cover_fraction)
                surface_layer_roughness_line_edit = self.createLineEdit(self.lid_controls_data.surface_layer_roughness)
                surface_layer_slope_line_edit = self.createLineEdit(self.lid_controls_data.surface_layer_slope)
                surface_layer_swale_side_slope_line_edit = self.createLineEdit(self.lid_controls_data.surface_layer_swale_side_slope)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.surface_layer_storage_depth.label, surface_layer_storage_depth_line_edit)
                self.mainFrame.formLayout_LID.addRow('',self.surface_layer_storage_depth_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.surface_layer_vegetative_cover_fraction.label, surface_layer_vegetative_cover_fraction_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.surface_layer_vegetative_cover_fraction_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.surface_layer_roughness.label, surface_layer_roughness_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.surface_layer_roughness_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.surface_layer_slope.label, surface_layer_slope_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.surface_layer_slope_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.surface_layer_swale_side_slope.label, surface_layer_swale_side_slope_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.surface_layer_swale_side_slope_line_edit_form.horizontalLayoutWidget)
                # print(self.lid_controls_data.has_drainmat_system)

            if item.text() == "Pavement":
                pavement_layer_thickness_line_edit = self.createLineEdit(self.lid_controls_data.pavement_layer_thickness)
                pavement_layer_void_ratio_line_edit = self.createLineEdit(self.lid_controls_data.pavement_layer_void_ratio)
                pavement_layer_impervious_surface_fraction_line_edit = self.createLineEdit(self.lid_controls_data.pavement_layer_impervious_surface_fraction)
                pavement_layer_permeability_line_edit = self.createLineEdit(self.lid_controls_data.pavement_layer_permeability)
                pavement_layer_clogging_factor_line_edit = self.createLineEdit(self.lid_controls_data.pavement_layer_clogging_factor)



                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.pavement_layer_thickness.label, pavement_layer_thickness_line_edit)
                self.mainFrame.formLayout_LID.addRow('',self.pavement_layer_thickness_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.pavement_layer_void_ratio.label, pavement_layer_void_ratio_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.pavement_layer_void_ratio_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.pavement_layer_impervious_surface_fraction.label, pavement_layer_impervious_surface_fraction_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.pavement_layer_impervious_surface_fraction_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.pavement_layer_permeability.label, pavement_layer_permeability_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.pavement_layer_permeability_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.pavement_layer_clogging_factor.label, pavement_layer_clogging_factor_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.pavement_layer_clogging_factor_line_edit_form.horizontalLayoutWidget)

            if item.text() == "Soil":
                soil_layer_thickness_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_thickness)
                soil_layer_porosity_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_porosity)
                soil_layer_field_capacity_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_field_capacity)
                soil_layer_wilting_point_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_wilting_point)
                soil_layer_conductivity_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_conductivity)
                soil_layer_slope_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_slope)
                soil_layer_suction_head_line_edit = self.createLineEdit(self.lid_controls_data.soil_layer_suction_head)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_thickness.label, soil_layer_thickness_line_edit)
                self.mainFrame.formLayout_LID.addRow('',self.soil_layer_thickness_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_porosity.label, soil_layer_porosity_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.soil_layer_porosity_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_field_capacity.label, soil_layer_field_capacity_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.soil_layer_field_capacity_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_wilting_point.label, soil_layer_wilting_point_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.soil_layer_wilting_point_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_conductivity.label, soil_layer_conductivity_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.soil_layer_conductivity_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_slope.label, soil_layer_slope_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.soil_layer_slope_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.soil_layer_suction_head.label, soil_layer_suction_head_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.soil_layer_suction_head_line_edit_form.horizontalLayoutWidget)

            if item.text() == "Storage":
                storage_layer_height_line_edit = self.createLineEdit(self.lid_controls_data.storage_layer_height)
                storage_layer_void_ratio_line_edit = self.createLineEdit(self.lid_controls_data.storage_layer_void_ratio)
                storage_layer_filtration_rate_line_edit = self.createLineEdit(self.lid_controls_data.storage_layer_filtration_rate)
                storage_layer_clogging_factor_line_edit = self.createLineEdit(self.lid_controls_data.storage_layer_clogging_factor)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.storage_layer_height.label, storage_layer_height_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.storage_layer_height_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.storage_layer_void_ratio.label, storage_layer_void_ratio_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.storage_layer_void_ratio_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.storage_layer_filtration_rate.label, storage_layer_filtration_rate_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.storage_layer_filtration_rate_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.storage_layer_clogging_factor.label, storage_layer_clogging_factor_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.storage_layer_clogging_factor_line_edit_form.horizontalLayoutWidget)

            if item.text() == "Drain":
                drain_coefficient_line_edit = self.createLineEdit(self.lid_controls_data.drain_coefficient)
                drain_exponent_line_edit = self.createLineEdit(self.lid_controls_data.drain_exponent)
                drain_offset_height_line_edit = self.createLineEdit(self.lid_controls_data.drain_offset_height)
                drain_delay_line_edit = self.createLineEdit(self.lid_controls_data.drain_delay)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drain_coefficient.label, drain_coefficient_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drain_coefficient_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drain_exponent.label, drain_exponent_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drain_exponent_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drain_offset_height.label, drain_offset_height_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drain_offset_height_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drain_delay.label, drain_delay_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drain_delay_line_edit_form.horizontalLayoutWidget)

            if item.text() == "DrainMat":
                drainmat_thickness_line_edit = self.createLineEdit(self.lid_controls_data.drainmat_thickness)
                drainmat_void_fraction_line_edit = self.createLineEdit(self.lid_controls_data.drainmat_void_fraction)
                drainmat_roughness_line_edit = self.createLineEdit(self.lid_controls_data.drainmat_roughness)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drainmat_thickness.label, drainmat_thickness_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drainmat_thickness_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drainmat_void_fraction.label, drainmat_void_fraction_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drainmat_void_fraction_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_LID.addRow(self.lid_controls_data.drainmat_roughness.label, drainmat_roughness_line_edit)
                self.mainFrame.formLayout_LID.addRow('', self.drainmat_roughness_line_edit_form.horizontalLayoutWidget)

        if type_of == "Sub":
            # item list:
            # area
            # impervious_percent
            # width
            # percent_slope
            # n_imperv
            # n_perv
            # imperv_storage_depth
            # perv_storage_depth
            # percent_zero_impervious
            # suction
            # hydraulic_conductivity
            # initial_moisture_deficit

            for i in reversed(range(self.mainFrame.formLayout_Sub.count())):  # clear formLayout_Sub
                self.mainFrame.formLayout_Sub.itemAt(i).widget().setParent(None)

            # save Current Sub data (lower limit, upper limit,Fixed, None)
            self.saveSubParametersValue()

            # read Current Sub data (lower limit, upper limit,Fixed, None)
            self.readSubParametersValue()

            area_line_edit = self.createLineEdit(self.current_sub.area)
            percent_impervious_line_edit = self.createLineEdit(self.current_sub.impervious_percent)
            width_line_edit = self.createLineEdit(self.current_sub.width)
            percent_slope_line_edit = self.createLineEdit(self.current_sub.percent_slope)
            n_imperv_line_edit = self.createLineEdit(self.current_sub.n_imperv)
            n_perv_line_edit = self.createLineEdit(self.current_sub.n_perv)
            storage_depth_imperv_line_edit = self.createLineEdit(self.current_sub.imperv_storage_depth)
            storage_depth_perv_line_edit = self.createLineEdit(self.current_sub.perv_storage_depth)
            percent_zero_impervious_line_edit = self.createLineEdit(self.current_sub.percent_zero_impervious)
            suction_line_edit = self.createLineEdit(self.current_sub.suction)
            hydraulic_conductivity_line_edit = self.createLineEdit(self.current_sub.hydraulic_conductivity)
            initial_moisture_deficit_line_edit = self.createLineEdit(self.current_sub.initial_moisture_deficit)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.area.label, area_line_edit)
            self.mainFrame.formLayout_Sub.addRow( '',self.current_sub.area_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.impervious_percent.label, percent_impervious_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.percent_impervious_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.width.label, width_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.width_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.percent_slope.label, percent_slope_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.percent_slope_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.n_imperv.label, n_imperv_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.n_imperv_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.n_perv.label, n_perv_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.n_perv_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.imperv_storage_depth.label, storage_depth_imperv_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.storage_depth_imperv_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.perv_storage_depth.label, storage_depth_perv_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.storage_depth_perv_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.percent_zero_impervious.label, percent_zero_impervious_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.percent_zero_impervious_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.suction.label, suction_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.suction_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.hydraulic_conductivity.label, hydraulic_conductivity_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.hydraulic_conductivity_line_edit_form.horizontalLayoutWidget)


            self.mainFrame.formLayout_Sub.addRow(self.current_sub.initial_moisture_deficit.label, initial_moisture_deficit_line_edit)
            self.mainFrame.formLayout_Sub.addRow('', self.current_sub.initial_moisture_deficit_line_edit_form.horizontalLayoutWidget)

            # --------LID USAGE------------
            if self.current_sub.control_name != '':
                number_replicate_units_line_edit = self.createLineEdit(self.current_sub.number_replicate_units)
                area_each_unit_line_edit = self.createLineEdit(self.current_sub.area_each_unit)
                top_width_overland_flow_surface_line_edit = self.createLineEdit(self.current_sub.top_width_overland_flow_surface)
                percent_initially_saturated_line_edit = self.createLineEdit(self.current_sub.percent_initially_saturated)
                percent_impervious_area_treated_line_edit = self.createLineEdit(self.current_sub.percent_impervious_area_treated)
                send_outflow_pervious_area_line_edit = self.createLineEdit(self.current_sub.send_outflow_pervious_area)


                self.mainFrame.formLayout_Sub.addRow(self.current_sub.number_replicate_units.label, number_replicate_units_line_edit)
                self.mainFrame.formLayout_Sub.addRow('', self.current_sub.number_replicate_units_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_Sub.addRow(self.current_sub.area_each_unit.label, area_each_unit_line_edit)
                self.mainFrame.formLayout_Sub.addRow('', self.current_sub.area_each_unit_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_Sub.addRow(self.current_sub.top_width_overland_flow_surface.label, top_width_overland_flow_surface_line_edit)
                self.mainFrame.formLayout_Sub.addRow('', self.current_sub.top_width_overland_flow_surface_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_Sub.addRow(self.current_sub.percent_initially_saturated.label, percent_initially_saturated_line_edit)
                self.mainFrame.formLayout_Sub.addRow('', self.current_sub.percent_initially_saturated_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_Sub.addRow(self.current_sub.percent_impervious_area_treated.label, percent_impervious_area_treated_line_edit)
                self.mainFrame.formLayout_Sub.addRow('', self.current_sub.percent_impervious_area_treated_line_edit_form.horizontalLayoutWidget)


                self.mainFrame.formLayout_Sub.addRow(self.current_sub.send_outflow_pervious_area.label, send_outflow_pervious_area_line_edit)
                self.mainFrame.formLayout_Sub.addRow('', self.current_sub.send_outflow_pervious_area_line_edit_form.horizontalLayoutWidget)


class LoadMainFrame(QMainWindow, MainFrameUI.Ui_MainWindow): # Main Window

    def __init__(self):
        super(self.__class__, self).__init__()
        print("In second page")
        self.setupUi(self)
        # self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.show()

class cQLineEdit(QtWidgets.QLineEdit): # Lower and Upper Limit Line Edit

    clicked = pyqtSignal()

    def __init__(self, widget):
        super(cQLineEdit, self).__init__(widget)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()

class LoadHelpWindow(QMainWindow, HelpWindowUI.Ui_MainWindow): # Help Window

    def __init__(self):
        super(self.__class__, self).__init__()

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.show()

class LoadPestCalibrationWindow(QMainWindow, PestCalibrationUI.Ui_mainWindow): # PEST Calibration Window

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Swmm2Pest = MainFrame()
    Swmm2Pest.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
    Swmm2Pest.show()
    sys.exit(app.exec_())
