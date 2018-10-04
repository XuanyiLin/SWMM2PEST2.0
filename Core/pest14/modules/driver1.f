program driver1

! -- Program DRIVER1 demonstrates use of the MIO module.

       use model_input_output_interface
       implicit none

       integer   :: npar,nobs,ntempfile,ninsfile,i,ifail,n1,n2
       integer   :: template_status,instruction_status
       double precision, allocatable :: parval(:),obsval(:)
       character*200   :: infile,comline,outfile
       character*300   :: instruction
       character*500   :: amessage

       character*12, allocatable  :: apar(:)
       character*20, allocatable  :: aobs(:)
       character*200, allocatable :: tempfile(:),modinfile(:)
       character*200, allocatable :: insfile(:),modoutfile(:)

#ifndef UNIX
#ifdef LAHEY
       open(unit=*,action='read',carriagecontrol='list')
#endif
#endif

! -- Initialisation.

       instruction=' '

! -- The input file is opened.

100    write(6,110,advance='no')
110    format(' Enter name of DRIVER1 input file: ')
       read(5,*) infile
       open(unit=10,file=infile,status='old',err=100)

! -- And now read.

       read(10,*)
       read(10,*) npar,nobs
       allocate(apar(npar),parval(npar))
       allocate(aobs(nobs),obsval(nobs))
       read(10,*) ntempfile,ninsfile
       allocate(tempfile(ntempfile),modinfile(ntempfile))
       allocate(insfile(ninsfile),modoutfile(ninsfile))
       read(10,*)
       do i=1,npar
         read(10,*) apar(i),parval(i)
         call lowcase(apar(i))
       end do
       read(10,*)
       do i=1,nobs
         read(10,*) aobs(i)
       end do
       read(10,*)
       read(10,*) comline
       read(10,*)
       do i=1,ntempfile
         read(10,*) tempfile(i),modinfile(i)
       end do
       do i=1,ninsfile
         read(10,*) insfile(i),modoutfile(i)
       end do
       close(unit=10)
       write(6,200) trim(infile)
200    format(' - file ',a,' read ok.')

! -- The output file is opened.

       write(6,*)
300    write(6,310,advance='no')
310    format(' Enter name for output file: ')
       read(5,*) outfile
       open(unit=20,file=outfile)

! -- MIO initialisation

       call mio_initialise(ifail,ntempfile,ninsfile,npar,nobs)
       if(ifail.ne.0) go to 9000

! -- Dimensions are recorded.

       write(6,*)
       call mio_get_dimensions(n1,n2)
       write(6,240) n1
240    format(' Number of template files    = ',i3)
       write(6,250) n2
250    format(' Number of instruction files = ',i3)

! -- MIO filename storage

       do i=1,ntempfile
         call mio_put_file(ifail,1,i,tempfile(i))
         if(ifail.ne.0) go to 9000
         call mio_put_file(ifail,2,i,modinfile(i))
         if(ifail.ne.0) go to 9000
       end do
       do i=1,ninsfile
         call mio_put_file(ifail,3,i,insfile(i))
         if(ifail.ne.0) go to 9000
         call mio_put_file(ifail,4,i,modoutfile(i))
         if(ifail.ne.0) go to 9000
       end do

! -- Status is acquired.

       write(6,*)
       call mio_get_status(template_status,instruction_status)
       write(6,260) template_status
260    format(' Template status    = ',i2)
       write(6,270) instruction_status
270    format(' Instruction status = ',i2)

! -- Template file processing

       call mio_process_template_files(ifail,npar,apar)
       if(ifail.ne.0) go to 9000

! -- Instruction file processing

       call mio_store_instruction_set(ifail)
       if(ifail.ne.0) go to 9000

! -- Status is acquired.

       write(6,*)
       call mio_get_status(template_status,instruction_status)
       write(6,260) template_status
       write(6,270) instruction_status

! -- Model output files are deleted.

       call mio_delete_output_files(ifail)
       if(ifail.ne.0) go to 9000

! -- Model input files are written.

       call  mio_write_model_input_files(ifail,npar,apar,parval)
       if(ifail.ne.0) go to 9000

! -- The model is run.

       call system(comline)

! -- Model output files are read.

       call mio_read_model_output_files(ifail,nobs,aobs,obsval,instruction)
       if(ifail.ne.0) go to 9000

! -- The DRIVER1 output file is written.

       write(20,470)
470    format(' Parameter values')
       do i=1,npar
         write(20,400) trim(apar(i)),parval(i)
       end do
       write(20,480)
480    format(/,' Observation values')
       do i=1,nobs
         write(20,400) trim(aobs(i)),obsval(i)
400      format(2x,a,t25,1pg14.7)
       end do
       write(6,500) trim(outfile)
500    format(/,' - model output file ',a,' written ok.')

       go to 9900

9000   call mio_get_message_string(ifail,amessage)
       write(6,*)
       amessage=' '//amessage
       call writmess(6,amessage)
       if(instruction.ne.' ')then
         write(6,9010)
9010     format(' Instruction follows:-')
         write(6,9020) trim(instruction)
9020     format(1x,a)
       end if


9900   call mio_finalise(ifail)

end program driver1


subroutine writmess(iunit,amessage)

! -- Subroutine WRITMESS writes an error message.

        implicit none

	integer iunit,jend,i,nblc,junit,leadblank,itake,j
        character*(*) amessage
	character (len=20) ablank

	ablank=' '
	itake=0
	j=0
	junit=iunit

        if(amessage.eq.' ')then
          write(junit,*)
          return
        end if
        write(junit,*)
	do i=1,min(20,len(amessage))
	  if(amessage(i:i).ne.' ')go to 21
20      end do
21	leadblank=i-1
	nblc=len_trim(amessage)
5       jend=j+78-itake
	if(jend.ge.nblc) go to 100
	do i=jend,j+1,-1
	if(amessage(i:i).eq.' ') then
	  if(itake.eq.0) then
	     write(junit,'(a)') amessage(j+1:i)
	     itake=2+leadblank
	  else
	     write(junit,'(a)') ablank(1:leadblank+2)//amessage(j+1:i)
	  end if
	  j=i
	  go to 5
	end if
	end do
	if(itake.eq.0)then
	  write(junit,'(a)') amessage(j+1:jend)
	  itake=2+leadblank
	else
	  write(junit,'(a)') ablank(1:leadblank+2)//amessage(j+1:jend)
	end if
	j=jend
	go to 5
100     jend=nblc
	if(itake.eq.0)then
	  write(junit,'(a)') amessage(j+1:jend)
	else
	  write(junit,'(a)') ablank(1:leadblank+2)//amessage(j+1:jend)
	end if
	return

end subroutine writmess



subroutine lowcase(astrng)

! -- Subroutine LOWCAS converts a string to lower case.

        integer i,j
        character*(*) astrng

        do 10 i=1,len_trim(astrng)
        j=ichar(astrng(i:i))
        if((j.ge.65).and.(j.le.90)) astrng(i:i)=char(j+32)
10      continue
        return

end subroutine lowcase
