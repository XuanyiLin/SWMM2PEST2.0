      program cppp

! -- Program CPPP is a basic c pre-processor.

      implicit none
      integer, parameter :: MAXOPT=50,MAXDEEP=50
      integer i,iopt,ifile,nb,nopt,iblock,jcopy,ierr,iline
      integer icopy(MAXDEEP)
      character*20 option(MAXOPT),ablock
      character*200 infile,outfile
      character*500 cline

! -- Initialisation

      infile=' '
      outfile=' '
      iopt=0
      ifile=0
      iline=0

! -- The command line is parsed.

      call pgetcl(cline)
      write(6,*) trim(cline)              ! debug

10    continue
      cline=adjustl(cline)
      nb=len_trim(cline)
      if(nb.eq.0) go to 100
      do i=1,nb
        if(cline(i:i).ne.' ') go to 50
      end do
      go to 100
50    continue
!      write(6,*) trim(cline)          ! debug
      if(cline(1:1).eq.'-')then
        if(cline(2:2).ne.'D')then
          write(6,20) cline(1:2)
20        format(/,' *** Unknown switch ',a,' ***',/)
          stop
        end if
        cline=cline(3:)
        if((cline(1:1).eq.' ').or.(cline(1:1).eq.char(9)))then
          write(6,25)
25        format(/,' *** Blank follows -D switch on command line ***',/)
          stop
        end if
        nb=len_trim(cline)
        do i=1,nb
          if((cline(i:i).eq.' ').or.(cline(i:i).eq.char(9))) go to 30
        end do
        i=nb+1
30      i=i-1
        iopt=iopt+1
        option(iopt)=cline(1:i)
        cline=cline(i+1:)
      else
        nb=len_trim(cline)
        do i=1,nb
          if((cline(i:i).eq.' ').or.(cline(i:i).eq.char(9))) go to 40
        end do
        i=nb+1
40      i=i-1
        ifile=ifile+1
        if(ifile.gt.2)then
          write(6,45)
45        format(/,' *** Too many files cited on command line ***',/)
          stop
        end if
        if(ifile.eq.1)then
          infile=cline(1:i)
        else
          outfile=cline(1:i)
        end if
        cline=cline(i+1:)
      end if

      go to 10

100   if((infile.eq.' ').or.(outfile.eq.' '))then
        write(6,110)
110     format(/,' *** Two filenames expected on command line ***',/)
        stop
      end if

      nopt=iopt

      do iopt=1,nopt
        write(6,*) trim(option(iopt))
      end do
!      write(6,*) trim(infile)
!      write(6,*) trim(outfile)

! -- The input file is read and output file is written.

       open(unit=10,file=infile,iostat=ierr)
       if(ierr.ne.0)then
         write(6,140) trim(infile)
140      format(/,' *** Cannot open file ',a,' ***',/)
         stop
       end if
       open(unit=20,file=outfile)

       iblock=0
       jcopy=1
       do
         iline=iline+1
         read(10,'(a)',end=1000) cline
         if(cline(1:1).ne.'#')then
           if(jcopy.eq.1) write(20,'(a)') trim(cline)
         else
           if((cline(1:6).eq.'#ifdef').or.(cline(1:7).eq.'#ifndef'))then
             iblock=iblock+1
             if(cline(1:6).eq.'#ifdef')then
               ablock=cline(7:)
             else
               ablock=cline(8:)
             end if
             ablock=adjustl(ablock)
             i=index(ablock,' ')
             if(i.gt.1)then
               ablock=ablock(1:i-1)
             end if
             if(cline(1:6).eq.'#ifdef')then
               if(nopt.gt.0)then
                 do iopt=1,nopt
                   if(ablock.eq.option(iopt)) then
                     icopy(iblock)=1
                     go to 150
                   end if
                 end do
                 icopy(iblock)=0
150              continue
               else
                 icopy(iblock)=0
               end if
             else
               if(nopt.gt.0)then
                 do iopt=1,nopt
                   if(ablock.eq.option(iopt)) go to 170
                 end do
                 icopy(iblock)=1
                 go to 180
170              icopy(iblock)=0
180              continue
               else
                 icopy(iblock)=1
               end if
             end if
!             write(6,*) icopy(1),ablock, option(1)   !debug
           else if(cline(1:5).eq.'#else')then
             if(iblock.le.0)then
               write(6,154) iline,trim(infile)
154            format(/,' *** Unexpected #else at line',i5,
     +         ' of file ',a,' ***',/)
               go to 9900
             end if
             icopy(iblock)=1-icopy(iblock)
           else if(cline(1:6).eq.'#endif')then
             iblock=iblock-1
             if(iblock.lt.0)then
               write(6,155) iline,trim(infile)
155            format(/,' *** Unexpected #endif at line',i5,
     +         ' of file ',a,' ***',/)
               go to 9900
             end if
           else if(cline(1:7).eq.'#define')then
             if(jcopy.eq.1) write(20,'(a)') trim(cline)
           else if(cline(1:8).eq.'#include')then
             if(jcopy.eq.1) write(20,'(a)') trim(cline)           
           else
             write(6,171) iline,trim(infile)
171          format(/,' *** Unknown directive at line',i5,
     +       ' of file ',a,' ***',/)
             go to 9900
           end if
           jcopy=1
           if(iblock.gt.0)then
             do i=1,iblock
               if(icopy(i).eq.0) jcopy=0
             end do
           end if
         end if
       end do

1000   continue
       go to 9999

9900   continue
       close(unit=10,iostat=ierr)
       close(unit=20,status='delete',iostat=ierr)

9999   end


        SUBROUTINE TABREM(CLINE)
 
C -- Subroutine TABREM removes tabs from a string.
 
        INTEGER I
        CHARACTER*(*) CLINE
 
        DO 10 I=1,LEN(CLINE)
10      IF(ICHAR(CLINE(I:I)).EQ.9) CLINE(I:I)=' '
 
        RETURN
        END

      
             
        SUBROUTINE PGETCL(COMLIN)

        CHARACTER*(*) COMLIN
        INTEGER IARGC
        INTEGER LLEN,NARG,IB,I,NB,IBB
        CHARACTER*120 ARG(15)

        LLEN=LEN(COMLIN)
        NARG=IARGC()
        COMLIN=' '
        IF(NARG.EQ.0) RETURN
        IB=0
        DO 100 I=1,MIN(NARG,15)
          CALL GETARG(I,ARG(I))
          NB=LEN_TRIM(ARG(I))
          IBB=MIN(IB+NB+1,LLEN)
          COMLIN(IB+1:IBB)= ARG(I)(1:NB)
          IB=IBB
          IF(IB.GE.LLEN)RETURN
100     CONTINUE
        RETURN
        END
