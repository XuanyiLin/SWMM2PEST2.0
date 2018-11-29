# ObservationData.py
#
# Project: SWMM2PEST
# Version: 2.1
# Date:   11/29/2018 (version 2.1; author: X.Lin)
#
# Operate Observation Data.
#
class ObservationData:
    # read data from observation file
    def readObsFile(self, obs_fname):
        with open(obs_fname, 'r') as f:
            lines = f.readlines()

        line_num=0
        self.date_list=[]
        self.time_list=[]
        self.data_list=[]
        self.data_lenth=len(lines)
        while line_num < len(lines):
            # date - mm/dd/yyyy
            date = lines[line_num].split()[0]
            # date_format - mmddyyyy
            date_format = ""+ date.split("/")[0] + date.split("/")[1] + date.split("/")[2]

            # time - hh:mm:ss
            time = lines[line_num].split()[1]
            # time_format - hhmm
            time_format = "" + time.split(":")[0] + time.split(":")[1]

            # data
            data = lines[line_num].split()[2]
            data_format = "" + data

            self.date_list.append(date_format)
            self.time_list.append(time_format)
            self.data_list.append(data_format)
            line_num += 1

    # get observed value of a specific time
    def getObservationValue(self, date, time):
        line_num = 0
        obs_value=""
        while line_num < self.data_lenth:
            # print(self.date_list[line_num])
            if self.date_list[line_num] == date:
                # print(self.time_list[line_num])
                if self.time_list[line_num] == time:
                    obs_value=self.data_list[line_num]
                    break
            line_num += 1
        return obs_value

    # get all observed value
    def getAllValue(self):
        return self.data_list

# if __name__ == '__main__':
#     obs_fname="C:/2009Q1/obs.txt"
#     obs_data= ObservationData()
#     obs_data.readObsFile(obs_fname)
#     print(obs_data.getObservationValue("01062009","1215"))