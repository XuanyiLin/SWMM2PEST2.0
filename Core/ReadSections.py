# ReadSections.py
#
# Project: SWMM2PEST
# Version: 2.0
# Date:   06/04/2018 (version 2.0; author: X.Lin)
#         07/16/2017 (version 1.0; author: S.Kamble)
#
# Read parameter values from Subcatchment and LIDControl.
#
from Core.Subcatchments import Subcatchment
from Core.LidControl import LIDControl

class ReadSections:

    input_file_name = ""

    def __init__(self):

        self.subcatchments_data = []
        self.lid_control_data = LIDControl()
        print("In ReadSections.__init__()")
        pass

    def read_subcatchment_data(self, file_name):

        ReadSections.input_file_name = file_name

        print(file_name)

        with open(file_name, 'r') as inp_file:

            print(file_name)

            lines = inp_file.readlines()

            # print lines
            # print "\n after"

        # subcatchments_data = []

        for line_num in range(len(lines)):

            if lines[line_num] == "[SUBCATCHMENTS]\n":
                sub_items = self.read_section_data(lines, line_num)

                print("Subcatchments: ")
                print(len(sub_items))

                sub_index = 0

                for item in sub_items:
                    if len(item) > 1:
                        item = item.split()
                        print(item)

                        sub_index = sub_index + 1

                        sub = Subcatchment(sub_index, item[0])  # Create and assign values to subcatchment objects.

                        # sub.name = item[0]
                        sub.rain_gage = item[1]
                        sub.outlet = item[2]
                        sub.area.value = item[3]
                        sub.impervious_percent.value = item[4]
                        sub.width.value = item[5]
                        sub.percent_slope.value = item[6]
                        sub.curb_length.value = item[7]
                        if len(item) > 8:
                            sub.snow_pack.value = item[8]

                        self.subcatchments_data.append(sub)

                print(len(self.subcatchments_data))

            if lines[line_num] == "[SUBAREAS]\n":
                sub_items = self.read_section_data(lines, line_num)

                print(sub_items)
                for item, sub_data in zip(sub_items, self.subcatchments_data):

                    item = item.split()
                    print(item)
                    print("Sub Data: ")
                    print(sub_data)
                    if item[0] == sub_data.name:
                        print("in If")
                        sub_data.n_imperv.value = item[1]
                        sub_data.n_perv.value = item[2]
                        sub_data.imperv_storage_depth.value = item[3]
                        sub_data.perv_storage_depth.value = item[4]
                        sub_data.percent_zero_impervious.value = item[5]
                        sub_data.subarea_routing.value = item[6]
                        if len(item) > 7:
                            sub_data.percent_routed.value = item[7]

            if lines[line_num] == "[INFILTRATION]\n":
                sub_items = self.read_section_data(lines, line_num)

                for item, sub_data in zip(sub_items, self.subcatchments_data):

                    item = item.split()
                    print(item)
                    print("Sub Data: ")
                    print(sub_data)

                    if item[0] == sub_data.name:
                        sub_data.suction.value = item[1]
                        sub_data.hydraulic_conductivity.value = item[2]
                        sub_data.initial_moisture_deficit.value = item[3]

            if lines[line_num] == "[LID_USAGE]\n":
                sub_items = self.read_section_data(lines, line_num)

                for item in sub_items:
                    item = item.split()

                    print("LID USAGE: ")

                    if len(item) > 0:

                        print(item[0])

                        for sub_data in self.subcatchments_data:

                            print(sub_data.name)

                            if item[0] == sub_data.name:
                                sub_data.control_name = item[1]
                                sub_data.number_replicate_units.value = item[2]
                                sub_data.area_each_unit.value = item[3]
                                sub_data.top_width_overland_flow_surface.value = item[4]
                                sub_data.percent_initially_saturated.value = item[5]
                                sub_data.percent_impervious_area_treated.value = item[6]
                                sub_data.send_outflow_pervious_area.value = item[7]
                                if len(item)>8:
                                    sub_data.detailed_report_file = item[8]
                                else:
                                    sub_data.detailed_report_file = 'unknown'
                                if len(item) > 9:
                                    sub_data.subcatchment_drains_to = item[9]


            if lines[line_num] == "[LID_CONTROLS]\n":
                lid_control_items = self.read_section_data(lines, line_num)

                print("LID CONTROLS: ")
                print(lid_control_items)

                for lid_item in lid_control_items:
                    if len(lid_item) > 2:
                        lid_item = lid_item.split()

                        if lid_item[1] == "SURFACE":
                            self.lid_control_data.has_surface_layer = True
                            self.lid_control_data.surface_layer_storage_depth.value = lid_item[2]
                            self.lid_control_data.surface_layer_vegetative_cover_fraction.value = lid_item[3]
                            self.lid_control_data.surface_layer_roughness.value = lid_item[4]
                            self.lid_control_data.surface_layer_slope.value = lid_item[5]
                            self.lid_control_data.surface_layer_swale_side_slope.value = lid_item[6]

                        if lid_item[1] == "PAVEMENT":
                            self.lid_control_data.has_pavement_layer = True
                            self.lid_control_data.pavement_layer_thickness.value = lid_item[2]
                            self.lid_control_data.pavement_layer_void_ratio.value = lid_item[3]
                            self.lid_control_data.pavement_layer_impervious_surface_fraction.value = lid_item[4]
                            self.lid_control_data.pavement_layer_permeability.value = lid_item[5]
                            self.lid_control_data.pavement_layer_clogging_factor.value = lid_item[6]

                        if lid_item[1] == "SOIL":
                            self.lid_control_data.has_soil_layer = True
                            self.lid_control_data.soil_layer_thickness.value = lid_item[2]
                            self.lid_control_data.soil_layer_porosity.value = lid_item[3]
                            self.lid_control_data.soil_layer_field_capacity.value = lid_item[4]
                            self.lid_control_data.soil_layer_wilting_point.value = lid_item[5]
                            self.lid_control_data.soil_layer_conductivity.value = lid_item[6]
                            self.lid_control_data.soil_layer_slope.value = lid_item[7]
                            self.lid_control_data.soil_layer_suction_head.value = lid_item[8]

                        if lid_item[1] == "STORAGE":
                            self.lid_control_data.has_storage_layer = True
                            self.lid_control_data.storage_layer_height.value = lid_item[2]
                            self.lid_control_data.storage_layer_void_ratio.value = lid_item[3]
                            self.lid_control_data.storage_layer_filtration_rate.value = lid_item[4]
                            self.lid_control_data.storage_layer_clogging_factor.value = lid_item[5]

                        if lid_item[1] == "DRAIN":
                            self.lid_control_data.has_underdrain_system = True
                            self.lid_control_data.drain_coefficient.value = lid_item[2]
                            self.lid_control_data.drain_exponent.value = lid_item[3]
                            self.lid_control_data.drain_offset_height.value = lid_item[4]
                            self.lid_control_data.drain_delay.value = lid_item[5]

                        if lid_item[1] == "DRAINMAT":
                            self.lid_control_data.has_drainmat_system = True
                            self.lid_control_data.drainmat_thickness.value = lid_item[2]
                            self.lid_control_data.drainmat_void_fraction.value = lid_item[3]
                            self.lid_control_data.drainmat_roughness.value = lid_item[4]

        return [self.subcatchments_data, self.lid_control_data]


    #@staticmethod
    def read_section_data(self, lines, line_num):

        data = ""

        line_num += 1

        while not (lines[line_num].startswith("[")):
            print(lines[line_num])

            if lines[line_num] != "":

                data += lines[line_num]

                line_num += 1
        # print data

        # print data.split("\n")
        items = []
        for item in data.split("\n"):

            if not (item.startswith("[") or item.startswith(";") or item == ""):
                items.append(item)
                # print item
        # print items
        return items


# an example:
'''
{'curb_length': '0', 'percent_routed': 100.0, 'impervious_percent': '100', 'tag': '', 'snow_pack': '',
'top_width_overland_flow_surface': '0', 'subcatchment_drains_to': '', 'area': '0.224', 'width': '143.000000',
'n_imperv': '.020000000', 'number_replicate_units': '0', 'percent_impervious_area_treated': '0',
'percent_initially_saturated': '0', 'imperv_storage_depth': '1', 'percent_slope': '.100000000', 'description': '',
'send_outflow_pervious_area': '0', 'detailed_report_file': '', 'n_perv': '0.24', 'perv_storage_depth': '5',
'control_name': 'None', 'outlet': 'LID', 'suction': '99.441', 'subarea_routing': 'OUTLET',
'percent_zero_impervious': '100', 'name': 'Roadway', 'rain_gage': '01-11-2006_Storm',
'initial_moisture_deficit': '0.378', 'hydraulic_conductivity': '7.112', 'area_each_unit': '0'}
'''

