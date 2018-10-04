DEFINES= -DLAHEY -DUSE_E_FORMAT -DPARALLEL -DFLUSHFILE

F90=lf95
FLAGS= -in -c -chk -trace -O0
#FLAGS= -in -c -O2
LD=lf95
LDFLAGS= -winconsole -chk -trace
#LDFLAGS= -winconsole -O2

######################################################################
# DON'T EDIT BELOW THIS LINE
######################################################################


all :   cppp.exe driver1.exe driver2.exe

cppp.exe :	cppp.obj
        $(LD) $(LDFLAGS) cppp.obj
        
cppp.obj :	cppp.f
        $(F90) cppp.f


driver1.exe :   driver1.obj mio.obj
        $(LD) $(LDFLAGS) driver1.obj mio.obj

driver1.obj :   driver1.f90 mio.obj
        $(F90) $(FLAGS) driver1.f90

driver1.f90 :       driver1.f
        cppp $(DEFINES) driver1.f driver1.f90


driver2.exe :   driver2.obj mio.obj prm.obj
        $(LD) $(LDFLAGS) driver2.obj mio.obj prm.obj

driver2.obj :   driver2.f90 mio.obj prm.obj
        $(F90) $(FLAGS) driver2.f90

driver2.f90 :       driver2.f
        cppp $(DEFINES) driver2.f driver2.f90



mio.obj :      mio.f90
        $(F90) $(FLAGS) mio.f90

model_input_output_interface.mod :      mio.f90
        $(F90) $(FLAGS) mio.f90

mio.f90 :       mio.f
        cppp $(DEFINES) mio.f mio.f90


prm.obj :      prm.f90 model_input_output_interface.mod
        $(F90) $(FLAGS) prm.f90

parallel_run_manager.mod :      prm.f90 model_input_output_interface.mod
        $(F90) $(FLAGS) prm.f90

prm.f90 :       prm.f
        cppp $(DEFINES) prm.F prm.f90


clean :
        del driver2.f90
        del driver1.f90
        del prm.f90
        del mio.f90
        del *.mod
        del *.obj
        del *.map


