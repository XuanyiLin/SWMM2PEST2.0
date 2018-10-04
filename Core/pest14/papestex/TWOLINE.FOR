	program twoline

	integer*4 i,nx
	real*4 s1,s2,y1,xc
	real*4 x(50),y(50)

	write(6,10)
10	format(/,' Program TWOLINE. Watermark Computing')
	write(6,20)
20	format(/,' Reading model input file IN.DAT....')

	open(unit=20,file='in.dat')

c	read the line parameters

	read(20,*) s1,s2
	read(20,*) y1
	read(20,*) xc

c	read the abscissae at which there are measurement values

	read(20,*) nx
	do 100 i=1,nx
	read(20,*) x(i)
100	continue
	close(unit=20)
	write(6,110)
110	format(' File IN.DAT read ok.')

c	evaluate y for each x

	do 200 i=1,nx
	if(x(i).le.xc) then
	  y(i)=s1*x(i)+y1
	else
	  y(i)=s2*x(i)+(s1-s2)*xc+y1
	end if
200	continue

c	write the y values to the output file


	write(6,220)
220	format(/,' Writing model output file OUT.DAT...')
	open(unit=20,file='out.dat')
	do 300 i=1,nx
	write(20,*) x(i),y(i)
300	continue
	close(unit=20)
	write(6,320)
320	format(' File OUT.DAT written ok.')

	end

