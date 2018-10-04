program driver2

! -- Program DRIVER2 demonstrates use the MIO and PRM modules.

       use parallel_run_manager
       use model_input_output_interface
       implicit none

       integer   :: npar,nobs,ntempfile,ninsfile,i,ifail,n1,n2,ierr
       integer   :: template_status,instruction_status
       integer   :: nslave,itemp,iwait,repeatrun,numused,itn,nitn,irun,nrun
       integer   :: maxrun,pregdim,pobsdim,irestart,failure_forgive
       integer   :: lw(5),rw(5)
       integer, allocatable :: iruntme(:)
       double precision     :: wait
       double precision, allocatable :: parreg(:,:),obsreg(:,:)
       character*12   :: aapar
       character*20   :: atemp
       character*200  :: infile,comline,restartfile,obsfile
       character*300  :: instruction
       character*500  :: amessage,cline
       character*500  :: suppl_amessage(2)

       character*12, allocatable  :: apar(:)
       character*20, allocatable  :: aobs(:)
       character*200, allocatable :: tempfile(:),modinfile(:)
       character*200, allocatable :: insfile(:),modoutfile(:)
       character*200, allocatable :: aslave(:),asldir(:)


#ifndef UNIX
#ifdef LAHEY
       open(unit=*,action='read',carriagecontrol='list')
#endif
#endif

! -- Read command line argument.

       comline=' '
       irestart=1
       call pgetcl(comline)
       call lowcase(comline)
       if(comline.eq.'/r')then
         irestart=2
       else if(comline.eq.' ')then
         irestart=1
       else
         write(amessage,10)
10       format('Unrecognised command line.')
         go to 9800
       end if

! -- Initialisation.

       instruction=' '
       maxrun=10
       failure_forgive=0

! -- The input file is opened.

100    write(6,110,advance='no')
110    format(' Enter name of DRIVER2 input file: ')
       read(5,*) infile
       open(unit=10,file=infile,status='old',err=100)

! -- And now read.

       read(10,*)
       read(10,*) npar,nobs
       allocate(apar(npar),aobs(nobs))
       read(10,*) ntempfile,ninsfile
       allocate(tempfile(ntempfile),modinfile(ntempfile))
       allocate(insfile(ninsfile),modoutfile(ninsfile))
       read(10,*)
       do i=1,npar
         read(10,*) apar(i)
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

       write(6,*)
510    write(6,520,advance='no')
520    format(' Enter name of run management file: ')
       read(5,*,err=510) infile
       open(unit=10,file=infile,status='old',err=510)
       read(10,*)
       read(10,*) nslave,itemp,wait,itemp,repeatrun
       iwait=nint(wait*100)
       allocate(aslave(nslave),asldir(nslave),iruntme(nslave))
       do i=1,nslave
         read(10,'(a)') cline
         call linesplit(ifail,2,lw,rw,cline)
         aslave(i)=cline(lw(1):rw(1))
         asldir(i)=cline(lw(2):rw(2))
       end do
       read(10,*) (iruntme(i),i=1,nslave)
       close(unit=10)
       write(6,200) trim(infile)

! -- MIO initialisation

       call mio_initialise(ifail,ntempfile,ninsfile,npar,nobs)
       if(ifail.ne.0) go to 9000

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

! -- Template file processing

       call mio_process_template_files(ifail,npar,apar)
       if(ifail.ne.0) go to 9000

! -- Instruction file processing

       call mio_store_instruction_set(ifail)
       if(ifail.ne.0) go to 9000

! -- The parallel run record is opened.

       open(unit=30,file='driver2.rmr')

! -- The parallel run completion record is opened.

       open(unit=33,file='model.runs')

       write(6,*)

! -- PRM is initialised.

       call prm_initialise(ifail,30,31,32,33,nslave,maxrun,iwait,repeatrun)
       if(ifail.ne.0) go to 9100

! -- PRM slave data is stored.

       do i=1,nslave
         call prm_slavedat(ifail,i,iruntme(i),aslave(i),asldir(i))
         if(ifail.ne.0) go to 9100
       end do

! -- We test for the presence of slaves.

       call prm_slavetest(ifail)
       if(ifail.ne.0) then
         if(ifail.gt.0) then
           go to 9100
         else
           go to 9200
         end if
       end if

! -- Parallel runs are carried out.

       pregdim=npar
       allocate(parreg(pregdim,maxrun))
       pobsdim=nobs
       allocate(obsreg(pobsdim,maxrun))

590    write(6,591,advance='no')
591    format(' How many run packages do you wish to implement? ')
       read(5,*,err=590) nitn
       do itn=1,nitn
         write(6,*)
         call writint(atemp,itn)
600      write(6,610,advance='no') trim(atemp)
610      format(' Enter name for parameter value file for run package ',a,': ')
         read(5,*,err=600) infile
         open(unit=10,file=infile,status='old',err=600)
         read(10,*) nrun
         if(nrun.gt.maxrun)then
           write(amessage,640)
640        format('Increase MAXRUN and re-compile DRIVER2 program.')
           go to 9800
         end if
         do i=1,npar
           read(10,*) aapar, (parreg(i,irun),irun=1,nrun)
           call lowcase(aapar)
           if(aapar.ne.apar(i))then
             write(amessage,642) trim(infile)
642          format('Parameter values are incorrect, or are supplied in the wrong order, in file ',a,'.')
             go to 9800
           end if
         end do
         close(unit=10)
         write(6,650) trim(infile)
650      format(' - file ',a,' read ok.')

620      write(6,630,advance='no') trim(atemp)
630      format(' Enter name for observation output file for run package ',a,': ')
         read(5,*,err=620) obsfile
         open(unit=25,file=obsfile,err=620)
         write(6,660)
660      format(' - carrying out parallelised model runs...')
         write(6,*)
         call prm_doruns(ifail,itn,npar,nobs,nrun,pregdim,pobsdim,parreg,obsreg,apar,aobs,    &
         irestart,'driver2.res',failure_forgive)
         if(ifail.ne.0) then
           if(ifail.gt.0) then
             go to 9100
           else
             go to 9200
           end if
         end if
         write(25,665)
665      format(' Parameter values ---->')
         do i=1,npar
           write(25,670) trim(apar(i)),(parreg(i,irun),irun=1,nrun)
         end do
         write(25,666)
666      format(/,' Model output values ---->')
         do i=1,nobs
           write(25,670) trim(aobs(i)),(obsreg(i,irun),irun=1,nrun)
670        format(1x,a,t22,100(1x,1pg14.7))
         end do
         write(6,*)
         write(6,680) trim(obsfile)
680      format(' - file ',a,' written ok.')
         close(unit=25)
       end do

       write(6,690)
690    format(/,' Shutting down slaves...')
       call prm_slavestop(ifail)

       go to 9900

9000   call mio_get_message_string(ifail,amessage)
       amessage=' '//amessage
       call writmess(6,amessage)
       if(instruction.ne.' ')then
         write(6,9010)
9010     format(' Instruction follows:-')
         write(6,9020) trim(instruction)
9020     format(1x,a)
       end if
       go to 9900

9100   call prm_get_message_strings(ifail,numused,amessage,suppl_amessage)
       amessage=' '//amessage
       call writmess(6,amessage)
       if(numused.gt.1)then
         write(6,9020) trim(suppl_amessage(1))
         write(6,9020) trim(suppl_amessage(2))
       end if
       go to 9900

9200   write(6,9210)
9210   format(/,' Processing has been terminated by user.')
       write(6,9220) -ifail
9220   format(' ISTOP = ',i1)
       go to 9900

9800   amessage=' '//amessage
       call writmess(6,amessage)
       go to 9900


9900   call mio_finalise(ifail)
       call prm_finalise(ifail)


       deallocate(aslave,asldir,iruntme,stat=ierr)
       deallocate(iruntme,parreg,obsreg,stat=ierr)
       deallocate(apar,aobs,tempfile,modinfile,insfile,modoutfile,aslave,asldir,stat=ierr)

end program driver2


subroutine writmess(iunit,amessage)

! -- Program WRITMESS writes an error message string.

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


subroutine linesplit(ifail,num,lw,rw,cline)
 
! -- Subroutine LINESPLIT splits a string into blank-delimited fragments.
 
        integer ifail,nw,nblc,j,i
        integer num,nblnk
        integer lw(num),rw(num)
        character*(*) cline
 
        ifail=0
        nw=0
        nblc=len_trim(cline)
        if((nblc.ne.0).and.(index(cline,char(9)).ne.0)) then
          call tabrem(cline)
          nblc=len_trim(cline)
        endif
        if(nblc.eq.0) then
          ifail=-1
          return
        end if
        j=0
5       if(nw.eq.num) return
        do 10 i=j+1,nblc
          if((cline(i:i).ne.' ').and.(cline(i:i).ne.',').and.(ichar(cline(i:i)).ne.9)) go to 20
10      continue
        ifail=1
        return
20      nw=nw+1
        lw(nw)=i
        do 30 i=lw(nw)+1,nblc
          if((cline(i:i).eq.' ').or.(cline(i:i).eq.',').or.(ichar(cline(i:i)).eq.9)) go to 40
30      continue
        rw(nw)=nblc
        if(nw.lt.num) ifail=1
        return
40      rw(nw)=i-1
        j=rw(nw)
        go to 5
 
end subroutine linesplit
 
 
subroutine tabrem(cline)
 
! -- Subroutine TABREM removes tabs from a string.
 
        integer i
        character*(*) cline
 
        do 10 i=1,len(cline)
10      if(ichar(cline(i:i)).eq.9) cline(i:i)=' '
 
        return

end subroutine tabrem


subroutine writint(atemp,ival)

! --    Subroutine WRITINT writes an integer to a character variable.

        integer*4 ival
        character*6 afmt
        character*(*) atemp

        afmt='(i   )'
        write(afmt(3:5),'(i3)') len(atemp)
        write(atemp,afmt)ival
        atemp=adjustl(atemp)
        return

end subroutine writint



#ifdef LAHEY

subroutine pgetcl(comlin)

        character comlin*(*)

        call getcl(comlin)
        return

end subroutine pgetcl
#else

subroutine pgetcl(comlin)

        character*(*) comlin
        integer iargc
        integer llen,narg,ib,i,nb,ibb
        character*120 arg(4)

        llen=len(comlin)
        narg=iargc()
        comlin=' '
        if(narg.eq.0) return
        ib=0
        do 100 i=1,min(narg,4)
          call getarg(i,arg(i))
          nb=len_trim(arg(i))
          ibb=min(ib+nb+1,llen)
          comlin(ib+1:ibb)= arg(i)(1:nb)
          ib=ibb
          if(ib.ge.llen)return
100     continue
        return

end subroutine pgetcl

#endif

