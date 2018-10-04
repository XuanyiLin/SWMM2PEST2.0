# UpdateParameter.py
#
# Project: SWMM2PEST
# Version: 2.0
# Date:   06/04/2018 (version 2.0; author: X.Lin)
#
# Generate and Write SWMM report file path.
#
from Core.ReadSections import ReadSections

class UpdateParameter:

    def updateReportFile(self,inp_fname):
        read_file = ReadSections()  # Class ReadSections Instantiation
        all_data = read_file.read_subcatchment_data(inp_fname)
        subcatchments_data = all_data[0]
        detailed_report_file=subcatchments_data[-1].detailed_report_file #Get the last subcatchment detailed report file
        inp_fname_dir = inp_fname[:-4]
        out_fname = inp_fname_dir + '.txt'
        out_fname_dir = '\"' + inp_fname_dir + '.txt\"'
        if detailed_report_file!=None and detailed_report_file!='':

            # self.modifyOperations(self, inp_fname, 'detailed_report_file', out_fname)
            with open(inp_fname, 'r') as inp_file:
                lines = inp_file.readlines()

            with open(inp_fname, "w") as f_w:
                for line in lines:
                    f_w.write(line.replace(detailed_report_file,out_fname_dir))

        return out_fname


# if __name__ == '__main__':
    # read_file = ReadSections()  # Class ReadSections Instantiation
    # all_data = read_file.read_subcatchment_data('C:/2009Q1/groof09Q1.inp')
    # subcatchments_data = all_data[0]
    # print('*******************************************************************************************\n')
    # print(subcatchments_data[0].detailed_report_file)
    # up1=UpdateParameter()
    # out_fname=up1.updateReportFile('C:/2009Q1/groof09Q1.inp')
    # print(out_fname)