# WriteSections.py
#
# Project: SWMM2PEST
# Version: 2.0
# Date:   06/04/2018 (version 2.0; author: X.Lin)
#         07/16/2017 (version 1.0; author: S.Kamble)
#
# Write .tpl file
# Find location of [SUBCATCHMENTS] and replace each subcatchment data with new data with parameter values replaced with
# short parameter names. And then write the file with this new data.

from Core.ReadSections import ReadSections

class write_sections():
    def __init__(self, subcatchments_data, lid_controls_data):

        self.subcatchments_data = subcatchments_data
        self.lid_controls_data = lid_controls_data

    # Write the new subcatchment data to template file
    def write_template_data(self, subcatchments):

        self.input_file_name = ReadSections.input_file_name
        self.read_subcatchment_data(self.input_file_name, self.subcatchments_data)
        self.tpl_file_name = self.input_file_name[:-3] + "tpl"
        self.replaced_file_lines = "ptf #\n" + self.string_of_file_lines

        with open(self.tpl_file_name, 'w') as tpl_file:
            tpl_file.write(self.replaced_file_lines)

        # print("Replaced file lines: ")
        # print(self.string_of_file_lines)
        # print("subcatchments data: ")
        # for sub in self.subcatchments_data:
        #     print(sub.sub_index)


    def read_subcatchment_data(self, file_name, subcatchments): # read subcatchment data and do replace operation.

        # print(file_name)
        with open(file_name, 'r') as inp_file:
            # print(file_name)

            self.list_of_file_lines = inp_file.readlines()

        with open(file_name, 'r') as inp_file:

            self.string_of_file_lines = inp_file.read()

            # print("String of file lines after reading: ")
            # print(self.string_of_file_lines)
            # original_subcatchment_data = ""

        for line_num in range(len(self.list_of_file_lines)):

            if self.list_of_file_lines[line_num] == "[SUBCATCHMENTS]\n":
                # print("line_num1: ")
                # print(line_num)
                # original_subcatchment_data = self.read_section_data(self.list_of_file_lines, line_num,
                #                                                     self.string_of_file_lines)
                # print("line_num2: ")
                # print(line_num)
                self.replace_subcatchment_data("SUBCATCHMENTS", line_num, subcatchments)

            if self.list_of_file_lines[line_num] == "[SUBAREAS]\n":
                self.replace_subcatchment_data("SUBAREAS", line_num, subcatchments)

            if self.list_of_file_lines[line_num] == "[INFILTRATION]\n":
                self.replace_subcatchment_data("INFILTRATION", line_num, subcatchments)

            if self.list_of_file_lines[line_num] == "[LID_USAGE]\n":
                self.replace_subcatchment_data("LID_USAGE", line_num, subcatchments)

            if self.list_of_file_lines[line_num] == "[LID_CONTROLS]\n":
                self.replace_lid_controls_data(line_num, self.lid_controls_data)

    # Replace LID controls data for each LID

    def replace_lid_controls_data(self, line_num, lid_controls_data):# replace parameters' name in lid control data.

        line_num += 1
        while not (self.list_of_file_lines[line_num].startswith("[")):

            if not (self.list_of_file_lines[line_num].startswith(";") or self.list_of_file_lines[line_num] == "" or
                        len(self.list_of_file_lines[line_num].split()) <= 2):

                individual_control_line = self.list_of_file_lines[line_num]
                individual_control_line_as_list_with_spaces = self.list_of_file_lines[line_num].split(" ")
                individual_control_line_as_list = self.list_of_file_lines[line_num].split()

                # print("individual control line: ")
                # print(individual_control_line)
                selected_pars = []

                control_name = individual_control_line_as_list[1]

                if control_name == "SURFACE":
                    selected_pars = lid_controls_data.get_selected_surface_pars()
                if control_name == "PAVEMENT":
                    selected_pars = lid_controls_data.get_selected_pavement_pars()
                if control_name == "SOIL":
                    selected_pars = lid_controls_data.get_selected_soil_pars()
                if control_name == "STORAGE":
                    selected_pars = lid_controls_data.get_selected_storage_pars()
                if control_name == "DRAIN":
                    selected_pars = lid_controls_data.get_selected_drain_pars()
                if control_name == "DRAINMAT":
                    selected_pars = lid_controls_data.get_selected_drainmat_pars()

                for par in selected_pars:
                    # print("par short name: ")
                    # print(par.get_short_name())
                    # print("par index: ")
                    # print(par.index)
                    individual_control_line_as_list[par.index] = par.get_short_name()

                for i in range(len(individual_control_line_as_list_with_spaces)):
                    if individual_control_line_as_list_with_spaces[i] == "":
                        individual_control_line_as_list.insert(i, individual_control_line_as_list_with_spaces[i])

                # print("LID controls data as list with spaces: ")
                # print(individual_control_line_as_list)

                replaced_control_line = ' '.join(individual_control_line_as_list)
                replaced_control_line += "\n"

                # print("Individual sub data: ")
                # print(individual_control_line)
                #
                # print("String of file lines before replacing: ")
                # print(self.string_of_file_lines)

                self.string_of_file_lines = self.string_of_file_lines.replace(individual_control_line, replaced_control_line)

                # print("String of file lines: ")
                # print(self.string_of_file_lines)
                #
                # print("replaced sub data: ")
                # print(replaced_control_line)

                # line_num += 1


            line_num += 1


    def replace_subcatchment_data(self, section_name, line_num, subcatchments): # replace parameters' name in subcatchment data.

        current_index = 0

        for subcatchment in subcatchments:

            # print((self.list_of_file_lines[line_num + 1].startswith("[") or
            #                self.list_of_file_lines[line_num + 1].startswith(";") or
            #                    self.list_of_file_lines[line_num + 1] == ""))
            line_num += 1

            while not (self.list_of_file_lines[line_num].startswith("[")):

                if not (self.list_of_file_lines[line_num].startswith(";") or self.list_of_file_lines[line_num] == ""):

                    print(self.list_of_file_lines[line_num])

                    current_index = current_index + 1
                    try:
                        current_sub_name = self.list_of_file_lines[line_num].split()[0]
                    except Exception:
                        print('\nERROR in write_sections.py_current_sub_name = self.list_of_file_lines[line_num].split()[0]\n')
                    # print("current sub name")
                    # print(current_sub_name)
                    # print(subcatchment.name)

                    individual_sub_data = ""

                    # print("current index: ")
                    # print(current_index)

                    if current_sub_name == subcatchment.name:

                        individual_sub_data = self.list_of_file_lines[line_num]

                        individual_sub_data_as_list_with_spaces = individual_sub_data.split(" ")

                        individual_sub_data_as_list = individual_sub_data.split()

                        selected_pars = []

                        if section_name == "SUBCATCHMENTS":
                            selected_pars = subcatchment.get_selected_subcatchment_pars()
                        if section_name == "SUBAREAS":
                            selected_pars = subcatchment.get_selected_subareas_pars()
                        if section_name == "INFILTRATION":
                            selected_pars = subcatchment.get_selected_inflitration_pars()
                        if section_name == "LID_USAGE":
                            if subcatchment.get_selected_lid_usage_pars() is None:
                                break
                            selected_pars = subcatchment.get_selected_lid_usage_pars()

                        for par in selected_pars:
                            # print("par short name: ")
                            # print(par.get_short_name())
                            # print("par index: ")
                            # print(par.index)

                            individual_sub_data_as_list[par.index] = par.get_short_name()

                        # print("parse\n")
                        for i in range(len(individual_sub_data_as_list_with_spaces)):
                            if individual_sub_data_as_list_with_spaces[i] == "":
                                individual_sub_data_as_list.insert(i, individual_sub_data_as_list_with_spaces[i])
                        # print("data as list with spaces: ")
                        # print(individual_sub_data_as_list)

                        replaced_sub_data = ' '.join(individual_sub_data_as_list)

                        replaced_sub_data += "\n"
                        # print("Individual sub data: ")
                        # print(individual_sub_data)

                        # print("String of file lines before replacing: ")
                        # print(self.string_of_file_lines)

                        self.string_of_file_lines = self.string_of_file_lines.replace(individual_sub_data, replaced_sub_data)

                        # print("String of file lines: ")
                        # print(self.string_of_file_lines)

                        # print("replaced sub data: ")
                        # print(replaced_sub_data)

                        break

                    else:  # for LID_USAGE, if there is only one line of subcatchment
                        line_num -= 1
                        break

                line_num += 1
