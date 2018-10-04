# Subcatchments.py
#
# Project: SWMM2PEST
# Version: 2.0
# Date:   06/04/2018 (version 2.0; author: X.Lin)
#         07/16/2017 (version 1.0; author: S.Kamble)
#
# Class type for subcatchments and all its parameters as variables

class Subcatchment():
    """Subcatchment geometry, location, parameters, and time-series data"""

    def __init__(self, sub_index, name):

        self.sub_index = sub_index

        self.name = name

        self.description = ''

        self.tag = ''

        self.rain_gage = 'None'

        self.outlet = 'None'

        self.area = DataField("area", "Area", self.name, 3)

        self.impervious_percent = DataField('impervious_percent', "% Impervious", self.name, 4)

        self.width = DataField('width', "Width", self.name, 5)

        self.percent_slope = DataField('percent_slope', "% Slope", self.name, 6)

        self.snow_pack = DataField('snow_pack', "Snow Pack", self.name, 7)

        self.curb_length = DataField('curb_length', "Curb Length", self.name, 8)

        # -------Sub Areas------------

        self.n_imperv = DataField('n_imperv', "N_Imperv", self.name, 1)

        self.n_perv = DataField('n_perv', "N_Perv", self.name, 2)

        self.imperv_storage_depth = DataField('imperv_storage_depth', "Storage Depth Imperv", self.name, 3)

        self.perv_storage_depth = DataField('perv_storage_depth', "Storage Depth Perv", self.name, 4)

        self.percent_zero_impervious = DataField('percent_zero_impervious', "% Zero Impervious", self.name, 5)

        self.subarea_routing = DataField('subarea_routing', "Subarea Routing", self.name, 6)

        self.percent_routed = DataField('percent_routed', "% Routing", self.name, 7)

        # -------Infiltration----------

        self.suction = DataField('suction', "Suction", self.name, 1)

        self.hydraulic_conductivity = DataField('hydraulic_conductivity', "Hydraulic Conductivity", self.name, 2)

        self.initial_moisture_deficit = DataField('initial_moisture_deficit', "Initial Moisture Deficit", self.name, 3)


        # -------LID_Usage-------------

        self.control_name = ''

        self.number_replicate_units = DataField('number_replicate_units', "Number Replicate Units", self.name, 2)

        self.area_each_unit = DataField('area_each_unit', "Area Each Unit", self.name, 3)

        self.top_width_overland_flow_surface = DataField('top_width_overland_flow_surface', "Top Width Overland Flow Surface", self.name, 4)

        self.percent_initially_saturated = DataField('percent_initially_saturated', "% Initially Saturated", self.name, 5)

        self.percent_impervious_area_treated = DataField('percent_impervious_area_treated', "% Imperv Area Treated", self.name, 6)

        self.send_outflow_pervious_area = DataField('send_outflow_pervious_area', "Send Outflow Perv Area", self.name, 7)

        self.detailed_report_file = ''

        self.subcatchment_drains_to = ''


    def get_sub_index(self):
        return self.sub_index


    def get_lid_usage_data_as_list(self):

        if self.control_name == '':
            return None

        return [self.number_replicate_units, self.area_each_unit, self.top_width_overland_flow_surface,
                self.percent_initially_saturated, self.percent_impervious_area_treated, self.send_outflow_pervious_area]

    def get_subcatchment_data_as_list(self):

        return [self.area, self.impervious_percent, self.width, self.percent_slope, self.snow_pack, self.curb_length]

    def get_subareas_data_as_list(self):

        return [self.n_imperv, self.n_perv, self.imperv_storage_depth, self.perv_storage_depth,
                self.percent_zero_impervious, self.subarea_routing, self.percent_routed]

    def get_infiltration_data_as_list(self):

        return [self.suction, self.hydraulic_conductivity, self.initial_moisture_deficit]

    def get_all_data_as_list(self):

        return [self.number_replicate_units, self.area_each_unit, self.top_width_overland_flow_surface,
                self.percent_initially_saturated, self.percent_impervious_area_treated, self.send_outflow_pervious_area,
                self.area, self.impervious_percent, self.width, self.percent_slope, self.snow_pack, self.curb_length,
                self.n_imperv, self.n_perv, self.imperv_storage_depth, self.perv_storage_depth,
                self.percent_zero_impervious, self.subarea_routing, self.percent_routed,
                self.suction, self.hydraulic_conductivity, self.initial_moisture_deficit]


    def get_all_selected_pars(self):

        list_of_selected_pars = []

        for parameter in self.get_all_data_as_list():

            if parameter.check_if_selected_for_estimation():
                print(parameter.name)
                print('get_all_selected_pars')
                list_of_selected_pars.append(parameter)

        print("List of selected pars: ")
        print(list_of_selected_pars)

        return list_of_selected_pars




    def get_selected_lid_usage_pars(self):

        list_of_selected_pars = []

        if self.get_lid_usage_data_as_list() is None:
            return None

        else:

            for parameter in self.get_lid_usage_data_as_list():

                if parameter.check_if_selected_for_estimation():
                    print(parameter.name)
                    print('get_selected_lid_usage_pars')
                    list_of_selected_pars.append(parameter)

            print("List of selected pars: ")
            print(list_of_selected_pars)

            return list_of_selected_pars


    def get_selected_inflitration_pars(self):

        list_of_selected_pars = []

        for parameter in self.get_infiltration_data_as_list():

            if parameter.check_if_selected_for_estimation():
                print(parameter.name)
                print('get_selected_inflitration_pars')
                list_of_selected_pars.append(parameter)

        print("List of selected pars: ")
        print(list_of_selected_pars)

        return list_of_selected_pars


    def get_selected_subareas_pars(self):

        list_of_selected_pars = []

        for parameter in self.get_subareas_data_as_list():

            if parameter.check_if_selected_for_estimation():
                print(parameter.name)
                print('get_selected_subareas_pars')
                list_of_selected_pars.append(parameter)

        print("List of selected pars: ")
        print(list_of_selected_pars)

        return list_of_selected_pars


    def get_selected_subcatchment_pars(self):

        list_of_selected_pars = []

        for parameter in self.get_subcatchment_data_as_list():

            if parameter.check_if_selected_for_estimation():

                print(parameter.name)
                print('get_selected_subcatchment_pars')
                list_of_selected_pars.append(parameter)

        print("List of selected pars: ")
        print(list_of_selected_pars)

        return list_of_selected_pars



class DataField():

    def __init__(self, name, label, sub_name="", index=0):
        self.name = name
        self.value = ''
        self.label = label

        self.sub_name = sub_name

        self.index = index
        # self.edit_field = QtWidgets.QLineEdit().setText(self.value)

        self.lower_limit = ''
        self.upper_limit = ''

        self.short_name = ''

        self.is_selected_for_estimation = self.check_if_selected_for_estimation()

        self.is_checked_fixed = False
        self.is_checked_none = False


    def get_value(self):
        return self.value

    def get_lower_limit(self):
        return self.lower_limit

    def get_upper_limit(self):
        return self.upper_limit

    def check_if_selected_for_estimation(self):

        if self.lower_limit != '' or self.upper_limit != '':

            print("in selected for estimation")

            return True

    def generate_short_name(self, name):

        name = name.lower()

        short_name = ""

        for i in range(len(name)):
            if name[i] not in [" ", "a", "e", "i", "o", "u"]:
                short_name += name[i]

        return short_name

    def get_short_name(self):

        if self.check_if_selected_for_estimation():

            self.short_name = self.generate_short_name(self.name)

            if len(self.sub_name) > 0:

                self.short_name = self.sub_name[0] + self.sub_name[-1] + self.short_name

        if len(self.name) > 6:
            return "#" + self.short_name[:12] + "#"
        else:
            if len(self.sub_name) > 0:
                return "#" + self.sub_name[0] + self.sub_name[-1] + self.name + "#"




class HortonInfiltration():
    """Horton Infiltration parameters"""

    def __init__(self):

        self.subcatchment = "None"
        """Subcatchment name"""

        self.max_rate = '0.0'
        """Maximum infiltration rate on Horton curve (in/hr or mm/hr)"""

        self.min_rate = '0.0'
        """Minimum infiltration rate on Horton curve (in/hr or mm/hr)."""

        self.decay = '0.0'
        """Decay rate constant of Horton curve (1/hr)."""

        self.dry_time = '0.0'
        """Time it takes for fully saturated soil to dry (days)."""

        self.max_volume = '0.0'
        """Maximum infiltration volume possible (in or mm)."""


class GreenAmptInfiltration():
    """Green-Ampt Infiltration parameters"""

    def __init__(self):


        self.subcatchment = "None"
        """Subcatchment name"""

        self.suction = '0.0'
        """Soil capillary suction (in or mm)."""

        self.hydraulic_conductivity = '0.0'
        """Soil saturated hydraulic conductivity (in/hr or mm/hr)."""

        self.initial_moisture_deficit = '0.0'
        """Initial soil moisture deficit (volume of voids / total volume)."""


class CurveNumberInfiltration():
    """Curve Number Infiltration parameters"""

    def __init__(self):

        self.subcatchment = "None"
        """Subcatchment name"""

        self.curve_number = "None"
        """SCS Curve Number"""

        self.hydraulic_conductivity = '0'
        """Soil saturated hydraulic conductivity (no longer used for curve number infiltration)."""

        self.dry_days = '0.0'
        """Time it takes for fully saturated soil to dry (days)."""


class LIDUsage():
    """Specifies how an LID control will be deployed in a subcatchment"""

    def __init__(self):

        self.subcatchment_name = "None"
        """Name of the Subcatchment defined in [SUBCATCHMENTS] where this usage occurs"""

        self.control_name = "None"
        """Name of the LID control defined in [LID_CONTROLS] to be used in the subcatchment"""

        self.number_replicate_units = '0'
        """Number of equal size units of the LID practice deployed within the subcatchment"""

        self.area_each_unit = '0'
        """Surface area devoted to each replicate LID unit"""

        self.top_width_overland_flow_surface = '0'
        """Width of the outflow face of each identical LID unit"""

        self.percent_initially_saturated = '0'
        """Degree to which storage zone is initially filled with water"""

        self.percent_impervious_area_treated = '0'
        """Percent of the impervious portion of the subcatchment's non-LID area whose runoff
        is treated by the LID practice"""

        self.send_outflow_pervious_area = '0'
        """1 if the outflow from the LID is returned onto the subcatchment's pervious area rather
        than going to the subcatchment's outlet"""

        self.detailed_report_file = ''
        """Name of an optional file where detailed time series results for the LID will be written"""

        self.subcatchment_drains_to = ''
        """ID of a subcatchment that this LID drains to"""