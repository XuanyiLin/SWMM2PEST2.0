module parallel_run_manager

private

! -- VARIABLES

! -- Resource and problem sizes.

        integer :: nslave                            ! Number of slaves
        integer :: maxrun                            ! Maximum number of runs that will ever be undertaken

! -- Control variables

        integer           :: iwait=200                  ! Wait period in 100ths of a second
        integer           :: repeatrun=1                ! Repeat a model run if an error condition arises
        logical           :: time_refresh_flag=.false.  ! Set to 1 to refresh run times on basis of last model run.
        double precision  :: fac_rerun=1.5              ! Run time factor used in overdue calculations.

! -- Flags and counters

        integer :: slavetest=0                       ! Ensures that a test has been made to see if slaves alive
        integer :: ncall=0                           ! Total number of model runs

! -- Time data

        integer :: prm_m1                            ! Initial months
        integer :: prm_d1                            ! Initial days
        integer :: prm_y1                            ! Initial years
        integer :: prm_h1                            ! Initial hours
        integer :: prm_min1                          ! Initial minutes
        integer :: prm_s1                            ! Initial seconds

! -- Data arrays for slaves

        integer, allocatable :: idet(:)              ! Slave detection indicator
        integer, allocatable :: iruntme(:)           ! Slave run times
        integer, allocatable :: jrun(:)              ! Run currently being undertaken by a slave
        integer, allocatable :: istats(:)            ! Status of slave
        integer, allocatable :: istrtme(:)           ! Start time of current run on slave

! -- Character slave data

        character (len=200), allocatable :: aslave(:)        ! Name of slaves
        character (len=200), allocatable :: asldir(:)        ! Working directory of slaves
        character (len=200), allocatable :: scom(:)          ! Model command line for slaves

! -- Data arrays for model runs

        integer, allocatable :: istatr(:)            ! Status of each model run
        integer, allocatable :: itrial(:)            ! Number of trials for a run

! -- File unit numbers

        integer  :: prm_mr                           ! unit number for run management record file
        integer  :: prm_mf                           ! unit number used for message files
        integer  :: prm_wk                           ! unit number for tasks such as file deletions
        integer  :: prm_nr                           ! unit number to record completion of runs

! -- Filenames

        character (len=200) :: afile                 ! A general filename

! -- Communications files

        character (len=200) :: mreadfle='pest.rdy'
        character (len=200) :: sreadfle='pslave.rdy'
        character (len=200) :: preadfle='param.rdy'
        character (len=200) :: oreadfle='observ.rdy'
        character (len=200) :: sfinfle='pslave.fin'
        character (len=200) :: testfle='p###.##'
        character (len=200) :: stopfile='pest.stp'

! -- Error message strings

        character (len=500) :: amessage=' '
        character (len=300) :: amessage1=' '
        character (len=300) :: amessage2=' '

! -- Time variales

        character (len=11)  :: result                ! Time string obtained using prm_getsecs subroutine

! -- SUBROUTINES

! -- Visible subroutines.

      public prm_initialise,             &
             prm_slavedat,               &
             prm_slavetest,              &
             prm_doruns,                 &
             prm_set_slave_runtime,      &
             prm_get_slave_runtime,      &
             prm_set_time_refresh_flag,  &
             prm_set_fac_rerun,          &
             prm_get_message_strings,    &
             prm_finalise,               &
             prm_slavestop

contains


  subroutine prm_initialise(ifail,prm_mr_in,prm_mf_in,prm_wk_in,prm_nr_in,nslave_in,maxrun_in,iwait_in,repeatrun_in)

! -- Subroutine PRM_INITIALISE receives data for initialisation of the parallel run manager module.

          implicit none

          integer, intent(out)           :: ifail                ! returned as zero unless an error
          integer, intent(in)            :: prm_mr_in
          integer, intent(in)            :: prm_mf_in
          integer, intent(in)            :: prm_wk_in
          integer, intent(in)            :: prm_nr_in
          integer, intent(in)            :: nslave_in
          integer, intent(in)            :: maxrun_in
          integer, intent(in)            :: iwait_in
          integer, intent(in)            :: repeatrun_in

          logical             :: lopened
          integer             :: ierr,jfail,itemp
          character (len=20)  :: avar,atemp

          ifail=0

! -- Values are assigned to module variables.

          prm_mr=prm_mr_in
          prm_mf=prm_mf_in
          prm_wk=prm_wk_in
          prm_nr=prm_nr_in
          nslave=nslave_in
          maxrun=maxrun_in
          iwait=iwait_in
          repeatrun=repeatrun_in

! -- Input variables are checked for legal values.

          if(prm_mr.le.0)then
            avar='PRM_MR'
            go to 9000
          end if
          if(prm_mf.le.0)then
            avar='PRM_MF'
            go to 9000
          end if
          if(prm_wk.le.0)then
            avar='PRM_WK'
            go to 9000
          end if
          if(prm_nr.lt.0) prm_nr=0
          if(nslave.le.0) then
            avar='NSLAVE'
            go to 9000
          end if
          if(maxrun.le.0)then
            avar='MAXRUN'
            go to 9000
          end if
          if(iwait.le.0)then
            avar='IWAIT'
            go to 9000
          end if
          if((repeatrun.ne.0).and.(repeatrun.ne.1))then
            avar='REPEATRUN'
            go to 9000
          end if

! -- Tests are made regarding unit number usage.

          inquire(unit=prm_mr,opened=lopened)
          if(.not.lopened)then
            call prm_writint(atemp,prm_mr)
            write(amessage,10) trim(atemp)
10          format('Parallel run record file that uses unit number ',a,' should be opened before ',  &
            'subroutine PRM_INITIALISE is called.')
            go to 9890
          end if
          inquire(unit=prm_mf,opened=lopened)
          if(lopened)then
            call prm_writint(atemp,prm_mf)
            write(amessage,20) trim(atemp)
20          format('Error in subroutine PRM_INITIALISE: unit number ',a,' should not be opened in calling program. ', &
            'This must be reserved for messaging files used by PARALLEL_RUN_MANAGER module.')
            go to 9890
          end if
          inquire(unit=prm_wk,opened=lopened)
          if(lopened)then
            call prm_writint(atemp,prm_wk)
            write(amessage,30) trim(atemp)
30          format('Error in subroutine PRM_INITIALISE: unit number ',a,' should not be opened in calling program. ', &
            'This must be reserved for file manipulation undertaken by PARALLEL_RUN_MANAGER module.')
            go to 9890
          end if
          if(prm_nr.gt.0)then
            inquire(unit=prm_nr,opened=lopened)
            if(.not.lopened)then
              call prm_writint(atemp,prm_nr)
              write(amessage,40) trim(atemp)
40            format('Parallel run completion record file that uses unit number ',a,' should be opened ', &
              'before subroutine PRM_INITIALISE is called.')
              go to 9890
            end if
          end if

! -- Arrays are allocated.

          allocate(idet(nslave),iruntme(nslave),jrun(nslave),istats(nslave),istrtme(nslave),stat=ierr)
          if(ierr.ne.0) go to 9200

          allocate(aslave(nslave),asldir(nslave),scom(nslave),stat=ierr)
          if(ierr.ne.0) go to 9200

          allocate(istatr(maxrun),itrial(maxrun),stat=ierr)
          if(ierr.ne.0) go to 9200

! -- Arrays are initialised

          idet=0
          iruntme=0
          jrun=0
          istats=0
          istrtme=0

          aslave=' '
          asldir=' '
          scom=' '

          istatr=0
          itrial=0

! -- An existent stopfile is deleted if present.

          call prm_delfile(jfail,-prm_mf,stopfile)
          if(jfail.ne.0)then
            write(amessage,110) trim(stopfile)
110         format('Cannot delete stop message file ',a,'.')
            go to 9890
          end if

! -- The GETSECS subroutine is initialised.

          call prm_getsecs(itemp,1)

          return

9000      write(amessage,9010) trim(avar)
9010      format('Illegal value supplied for ',a,' variable to subroutine PRM_INITIALISE.')
          go to 9890

9200      write(amessage,9210)
9210      format('Cannot allocate sufficient memory to continue execution.')
          go to 9890

9890      ifail=1

          return

  end subroutine prm_initialise



  subroutine prm_slavedat(ifail,islave,iruntme_in,aslave_in,asldir_in)

! -- Subroutine PRM_SLAVEDAT receives data for an individual slave.

        implicit none

        integer, intent(out) :: ifail
        integer, intent(in)  :: islave
        integer, intent(in)  :: iruntme_in
        character (len=*), intent(in)  :: aslave_in
        character (len=*), intent(in)  :: asldir_in

        integer   :: n
        character (len=20)   :: avar,anum

        ifail=0
        if((islave.le.0).or.(islave.gt.nslave))then
          write(amessage,10)
10        format('Value for ISLAVE supplied to subroutine PRM_SLAVEDAT is out ',  &
          'of range.')
          go to 9890
        end if

! -- A check is made of the data.

        if(aslave_in.eq.' ')then
          avar='ASLAVE'
          go to 9000
        end if
        if(asldir_in.eq.' ')then
          avar='ASLDIR'
          go to 9000
        end if
        if(iruntme_in.le.0)then
          write(amessage,20)
20        format('Illegal value supplied for IRUNTME variable to subroutine PRM_SLAVEDAT.')
          go to 9890
        end if

        aslave(islave)=aslave_in
        asldir(islave)=asldir_in
        iruntme(islave)=iruntme_in

! -- The data undergo a small amount of processing.

        n=len_trim(asldir(islave))
#ifdef UNIX
        if(asldir(islave)(n:n).ne.'/')then
          n=n+1
          asldir(islave)(n:n)='/'
#else
        if(asldir(islave)(n:n).ne.'\')then
          n=n+1
          asldir(islave)(n:n)='\'
#endif
        end if

        return

9000    call prm_writint(anum,islave)
        write(amessage,9010) trim(avar),trim(anum)
9010    format('Blank value supplied to subroutine PRM_SLAVEDAT for ',a,' variable ', &
        'for slave number ',a,'.')
        go to 9890

9890    ifail=1
        return

  end subroutine prm_slavedat



  subroutine prm_set_time_refresh_flag(ifail,time_refresh_flag_in)

! -- Subroutine PRM_SET_TIME_REFRESH_FLAG sets the flag to update model run times on
!    completion of the first model run in the next call to DORUNS.

     integer, intent(out)      :: ifail
     logical, intent(in)       :: time_refresh_flag_in

     ifail=0
     time_refresh_flag=time_refresh_flag_in

     return

  end subroutine prm_set_time_refresh_flag



  subroutine prm_set_fac_rerun(ifail,fac_rerun_in)

! -- Subroutine PRM_SET_FAC_RERUN is used to re-set the factor through which model
!    run times are deemed to be high enough to be worth being replaced by another run.

     integer, intent(out)          :: ifail
     double precision, intent(in)  :: fac_rerun_in

     ifail=0
     if(fac_rerun_in.le.1.0d0)then
       write(amessage,10)
10     format('Error in subroutine PRM_SET_FAC_RERUN. The value supplied for FAC_RERUN ',   &
       'must be greater than 1.0.')
       ifail=1
       return
     end if
     fac_rerun=fac_rerun_in

     return

  end subroutine prm_set_fac_rerun



  subroutine prm_get_slave_runtime(ifail,islave,iruntime_out)

! -- Subroutine PRM_GET_SLAVE_RUNTIME gets the run time for a slave.

        implicit none

        integer, intent(out) :: ifail
        integer, intent(in)  :: islave
        integer, intent(out) :: iruntime_out

        ifail=0
        if((islave.le.0).or.(islave.gt.nslave))then
          write(amessage,10)
10        format('Value for ISLAVE supplied to subroutine PRM_GET_SLAVE_RUNTIME is out ',  &
          'of range.')
          go to 9890
        end if

        iruntime_out=iruntme(islave)
        return

9890    ifail=1
        return

   end subroutine prm_get_slave_runtime



   subroutine prm_set_slave_runtime(ifail,islave,iruntime_in)

! -- Subroutine PRM_SET_SLAVE_RUNTIME sets the run time for a slave.

        implicit none

        integer, intent(out) :: ifail
        integer, intent(in)  :: islave
        integer, intent(in)  :: iruntime_in

        ifail=0
        if((islave.le.0).or.(islave.gt.nslave))then
          write(amessage,10)
10        format('Value for ISLAVE supplied to subroutine PRM_SET_SLAVE_RUNTIME is out ',  &
          'of range.')
          go to 9890
        end if

        iruntme(islave)=iruntime_in
        return

9890    ifail=1
        return

   end subroutine prm_set_slave_runtime





  subroutine prm_slavetest(ifail)

! -- Subroutine PRM_SLAVETEST tests for the presence of slaves and records data to the run management file.

       use model_input_output_interface
       implicit none

       integer, intent(out)    :: ifail

       integer            :: islave,ncount,iflag,iiwait,n,ndet,iitemp,istop,i
       integer            :: numerr,ierr,jfail
       integer            :: template_status,instruction_status,ninfle,noutfl
       character (len=1)  :: aa
       character (len=10) :: atemp

       ifail=0
       slavetest=1
       iiwait=iwait

! -- We make sure that enough mio processing has been done.

       call mio_get_status(template_status,instruction_status)
       if(template_status.eq.0)then
         write(amessage,10)
10       format('Subroutine MIO_PROCESS_TEMPLATE_FILES must be called before subroutine PRM_SLAVETEST is called.')
         go to 9890
       end if
       if(instruction_status.eq.0)then
         write(amessage,15)
15       format('Subroutine MIO_STORE_INSTRUCTION_SET must be called before subroutine PRM_SLAVETEST is called.')
         go to 9890
       end if

! -- And that data has been provided for all slaves.

       do islave=1,nslave
         if(iruntme(islave).eq.0)then
           call writint(atemp,islave)
           write(amessage,16) trim(atemp)
16         format('Subroutine PRM_SAVETEST must not be called before data has been ', &
           'provided for all slaves through subroutine PRM_SLAVEDAT. This has not be ', &
           'done for slave number ',a,'.')
           go to 9890
         end if
       end do

       ncount=0
       numerr=0
       do islave=1,nslave
         iflag=0
         afile=trim(asldir(islave))//trim(testfle)
         open(unit=prm_mf,file=trim(afile),iostat=ierr)
         if(ierr.ne.0) then
           write(6,150)
150        format(' Run management error:-')
           write(6,160) trim(asldir(islave))
160        format(' Cannot open a file in subdirectory ',a,/)
           numerr=numerr+1
           cycle
         end if
         write(prm_mf,'(a)',iostat=ierr) ' Testing'
         if(ierr.ne.0) then
           write(6,150)
           write(6,170) trim(asldir(islave))
170        format(' Cannot write to a file in subdirectory ',a,/)
           numerr=numerr+1
           iflag=1
           close(unit=prm_mf,iostat=ierr)
           cycle
         end if
         close(unit=prm_mf,iostat=ierr)
         if(ierr.ne.0) then
           write(6,150)
           write(6,190) trim(asldir(islave))
190        format(' Cannot close a file in subdirectory ',a,/)
           go to 9000
         end if
         afile=trim(asldir(islave))//trim(testfle)
         open(unit=prm_mf,file=trim(afile),status='old',iostat=ierr)
         if(ierr.ne.0) then
           write(6,150)
           write(6,160) trim(asldir(islave))
           numerr=numerr+1
           cycle
         end if
         read(prm_mf,'(a)',iostat=ierr) aa
         if(ierr.ne.0) then
           write(6,150)
           write(6,210) trim(asldir(islave))
210        format(' Cannot read from a file in subdirectory ',a,/)
           numerr=numerr+1
           iflag=1
           close(unit=prm_mf,iostat=ierr)
           cycle
         end if
         close(unit=prm_mf,iostat=ierr)
         if(ierr.ne.0) then
           write(6,150)
           write(6,190) trim(asldir(islave))
           go to 9000
         end if
         if(iflag.eq.0) ncount=ncount+1
       end do
       if(ncount.eq.0) go to 9000

! -- Some data is written to the run management record file.

       write(prm_mr,220)
220    format(t30,'RUN MANAGEMENT RECORD')
       write(prm_mr,20)
20     format(/,' SLAVE DETAILS:-',/)
       write(prm_mr,50)
50     format(' Slave Name',t40,'PSLAVE Working Directory')
       write(prm_mr,55)
55    format(' ----------',t40,'------------------------')
       do islave=1,nslave
         write(prm_mr,60)trim(aslave(islave)(1:38)),trim(asldir(islave))
60       format(' "',a,'"',t40,a)
       end do
       write(prm_mr,110)
110    format(/,/,' Attempting to communicate with slaves ....',/)
#ifdef FLUSHFILE
       call flush(prm_mr)
#endif

! -- Next we see if the slaves have started.

       do islave=1,nslave
         afile=trim(asldir(islave))//sreadfle
         call prm_delfile(jfail,-prm_wk,afile)
         if(jfail.ne.0) go to 9300
         afile=trim(asldir(islave))//oreadfle
         call prm_delfile(jfail,-prm_wk,afile)
         if(jfail.ne.0) go to 9300
         afile=trim(asldir(islave))//preadfle
         call prm_delfile(jfail,-prm_wk,afile)
         if(jfail.ne.0) go to 9300
         afile=trim(asldir(islave))//sfinfle
         call prm_delfile(jfail,-prm_wk,afile)
         if(jfail.ne.0) go to 9300
         afile=trim(asldir(islave))//mreadfle
         call prm_open_new_message_file(ierr,prm_mf,afile)
         if(ierr.eq.0)then
           write(prm_mf,'(i10)',err=9200) iwait
#ifdef UNIX
#ifdef UNICOS
           rewind(unit=prm_mf)
           write(prm_mf,'(i10)',err=9200) iwait
#endif
#endif
           call prm_closefile(jfail,prm_mf,2,afile)
           if(jfail.ne.0) go to 9400
         end if
       end do

       call prm_wait(iiwait)
       call prm_wait(iiwait)

520    continue
       write(6,525)
525    format(' Testing whether slaves are alive .....',/)
       n=0
       ndet=0
530    do islave=1,nslave
         if(idet(islave).eq.0) then
           afile=trim(asldir(islave))//sreadfle
           call prm_open_existing_message_file(ierr,prm_mf,afile)
           if(ierr.eq.0)then
             read(prm_mf,'(a)') scom(islave)
             call prm_closefile(jfail,prm_mf,2,afile)
             if(jfail.ne.0) go to 9400
             write(6,550) trim(aslave(islave))
550          format(' - slave "',a,'" has been detected.')
             write(prm_mr,550) trim(aslave(islave))
             idet(islave)=1
             ndet=ndet+1
             afile=trim(asldir(islave))//mreadfle
             call prm_open_new_message_file(ierr,prm_mf,afile)
             write(prm_mf,'(i10)',err=9200) iwait
#ifdef UNIX
#ifdef UNICOS
             rewind(unit=prm_mf)
             write(prm_mf,'(i10)',err=9200) iwait
#endif
#endif
             call prm_closefile(jfail,prm_mf,2,afile)
             if(jfail.ne.0) go to 9400
           end if
         end if
       end do
#ifdef FLUSHFILE
       call flush(prm_mr)
#endif

! -- Has a stop condition been encountered?

       call prm_stopress(prm_wk,istop)
       if(istop.ne.0)then
         ifail=-istop
         return
       end if

       if(ndet.lt.nslave) then
         n=n+1
         if(n.gt.10) then
           if(ndet.gt.0)then
             call prm_writint(atemp,ndet)
             write(6,630) trim(atemp)
             write(prm_mr,630) trim(atemp)
630          format(/,' Only ',a,' slaves are alive.')
             write(6,640)
             write(prm_mr,640)
640          format(/,' Parallel processing will commence using only these slaves.',/' Others will be used ',   &
             'if/when they become available.')
#ifdef FLUSHFILE
              call flush(prm_mr)
#endif
             write(6,*)
             go to 621
           else
             write(prm_mr,643)
643          format(' No slaves are alive.')
#ifdef FLUSHFILE
              call flush(prm_mr)
#endif
             write(amessage,644)
644          format('No slaves are alive. Start at least one slave and then restart program.')
             go to 9890
           end if
         end if
         iitemp=max(200,iwait*3/nslave)
         call prm_wait(iitemp)
         go to 530
       end if
       write(6,620)
620    format(/,' All slaves are alive.',/)

! -- Names of input and output files on all slaves are now recorded.

621    continue
       call mio_get_dimensions(ninfle,noutfl)
       write(prm_mr,1100)
1100   format(/,/,' SLAVE MODEL INPUT AND OUTPUT FILES:-')
       do islave=1,nslave
         write(prm_mr,1120) trim(aslave(islave))
1120     format(/,' Slave "',a,'" ----->')
         write(prm_mr,1130) trim(aslave(islave))
1130     format(/,'     Model input files on slave "',a,'":-')
         do i=1,ninfle
           call mio_get_file(ifail,2,i,afile)
           afile=trim(asldir(islave))//trim(afile)
           write(prm_mr,1150) trim(afile)
1150       format(t10,a)
         end do
         write(prm_mr,1180) trim(aslave(islave))
1180     format(/,'     Model output files on slave "',a,'":-')
         do i=1,noutfl
           call mio_get_file(ifail,4,i,afile)
           afile=trim(asldir(islave))//trim(afile)
           write(prm_mr,1150) trim(afile)
           call prm_delfile(jfail,-prm_mf,afile)
           if(jfail.ne.0) go to 9890
         end do
         write(prm_mr,1250) trim(aslave(islave))
1250     format(/,'     Model command line for slave "',a,'":-')
         if(scom(islave).eq.' ')then
           write(prm_mr,1252)
1252       format(t10,'unknown')
         else
           write(prm_mr,1251) trim(scom(islave))
1251       format(t10,'"',a,'"')
         end if
         write(prm_mr,*)
       end do
       call prm_writint(atemp,iiwait)
       write(prm_mr,1310) trim(atemp)
1310   format(/,' AVERAGE WAIT INTERVAL         : ',a,' hundredths of a second.')
       if(repeatrun.eq.1)then
         write(prm_mr,1318)
1318     format(' REPEAT TROUBLESOME MODEL RUNS : yes')
       else
         write(prm_mr,1319)
1319     format(' REPEAT TROUBLESOME MODEL RUNS : no')
       end if

       write(prm_mr,1350)
1350   format(/,/,t29,'RUN MANAGEMENT RECORD')

#ifdef FLUSHFILE
       call flush(prm_mr)
#endif

       go to 9999

9000   write(amessage,9010)
9010   format('Conditions are such that that parallel runs cannot take place.')
       go to 9890

9200   write(amessage,9210) trim(afile)
9210   format('Cannot communicate with file ',a,'.')
       go to 9890

9300   write(amessage,9310) trim(afile)
9310   format('File management error: cannot delete file ',a,'.')
       go to 9890

9400   write(amessage,9410) trim(afile)
9410   format('File management error: cannot close file ',a,'.')
       go to 9890

9999   return

9890   ifail=1
       return

  end subroutine prm_slavetest



  subroutine prm_doruns(ifail,itn,npar,nobs,nrun,pregdim,pobsdim,parreg,obsreg,apar,aobs,   &
                      irestart,restartfile,forgive_failure)

! -- Subroutine PRM_DORUNS supervises a number of parallel model runs.

       use model_input_output_interface
       implicit none

       integer, intent(out)    :: ifail
       integer, intent(in)     :: itn
       integer, intent(in)     :: npar
       integer, intent(in)     :: nobs
       integer, intent(in)     :: nrun
       integer, intent(in)     :: pregdim
       integer, intent(in)     :: pobsdim
       integer, intent(in)     :: forgive_failure

       double precision, intent(inout) :: parreg(pregdim,nrun)
       double precision, intent(inout) :: obsreg(pobsdim,nrun)

       character (len=*), intent(in)   :: apar(npar)
       character (len=*), intent(in)   :: aobs(nobs)

       integer, intent(inout), optional        :: irestart
       character (len=*), intent(in), optional :: restartfile

       logical   :: lopened
       integer   :: maxtrial,iiwait,ierr,jj,ii,i,jfail,istop,icount
       integer   :: islave,jslave,jjslave,iirun,irun,jrestart
       integer   :: pitn,titn,ptcount,final
       integer   :: now,resunit,reswritflag,idetect,iproblem
       integer   :: itemp1,itemp2,itemp3,itemp4,itemps
       double precision :: rtemp

       character (len=10)  :: atemp,atemp1,atemp2
       character (len=300) :: instruction

       ifail=0
       maxtrial=3
       pitn=itn

       iiwait=iwait
       iirun=0
       jrestart=0
       reswritflag=0
       resunit=0
       idetect=0
       iproblem=0

       if(slavetest.eq.0)then
         write(amessage,5)
5        format('Subroutine PRM_DORUNS must not be called before subroutine PRM_SLAVETEST is called.')
         go to 9890
       end if

       if(nrun.gt.MAXRUN)then
         write(amessage,7)
7        format('Integer argument NRUN supplied to subroutine PRM_DORUNS exceeds ', &
         'previously-supplied value for MAXRUN.')
         go to 9890
       end if

! -- Initialize some variables.

       do irun=1,nrun
         istatr(irun)=0
         if(repeatrun.eq.1)then
           itrial(irun)=0
         else
           itrial(irun)=maxtrial
         end if
       end do
       do islave=1,nslave
         jrun(islave)=0
       end do

! -- Record situation on run managemenr record file.

       call writint(atemp,itn)
       write(prm_mr,*)
       write(prm_mr,*)
       write(prm_mr,6) trim(atemp)
6      format(' PARALLEL RUN PACKAGE NUMBER ',a,' ---->')
#ifdef FLUSHFILE
       call flush(prm_mr)
#endif
       if(prm_nr.gt.0)then
         if(itn.gt.1)then
           write(prm_nr,*)
           write(prm_nr,*)
         end if
         write(prm_nr,6) trim(atemp)
#ifdef FLUSHFILE
         call flush(prm_nr)
#endif
       end if

! -- The restart file situation is handled

       if(present(irestart))then
         jrestart=irestart
         if((irestart.lt.0).or.(irestart.gt.2))then
           write(amessage,9)
9          format('Error in subroutine PRM_DORUNS. Optional argument IRESTART must be 0, 1 or 2.')
           go to 9890
         end if
         if(irestart.gt.0)then
           if(.not.present(restartfile))then
             write(amessage,10)
10           format('Error in subroutine PRM_DORUNS. If optional argument IRESTART is supplied ', &
             'as positive then optional argument RESTARTFILE must also be supplied.')
             go to 9890
           end if
           if(restartfile.eq.' ')then
             write(amessage,12)
12           format('Error in subroutine PRM_DORUNS. RESTARTFILE argument must not be blank.')
             go to 9890
           end if
           inquire(file=restartfile,opened=lopened)
           if(lopened)then
             write(amessage,13) trim(restartfile)
13           format('Error in subroutine PRM_DORUNS. File supplied as RESTARTFILE ',  &
             'argument (file "',a,'") must not already be opened.')
             go to 9890
           end if
         end if
         resunit=prm_nextunit()
         if(irestart.eq.1)then
           call prm_delfile(jfail,-prm_wk,restartfile)
           open(unit=resunit,file=restartfile,form='unformatted',action='write',iostat=ierr)
           if(ierr.ne.0)then
             write(amessage,14) trim(restartfile)
14           format('Cannot open file ',a,' to store parallel run module restart data.')
             go to 9890
           end if
           write(resunit)pitn
#ifdef FLUSHFILE
           call flush(resunit)
#endif
         else if(irestart.eq.2)then
           ptcount=0
           open(unit=resunit,file=restartfile,form='unformatted',status='old',iostat=ierr)
           if(ierr.ne.0) then
             write(amessage,18) trim(restartfile)
18           format('Cannot open file ',a,' to read restart data.')
             go to 9890
           end if
           titn=0
           read(resunit,iostat=ierr)titn
           if(pitn.ne.titn)then
             call writint(atemp1,pitn)
             call writint(atemp2,titn)
             write(amessage,25) trim(atemp1),trim(restartfile),trim(atemp2)
25           format('Error in subroutine PRM_DORUNS. Restart was requested. However presently requested run ', &
             'package is package number ',a,' whereas restart file ',a,' holds restart data for ', &
             'package number ',a,'.')
             go to 9890
           end if
           itemps=0
           do
             read(resunit,err=1900,end=1900) itemps
             do jj=1,nobs
               obsreg(jj,itemps)=-1.1d300
             end do
             istatr(itemps)=-99
             ptcount=ptcount+1
             read(resunit,err=1900,end=1900)(obsreg(jj,itemps),jj=1,nobs)
           end do
1900       close(unit=resunit,status='delete',iostat=ierr)
           if(itemps.ne.0)then
             do jj=1,nobs
               if(obsreg(jj,itemps).lt.-1.0d300)then
                 ptcount=ptcount-1
                 istatr(itemps)=0
                 go to 1901
               end if
             end do
           end if
1901       continue
2000       continue

           call prm_writint(atemp,ptcount)
           write(6,49) trim(atemp)
49         format(' Results from ',a,' model runs read from restart file.')
           write(6,*)
           write(prm_mr,2010) trim(atemp)
2010       format(3x,'Results from ',a,' model runs read from restart file.')

           reswritflag=1
           jrestart=1
           irestart=1
           iirun=ptcount
           ncall=ncall+ptcount
           open(unit=resunit,file=restartfile,form='unformatted',action='write',iostat=ierr)
           if(ierr.ne.0)then
             write(amessage,2011)
2011         format('Cannot open file ',a,' to store restart data for new model runs.')
             go to 9890
           end if
           write(resunit,iostat=ierr)pitn
           if(ptcount.ne.0)then
             do i=1,nrun
               if(istatr(i).eq.-99)then
                 write(resunit,iostat=ierr)i
                 write(resunit,iostat=ierr)(obsreg(jj,i),jj=1,nobs)
               end if
             end do
           end if
#ifdef FLUSHFILE
           call flush(resunit)
#endif
           if(ptcount.eq.nrun) go to 9999
         end if
       end if

50     continue

! -- See if any new slaves have appeared.

       do islave=1,nslave
	 if(idet(islave).eq.0) then
	   afile=trim(asldir(islave))//sreadfle
           call prm_open_existing_message_file(ierr,prm_mf,afile)
           if(ierr.eq.0)then
             read(prm_mf,'(a)') scom(islave)
             call prm_closefile(jfail,prm_mf,2,afile)
             if(jfail.ne.0) go to 9500
             write(prm_mr,750) result,trim(aslave(islave))
750          format(3x,a,':- slave "',a,'" has just been detected.')
#ifdef FLUSHFILE
             call flush(prm_mr)
#endif
             write(6,751) trim(aslave(islave))
751          format(/,' Slave "',a,'" has just been detected.')
             idetect=1
             idet(islave)=1
             afile=trim(asldir(islave))//mreadfle
             call prm_open_new_message_file(ierr,prm_mf,afile)
             write(prm_mf,'(i10)',err=9400) iwait
#ifdef UNIX
#ifdef UNICOS
             rewind(unit=prm_mf)
             write(prm_mf,'(i10)',err=9400) iwait
#endif
#endif
             call prm_closefile(jfail,prm_mf,2,afile)
             if(jfail.ne.0) go to 9500

             afile=trim(asldir(islave))//oreadfle
             call prm_open_existing_message_file(ierr,prm_wk,afile)
             if(ierr.eq.0)then
               call prm_closefile(jfail,prm_wk,2,afile)
               if(jfail.ne.0) go to 9500
               call prm_wait(iiwait)
               call prm_delfile(jfail,prm_wk,afile)
               if(jfail.ne.0) go to 9890
             end if

           end if
	 end if
       end do

! -- Have any slaves from lost runs or re-started slaves re-appeared?

       do islave=1,nslave
         if(istats(islave).eq.-999)then
           afile=trim(asldir(islave))//sreadfle
           call prm_open_existing_message_file(ierr,prm_mf,afile)
           if(ierr.eq.0)then
             read(prm_mf,'(a)') scom(islave)
             call prm_closefile(jfail,prm_mf,2,afile)
             if(jfail.ne.0) go to 9500
             afile=trim(asldir(islave))//mreadfle
             call prm_open_new_message_file(ierr,prm_mf,afile)
             write(prm_mf,'(i10)',err=9400) iwait
#ifdef UNIX
#ifdef UNICOS
             rewind(unit=prm_mf)
             write(prm_mf,'(i10)',err=9400) iwait
#endif
#endif
             call prm_closefile(jfail,prm_mf,2,afile)
             if(jfail.ne.0) go to 9500
             afile=trim(asldir(islave))//oreadfle
             call prm_delfile(jfail,-prm_wk,afile)
             if(jfail.ne.0) go to 9890
             write(prm_mr,753) result,trim(aslave(islave))
753          format(3x,a,':- slave "',a,'" has just reappeared.')
#ifdef FLUSHFILE
             call flush(prm_mr)
#endif
             write(6,754) trim(aslave(islave))
754          format(/,' Slave "',a,'" has just reappeared.')
             idetect=1
             istats(islave)=0
           end if
	 end if
       end do

! -- See whether a stop file exists.

       call prm_stopress(prm_wk,istop)
       if((istop.eq.2).or.(istop.eq.1)) then
         if(jrestart.ne.0) close(unit=resunit,iostat=ierr)
         ifail=-istop
         return
       end if

! -- See if it is time to try any "frozen" slaves again.

       do islave=1,nslave
         if(idet(islave).eq.0) cycle
         if(istats(islave).eq.150) then
           call prm_getsecs(now,0)
           if(now-istrtme(islave).gt.30)then   ! 30 seconds
             istats(islave)=0
           end if
         end if
       end do

! -- Look for the fastest free slave.

151    continue
       itemp2=0
       do islave=1,nslave
         if(idet(islave).eq.0) cycle
         if(istats(islave).eq.0) then
           itemp2=itemp2+1
           if(itemp2.eq.1) then
             itemp1=iruntme(islave)
             jjslave=islave
           else
             if(iruntme(islave).lt.itemp1)then
               itemp1=iruntme(islave)
               jjslave=islave
             end if
           end if
         end if
       end do
       if(itemp2.ne.0)then
         islave=jjslave

! -- First we make sure that the observation flag file has been deleted.

         afile=trim(asldir(islave))//oreadfle
         call prm_open_existing_message_file(ierr,prm_wk,afile)
         if(ierr.eq.0)then
           call prm_closefile(jfail,prm_wk,2,afile)
           if(jfail.ne.0) go to 9500
           call prm_wait(iiwait)
           call prm_delfile(jfail,prm_wk,afile)
           if(jfail.ne.0) go to 9890
           go to 9300
         end if
         go to 1000
       end if

! -- See if any runs are complete.

210    do islave=1,nslave
         if(idet(islave).eq.0) cycle
         afile=trim(asldir(islave))//oreadfle
         call prm_open_existing_message_file(ierr,prm_wk,afile)
         if(ierr.eq.0)then
           call prm_closefile(jfail,prm_wk,2,afile)
           if(jfail.ne.0) go to 9500
           call prm_wait(iiwait)
           call prm_delfile(jfail,prm_wk,afile)
           if(jfail.ne.0) go to 9890
           call prm_getsecs(now,0)
           if(istats(islave).eq.150) cycle
           if(istats(islave).eq.-999) then !doing a run left over from before
             write(prm_mr,220,err=9900) result,trim(aslave(islave))
220	     format(3x,a,':- slave "',a,'" finished execution; old run so results not needed.')
#ifdef FLUSHFILE
             call flush(prm_mr)
#endif
             go to 250
           end if
           if(jrun(islave).eq.0) then
             call prm_getsecs(now,0)
             write(prm_mr,9310) result,trim(aslave(islave))
#ifdef FLUSHFILE
             call flush(prm_mr)
#endif
             go to 500
           end if
           if(istatr(jrun(islave)).eq.-99) then  !already downloaded
             write(prm_mr,230,err=9900) result,trim(aslave(islave))
230          format(3x,a,':- slave "',a,'" finished execution; same run already completed by another slave.')
#ifdef FLUSHFILE
             call flush(prm_mr)
#endif
             go to 250
           end if
           write(prm_mr,240,err=9900) result,trim(aslave(islave))
240        format(3x,a,':- slave "',a,'" finished execution; reading results.')
#ifdef FLUSHFILE
           call flush(prm_mr)
#endif
           ncall=ncall+1
           if(repeatrun.eq.1)then
             final=0
           else
             final=1
           end if
           icount=0
245        continue
           amessage=' '
           call mio_read_model_output_files(jfail,nobs,aobs,obsreg(1,jrun(islave)),instruction,asldir(islave))
           if(jfail.ne.0) then
             if(forgive_failure.eq.1)then
               obsreg(1,jrun(islave))=1.234d300
               write(prm_mr,2491,err=9900) result,trim(aslave(islave))
2491           format(3x,a,':- model run failure on slave "',a,'". Failure is ignored.')
#ifdef FLUSHFILE
               call flush(prm_mr)
#endif
               go to 2471
             end if
             icount=icount+1
             if(icount.gt.2)then
               if(instruction.ne.' ') then
                 call mio_get_message_string(jfail,amessage)
                 amessage1='Instruction line follows:'
                 amessage2=instruction
                 go to 9890                 
               else
                 itrial(jrun(islave))=itrial(jrun(islave))+1
                 if(itrial(jrun(islave)).gt.maxtrial) then
                   call mio_get_message_string(jfail,amessage)
                   go to 9890
                 end if
                 istats(islave)=0
                 istatr(jrun(islave))=0
                 call prm_getsecs(now,0)
	         write(6,251,err=9900)trim(aslave(islave))
251	         format(/,' Problem encountered in reading results of run on slave "',  &
                 a,'".',/,' Will carry out run again.',/)
                 iproblem=1
                 write(prm_mr,249,err=9900) result,trim(aslave(islave))
249              format(3x,a,':- problems continuing with run on slave "',a,'". Will run model again.')
#ifdef FLUSHFILE
                 call flush(prm_mr)
#endif
                 go to 50
               end if
             end if
             call prm_getsecs(now,0)
             write(prm_mr,247,err=9900) result,trim(aslave(islave))
247          format(3x,a,':- problem (either model or communications) in reading results from slave "',a,'".')
#ifdef FLUSHFILE
             call flush(prm_mr)
#endif
             do ii=1,6
               call prm_wait(200)
               call prm_stopress(prm_wk,istop)
               if((istop.eq.2).or.(istop.eq.1)) then
                 if(jrestart.ne.0) close(unit=resunit,iostat=ierr)
                 ifail=-istop
                 return
               end if
             end do
             go to 245
	   end if
2471       continue	   
           istatr(jrun(islave))=-99
           iirun=iirun+1
           itemps=jrun(islave)
           if(jrestart.ne.0)then
             write(resunit,iostat=ierr) itemps
             write(resunit,iostat=ierr) (obsreg(jj,itemps),jj=1,nobs)
#ifdef FLUSHFILE
             call flush(resunit)
#endif              
           end if
           call prm_writint(atemp,iirun)
           if(prm_nr.ne.0)then
             write(prm_nr,254) trim(atemp)
254          format('    ',a,' model runs completed.')
#ifdef FLUSHFILE
             call flush(prm_nr)
#endif
           end if
           if((iirun.eq.1).or.(reswritflag.eq.1).or.(idetect.eq.1).or.(iproblem.eq.1))then
             write(6,256)
256          format(' - number of runs completed...')
             write(6,'(a)',advance='no') '   '
             reswritflag=0
             idetect=0
             iproblem=0
           end if
           write(6,257,advance='no') iirun
257        format(i6)
           if((iirun.eq.nrun).or.(mod(iirun,12).eq.0))then
             write(6,*)
             write(6,'(a)',advance='no') '   '
           end if
250        continue
           itemp1=iruntme(islave)
           iruntme(islave)=now-istrtme(islave)
           if(iruntme(islave).le.0) iruntme(islave)=1
           istats(islave)=0

! -- If this is the first parallel call, all estimated run times are upgraded.

260        continue
           if((ncall.eq.1).or.(time_refresh_flag))then
             time_refresh_flag=.false.
             do jslave=1,nslave
               if(islave.ne.jslave)then
                 iruntme(jslave)=iruntme(jslave)*float(iruntme(islave))/float(itemp1)
	         if(iruntme(jslave).le.0) iruntme(jslave)=1
               end if
             end do
           end if
           do irun=1,nrun                       !jan 2005
             if(istatr(irun).eq.0) go to 151
           end do
           do irun=1,nrun
             if(istatr(irun).gt.-99) go to 500   ! used to be 50
           end do
           go to 9000
         end if
500    continue
       end do

       call prm_wait(iiwait)
       go to 50

! -- If a slave is free and there is a run to do we give the slave that run.

1000   continue

       do irun=1,nrun
         if(istatr(irun).eq.0) then
           call prm_getsecs(istrtme(islave),0)
           write(prm_mr,1070) result,trim(aslave(islave))
1070       format(3x,a,':- slave "',a,'" commencing model run.')
#ifdef FLUSHFILE
           call flush(prm_mr)
#endif
           call mio_write_model_input_files(jfail,npar,apar,parreg(1,irun),asldir(islave))
           if(jfail.ne.0) then
             call mio_get_message_string(jfail,amessage)
             go to 9890
           end if
           call prm_wait(iiwait)
           call mio_delete_output_files(jfail,asldir(islave))
           if(ifail.ne.0)then
             call mio_get_message_string(jfail,amessage)
             go to 9890
           end if
           call prm_wait(iiwait)

           afile=trim(asldir(islave))//preadfle
           call prm_open_new_message_file(ierr,prm_mf,afile)
           write(prm_mf,1050,err=9199)
1050       format('P')
           call prm_closefile(jfail,prm_mf,2,afile)
           if(jfail.ne.0) go to 9500
           istatr(irun)=99
           istats(islave)=99
           jrun(islave)=irun
           go to 50
         end if
       end do

! -- There is a slave free. Can we redo a run on a faster machine?

       call prm_getsecs(now,0)
       itemp3=0
       jjslave=0
       do jslave=1,nslave
         if(idet(jslave).eq.0) cycle
         if(jslave.eq.islave) cycle
         if(istats(jslave).ne.99) cycle
         itemp4=istrtme(jslave)+iruntme(jslave)
         if(itemp4.gt.itemp3)then
           itemp3=itemp4
           jjslave=jslave
         end if
       end do
       if(jjslave.eq.0) go to 1500
       itemp3=itemp3-now
       if(itemp3.lt.2) go to 1500		! too small to worry about
       if(float(itemp3).gt.fac_rerun*float(iruntme(islave)))then
         irun=jrun(jjslave)
         istrtme(islave)=now
         write(prm_mr,1230) result,trim(aslave(islave)),trim(aslave(jjslave))
1230     format(3x,a,':- slave "',a,'" commencing model run because it can ',   &
         'complete it before slave "',a,'".')
#ifdef FLUSHFILE
         call flush(prm_mr)
#endif
         call mio_write_model_input_files(jfail,npar,apar,parreg(1,irun),asldir(islave))
         if(jfail.ne.0) then
           call mio_get_message_string(jfail,amessage)
           go to 9890
         end if
         call prm_wait(iiwait)
         call mio_delete_output_files(ifail,asldir(islave))
         if(ifail.ne.0)then
           call mio_get_message_string(jfail,amessage)
           go to 9890
         end if
         call prm_wait(iiwait)

         afile=trim(asldir(islave))//preadfle
         call prm_open_new_message_file(ierr,prm_mf,afile)
         write(prm_mf,1050,err=9199)
         call prm_closefile(jfail,prm_mf,2,afile)
         if(jfail.ne.0) go to 9500
         istatr(irun)=99
         istats(islave)=99
         jrun(islave)=irun
         istats(jjslave)=100			!so only one slave does it
         go to 210
       end if

! -- Are any runs overdue?

1500   continue
       itemp3=0
       jjslave=0
       do jslave=1,nslave
         if(idet(jslave).eq.0) cycle
         if(jslave.eq.islave) cycle
         if(istats(jslave).ne.99) cycle
         itemp4=istrtme(jslave)+iruntme(jslave)-now
         if(itemp4.lt.itemp3) then
           itemp3=itemp4
           jjslave=jslave
         end if
       end do
       rtemp=-(fac_rerun-1.0d0)
       if((jjslave.eq.0).or.(float(itemp3).gt.rtemp*float(iruntme(islave)))) then
         go to 210
       end if
       irun=jrun(jjslave)
       istrtme(islave)=now
       write(prm_mr,1520) result,trim(aslave(islave)),trim(aslave(jjslave))
1520   format(3x,a,':- slave "',a,'" commencing model run because slave "',a,'" is overdue.')
#ifdef FLUSHFILE
       call flush(prm_mr)
#endif
       call mio_write_model_input_files(jfail,npar,apar,parreg(1,irun),asldir(islave))
       if(jfail.ne.0) then
         call mio_get_message_string(jfail,amessage)
         go to 9890
       end if
       call prm_wait(iiwait)
       call mio_delete_output_files(ifail,asldir(islave))
       if(ifail.ne.0)then
         call mio_get_message_string(jfail,amessage)
         go to 9890
       end if
       call prm_wait(iiwait)

       afile=trim(asldir(islave))//preadfle
       call prm_open_new_message_file(ierr,prm_mf,afile)
       write(prm_mf,1050,err=9199)
       call prm_closefile(jfail,prm_mf,2,afile)
       if(jfail.ne.0) go to 9500
       istatr(irun)=99
       istats(islave)=99
       jrun(islave)=irun
       istats(jjslave)=100		!so only one slave does it
       go to 210

! -- Before returning we re-assign the status of incompleted runs.
! -- Also, the signal files are deleted. If they re-appear PEST will
!    use these slaves again.

9000   do islave=1,nslave
         if(idet(islave).eq.0) cycle
         if((istats(islave).eq.99).or.(istats(islave).eq.100))then
           afile=trim(asldir(islave))//sreadfle
           call prm_delfile(jfail,-prm_wk,afile)
           if(jfail.ne.0) go to 9890
           istats(islave)=-999
         end if
       end do
       go to 9999

9199   call prm_closefile(jfail,prm_mf,0,afile)
       if(jfail.ne.0) go to 9500

9200   call prm_getsecs(istrtme(islave),0)
       write(prm_mr,9210) result,trim(aslave(islave))
9210   format(3x,a,':- cannot write to slave "',a,'" to commence model run.')
#ifdef FLUSHFILE
       call flush(prm_mr)
#endif
       istats(islave)=150
       go to 50

9300   call prm_getsecs(istrtme(islave),0)
       write(prm_mr,9310) result,trim(aslave(islave))
9310   format(3x,a,':- previous observ.rdy file on slave "',a,'" not deleted.')
#ifdef FLUSHFILE
       call flush(prm_mr)
#endif
       istats(islave)=150
       go to 50

9400   write(amessage,9410) trim(afile)
9410   format('Cannot communicate with file ',a,'.')
       go to 9890

9500   write(amessage,9510) trim(afile)
9510   format('Cannot close file ',a,'.')
       go to 9890

9900   call prm_writint(atemp,prm_mr)
       write(amessage,9910) trim(atemp)
9910   format('Cannot write to run management record file on unit number ',a,'.')
       go to 9890

9890   ifail=1

9999   continue
       if((jrestart.eq.1).or.(jrestart.eq.2)) then
         if(resunit.ne.0) close(unit=resunit,iostat=ierr)
       end if
       return

  end subroutine prm_doruns



  subroutine prm_finalise(ifail)

! -- Subroutine PRM_FINALISE deallocates arrays used by the parallel run management module.

       integer, intent(out)  :: ifail

       integer               :: ierr

       ifail=0

! -- Memory is deallated.

       if(allocated(idet)) deallocate(idet,stat=ierr)
       if(allocated(idet)) deallocate(iruntme,stat=ierr)
       if(allocated(idet)) deallocate(jrun,stat=ierr)
       if(allocated(idet)) deallocate(istats,stat=ierr)
       if(allocated(idet)) deallocate(istrtme,stat=ierr)
       if(allocated(idet)) deallocate(aslave,stat=ierr)
       if(allocated(idet)) deallocate(asldir,stat=ierr)
       if(allocated(idet)) deallocate(scom,stat=ierr)
       if(allocated(idet)) deallocate(istatr,stat=ierr)
       if(allocated(idet)) deallocate(itrial,stat=ierr)

       return

  end subroutine prm_finalise


  subroutine prm_slavestop(ifail)

! -- Subroutine PRM_SLAVESTOP sends a message to slaves to shut them down.

        integer, intent(out)   :: ifail

        integer :: i,ierr

        ifail=0

        do i=1,nslave
          afile=trim(asldir(i))//trim(sfinfle)
          call prm_open_new_message_file(ierr,prm_mf,afile)
          if(ierr.eq.0)then
            write(prm_mf,'(a)',err=9000) 'F'
#ifdef UNIX
#ifdef UNICOS
            rewind(unit=prm_mf)
            write(prm_mf,'(a)',err=9000) 'F'
#endif
#endif
10          call prm_closefile(ierr,prm_mf,2,afile)
            if(ierr.ne.0) go to 9000
          end if
        end do

        return

9000    ifail=1
        write(amessage,9010)
9010    format('Could not send message to slaves to stop them.')
        return

  end subroutine prm_slavestop




  subroutine prm_get_message_strings(ifail,numused,amessage_out,suppl_amessage_out)

! -- Subroutine PRM_GET_MESSAGE_STRINGS copies the PRM message strings into user-defined strings.

       integer, intent(out)                         :: ifail
       integer, intent(out)                         :: numused
       character (len=*), intent(out)               :: amessage_out
       character (len=*), dimension(:),intent(out)  :: suppl_amessage_out

       integer                                :: n

       ifail=0
       if(amessage2.ne.' ')then
         numused=3
       else
         if(amessage1.ne.' ')then
           numused=2
         else
           if(amessage.ne.' ')then
             numused=1
           else
             numused=0
           end if
         end if
       end if

       amessage_out=amessage
       n=size(suppl_amessage_out)
       if(n.ge.1)then
         suppl_amessage_out(1)=amessage1
       end if
       if(n.ge.2)then
         suppl_amessage_out(2)=amessage2
       end if

       return

  end subroutine prm_get_message_strings



  subroutine prm_open_existing_message_file(ierr,iunit,afile)

! -- Subroutine PRM_OPEN_EXISTING_MESSAGE_FILE opens a message file.

       implicit none
       integer, intent(out)  :: ierr
       integer, intent(in)   :: iunit
       character (len=*)     :: afile

#ifdef UNIX
       open(unit=iunit,file=trim(afile),status='old',iostat=ierr)
#else
#ifdef LF90
       open(unit=iunit,file=trim(afile),action='readwrite,denynone',status='old',blocksize=1,iostat=ierr)
#else
       open(unit=iunit,file=trim(afile),blocksize=1,status='old',iostat=ierr)
#endif
#endif

       return

  end subroutine prm_open_existing_message_file




  subroutine prm_open_new_message_file(ierr,iunit,afile)

! -- Subroutine PRM_OPEN_NEW_MESSAGE_FILE opens a new message file.

        implicit none

        integer, intent(out)   :: ierr
        integer, intent(in)    :: iunit
        character (len=*)      :: afile


#ifdef UNIX
        open(unit=iunit,file=trim(afile),iostat=ierr)
#else
#ifdef LF90
        open(unit=iunit,file=trim(afile),action='readwrite,denynone',blocksize=1,iostat=ierr)
#else
        open(unit=iunit,file=trim(afile),blocksize=1,iostat=ierr)
#endif
#endif

        return

  end subroutine prm_open_new_message_file




  subroutine prm_closefile(jfail,iunit,istatus,afile)

       implicit none

       logical lopened
       integer iunit,icount,ierr,istatus,iiwait,jfail
       character*(*) afile

       jfail=0
       iiwait=iwait
       if(istatus.eq.2) go to 90
       inquire(unit=iunit,opened=lopened)
       if(.not.lopened) return
90     icount=0
100    icount=icount+1
       close(unit=iunit,iostat=ierr)
       if(ierr.ne.0) then
         if(icount.gt.20) then
           write(amessage,110) trim(afile)
110        format('Cannot close file ',a,'.')
           go to 9890
         end if
         call prm_wait(iiwait)
         go to 100
       end if

       return

9890   jfail=1
       return

  end subroutine prm_closefile



  subroutine prm_delfile(jfail,iunit,afile)

       implicit none

       logical lexist
       integer iunit,icount,junit,ierr,iiwait,itemp,jfail
       integer unlink
       character*(*) afile

       jfail=0
       iiwait=iwait
       junit=iunit
       if(iunit.lt.0)then
         inquire(file=trim(afile),exist=lexist)
         if(.not.lexist) then
           return
         end if
         junit=-junit
       end if
       icount=0
#ifdef UNIX
10     itemp=unlink(trim(afile))
#else
10     call system('del "'//trim(afile)//'" > nul')
#endif
       call prm_wait(iiwait)
!!!       if(iunit.lt.-500) return      ! We may need to reinstate this.
!#ifdef UNIX
!       open(unit=junit,file=trim(afile),status='old',iostat=ierr)
!#else
!#ifdef LF90
!       open(unit=junit,file=trim(afile),action='readwrite,denynone',status='old',  &
!       blocksize=1,iostat=ierr)
!#else
!       open(unit=junit,file=trim(afile),status='old',blocksize=1,iostat=ierr)
!#endif
!#endif
!       if(ierr.ne.0) return
!       call prm_wait(iiwait)
!       call prm_closefile(jfail,junit,2,afile)
!       if(jfail.ne.0) go to 9890

        inquire(file=trim(afile),exist=lexist)
        if(.not.lexist) then
          return
        end if

       icount=icount+1
       if(icount.gt.10)then
         write(amessage,12) trim(afile)
12       format('Cannot delete file ',a,'.')
         go to 9890
       end if
       call prm_wait(iiwait)
       go to 10

9890   jfail=1
       return

  end subroutine prm_delfile


  subroutine prm_getsecs(isecs,init)

        implicit none

        integer isecs,mm,dd,yy,hh,min,m1,d1,y1,h1,min1,ndays,init
        real ss,ss1
        character*11 result1,result2

        call date_and_time(date=result1,time=result2)
        read(result1,'(i4,i2,i2)') yy,mm,dd
        read(result2,'(i2,i2,f6.0)') hh,min,ss
        write(result,'(i2.2,'':'',i2.2,'':'',f5.2)') hh,min,ss
        if(init.eq.0) then
          ndays=prm_numdays(prm_d1,prm_m1,prm_y1,dd,mm,yy)
          isecs=ndays*86400+(hh-prm_h1)*3600+(min-prm_min1)*60+ss-prm_s1
        else
          prm_m1=mm
          prm_d1=dd
          prm_y1=yy
          prm_h1=hh
          prm_min1=min
          prm_s1=ss
        end if

        return

  end subroutine prm_getsecs




  subroutine prm_wait(nsec)

! -- Subroutine PRM_WAIT hangs around for NSECS hundredths of a second.

        implicit none

#ifdef SLEEP
        integer nsec,msec
        msec=nsec/100
        if(msec.lt.1)msec=1
        call sleep(msec)
#else
        integer ddate(8),iticks,iticks1,nsec
        call date_and_time(values=ddate)
        iticks=ddate(5)*360000+ddate(6)*6000+ddate(7)*100+ddate(8)/10
10      call date_and_time(values=ddate)
        iticks1=ddate(5)*360000+ddate(6)*6000+ddate(7)*100+ddate(8)/10
        if(iticks1.lt.iticks) iticks1=iticks1+8640000
        if(iticks1.lt.iticks+nsec) go to 10
#endif

        return

  end subroutine prm_wait


  subroutine prm_stopress(iunit,istop)

        implicit none

        integer ipause,iunit,ierr,istop
        integer*4 reason

        ipause=0
10      continue

        reason=0
        istop=0
        open(unit=iunit,file=stopfile,status='old',err=5)
        read(iunit,*,err=6,end=6) reason
6       continue
        if(reason.ne.3)then
          close(unit=iunit,status='delete',err=5)
        else
          close(unit=iunit,err=5)
        end if
5       continue

        if(reason.eq.3)then
          if(ipause.eq.0)then
            write(6,20)
20          format(/,' Program execution has been PAUSED...')
            ipause=1
          end if
          call prm_wait(100)
          go to 10
        else if((reason.eq.1).or.(reason.eq.2))then
          istop=reason
        else
          if(ipause.eq.1)then
            write(6,30)
30          format(' Program execution has been UNPAUSED.',/)
          end if
        end if
        return

  end subroutine prm_stopress


  integer function prm_numdays(DR,MR,YR,D,M,Y)

        implicit none

! -- Function prm_numdays calculates the number of days between dates
!    D-M-Y and DR-MR-YR. If the former preceeds the latter the answer is
!    negative.

! -- Arguments are as follows:-
!       dr,mr,yr:     days, months and years of first date
!       d,m,y:        days, months and years of second date
!       prm_numdays returns the number of elapsed days


        integer, intent(in) :: dr,mr,yr
        integer, intent(in) :: d,m,y

        integer flag,i,j,da(12),ye,me,de,yl,ml,dl

        data da /31,28,31,30,31,30,31,31,30,31,30,31/

! --    The smaller of the two dates is now chosen to do the counting from.

        if(y.lt.yr)go to 10
        if((y.eq.yr).and.(m.lt.mr)) go to 10
        if((y.eq.yr).and.(m.eq.mr).and.(d.lt.dr)) go to 10
        flag=0
        ye=yr
        me=mr
        de=dr
        yl=y
        ml=m
        dl=d
        go to 20
10      flag=1
        ye=y
        me=m
        de=d
        yl=yr
        ml=mr
        dl=dr

! --    In the above the postscript "e" stands for earlier date, while
!       "l" stands for the later date.

20      prm_numdays=0
        if((me.eq.ml).and.(yl.eq.ye))then
        prm_numdays=dl-de
        if(flag.eq.1) prm_numdays=-prm_numdays
        return
        end if

        do 30 j=me,12
        if((ml.eq.j).and.(ye.eq.yl))goto 40
        prm_numdays=prm_numdays+da(j)
        if((j.eq.2).and.(prm_leap(ye)))prm_numdays=prm_numdays+1
30      continue
        go to 50
40      prm_numdays=prm_numdays+dl-de
        if(flag.eq.1)prm_numdays=-prm_numdays
        return

50      do 60 i=ye+1,yl
        do 70 j=1,12
        if((yl.eq.i).and.(ml.eq.j))go to 80
        prm_numdays=prm_numdays+da(j)
        if((j.eq.2).and.(prm_leap(i))) prm_numdays=prm_numdays+1
70      continue
60      continue
        write(6,65)
65      format(/,' Error in subroutine prm_numdays')
        stop
        return

80      prm_numdays=prm_numdays+dl-de
        if(flag.eq.1) prm_numdays=-prm_numdays

        return

  end function prm_numdays



  logical function prm_leap(year)

! -- Function PRM_LEAP returns .true. if a year is a leap year.


        integer, intent(in)  ::  year

        prm_leap = ( mod(year,4).eq.0 .and. mod(year,100).ne.0 ) .or.( mod(year,400).eq.0 .and. year.ne.0 )

        return

   end function prm_leap


  subroutine prm_writint(atemp,ival)

!       Subroutine WRITINT writes an integer to a character variable.

        integer*4 ival
        character*6 afmt
        character*(*) atemp

        afmt='(i   )'
        write(afmt(3:5),'(i3)') len(atemp)
        write(atemp,afmt)ival
        atemp=adjustl(atemp)
        return

  end subroutine prm_writint

  integer function prm_nextunit()

! -- Function PRM_NEXTUNIT determines the lowest unit number available for
! -- opening.

        logical::lopen

        do prm_nextunit=10,100
          inquire(unit=prm_nextunit,opened=lopen)
          if(.not.lopen) return
        end do
        write(6,10)
10      format(' *** No more unit numbers to open files ***')
        stop

end function prm_nextunit

end module parallel_run_manager


