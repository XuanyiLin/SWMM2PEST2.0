
        program polymod

        implicit none
        integer numx,i,j
        real xx,a,b,c,d,prediction
        real x(200),jacob(200,4),oval(200),predictder(4)

C -- The abscissae at which polynomial evaluations are required are first read.

	open(unit=10,file='poly_x.in',status='old')
	read(10,*) numx
	do 20 i=1,numx
	  read(10,*) x(i)
20	continue
	close(unit=10)

C -- Next the parameter values are read.

        open(unit=10,file='poly_par.in',status='old')
        read(10,*) a,b,c,d
        close(unit=10)

C -- Polynomial calculations are made.

	do 50 i=1,numx
	  xx=x(i)
	  oval(i)=
     +    a*xx*xx*xx+b*xx*xx+c*xx+d

c	note: the programmer is aware that this is a dumb way to calculate
c	      the value of a polynomial on a computer because it makes
c	      the ground fertile for build-up of numerical errors. However,
c             it makes the role of the parameters clear.

50	continue


C -- Derivative calculations are made.

	do 150 i=1,numx
          xx=x(i)
	    jacob(i,1)=xx*xx*xx
150	continue
	do 160 i=1,numx
          xx=x(i)
          jacob(i,2)=xx*xx
160	continue
        do 170 i=1,numx
          xx=x(i)
          jacob(i,3)=xx
170     continue
        do 180 i=1,numx
          jacob(i,4)=1
180     continue

C -- Now calculations are made for the predictive component.

	prediction=1.0*a+2.0*b+3.0*c+4.0*d
        predictder(1)=1.0
        predictder(2)=2.0
        predictder(3)=3.0
        predictder(4)=4.0

C -- The "model output file" is written.

        open(unit=20,file='poly_val.out')
        do 200 i=1,numx
          write(20,*) oval(i)
200     continue
        write(20,*) prediction
        close(unit=20)

C -- Next the derivatives file is written.

        open(unit=20,file='poly_der.out')
        write(20,*) 4,numx+1
        do 220 j=1,numx
          write(20,*) (jacob(j,i),i=1,4)
220     continue
        write(20,*) (predictder(i),i=1,4)
        close(unit=20)


	end



