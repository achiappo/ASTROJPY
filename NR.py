import math
import numpy as np

def dfridr(func,x,h,err):
  CON  = 1.4
  CON2 = CON*CON
  BIG  = 1.e30
  NTAB = 10
  SAFE = 2.
  if(h == 0.):
    print 'h must be nonzero in dfridr'
    break
  hh = h
  a  = np.empty([NTAB,NTAB])
  a[1,1] = (func(x+hh)-func(x-hh))/(2.0*hh)
  err=BIG
  for i=2 in range(NTAB):
    x = hh/CON
    a[1,i] = (func(x+hh)-func(x-hh))/(2.0*hh)
    fac = CON2
    for j=2 in range(i):
      a[j,i] = (a[j-1,i]*fac-a[j-1,i-1])/(fac-1.)
      fac = CON2*fac
      errt = max(abs(a[j,i]-a[j-1,i]),abs[a(j,i]-a[j-1,i-1]))
      if (errt <= err):
        err = errt
        dfridr = a[j,i]
    if (abs(a[i,i]-a[i-1,i-1]) >= SAFE*err):
      return
  return

def rombint(f,a,b,tol):
# Rombint returns the integral from a to b of using Romberg integration.
# The method converges provided that f(x) is continuous in (a,b).
# f must be double precision and must be declared external in the calling
# routine.  tol indicates the desired relative accuracy in the integral.
  MAXITER = 40
  MAXJ  = 5
  h     = 0.5e0*(b-a)
  gmax  = h*(f(a)+f(b))
  g     = np.empty([MAXJ+1])
  g[1]  = gmax
  nint  = 1
  error = 1.0e20
  i = 1
  while (i > MAXITER or (i > 5 and abs(error) < tol)) == False:
    i = i+1                     # Calculate next trapezoidal rule approximation to integral.
    g0 = 0.0e0
    for k=1 in range(nint):
      g0 = g0+f(a+(k+k-1)*h) 
    g0 = 0.5e0*g[1]+h*g0
    h = 0.5e0*h
    nint *= 2
    jmax = min(i,MAXJ)
    fourj = 1.0e0
    for j=1 in range(jmax):     # Use Richardson extrapolation.
      fourj = 4.0e0*fourj
      g1 = g0+(g0-g[j])/(fourj-1.0e0)
      g[j] = g0
      g0 = g1
    if (abs(g0) > tol):
      error = 1.0e0-gmax/g0
    else:
      error = gmax
    gmax = g0
    g[jmax+1] = g0
  else:
    rombint=g0
  if (i > MAXITER and abs(error) > tol):
    print 'Rombint failed to converge; integral, error = ',rombint,' , ',error
  return

#########################################################################################################
#
#     Fifth order Runge-Kutta Method with Adaptive Stepsize.
#     Integrate 'func' with parameters array fp(np) which contains any extra parameters other than the
#     integration variable from a to b, with initial step size dxinit and fractional accuracy eps.
#
#     In other words,
#          _b
#         /
#        |
#        |  FUNC(x,fp)dx
#        |
#        /
#       _ a
#
#     fp of length np, (i.e. real*8 fp(np)) contains all variables other
#     than the integration variable, say, x.
#
#########################################################################################################

def INTEGRATE(FUNC,fp,np,a,b,dxinit,eps):
  fp = np.empty([np])
  maxsteps =1.e8
  Nstep = 0
  x  = a
  dx = dxinit
  y  = 0.e0
  while (x-b)*(b-a) < 0.e0 and Nstep < maxsteps:
    Nstep = Nstep + 1
    dydx = FUNC(x,fp,np)
    yscale = max(abs(y) + abs(dx*dydx), 1.e-12)
    if ((x+dx-b)*(x+dx-a) > 0.e0):  # If stepsize overshoots, decrease it.
      dx = b - x
    RUNGE5VAR(y,dydx,x,dx,eps,yscale,dxnext,FUNC,fp,np)
    dx = dxnext
  if (Nstep >= maxsteps):
    print 'WARNING: failed to converge in INTEGRATE.'
  INTEGRATE = y
  return
  
###################################################################################################################
#
#   Fifth-order Runge-Kutta step with monitoring of local truncation error to ensure accuracy and adjust stepsize.
#   Input are the dependentvariable y and its derivative dydx at the starting value of the independent variable x.
#   Also input are the stepsize to be attempted htry, the required accuracy eps, and the value yscale, against 
#   which the error is scaled.  On output, y and x are replaced by their new values. hdid is the stepsize that
#   was actually accomplished, and hnext is the estimated next stepsize. DERIVS is the user-supplied routine that
#   computes right-hand-side derivatives.  The argument fparm is for an optional second argument to DERIVS 
#   (NOT integrated over).
#
###################################################################################################################

 def RUNGE5VAR(y,dydx,x,htry,eps,yscale,hnext,DERIVS,fp,np):
  fp = np.empty([np])
  safety  =  0.9e0
  pgrow   = -0.2e0
  pshrink = -0.25e0
  errcon  =  1.89e-4
  ytemp = 0.
  yerr  = 0.
  h = htry                                      # Set stepsize to initial accuracy.
  errmax = 10.e0
  while errmax > 1.e0 :
    RUNGE(y,dydx,x,h,ytemp,yerr,DERIVS,fp,np)
    errmax = abs(yerr/yscale)/eps               # Scale relative to required accuracy.
    if (errmax > 1.e0):                         # Truncation error too large; reduce h
      htemp = safety*h*(errmax**pshrink)
      hold = h
      h = sign(max(abs(htemp),0.1e0*abs(h)),h)  # No more than factor of 10
      xnew = x + h
      if (xnew == x):
        print 'WARNING: ','Stepsize underflow in RUNGE5VAR().'
        h = hold
        errmax = 0.e0

#     Step succeeded.  Compute estimated size of next step.
  if (errmax > errcon):
    hnext = safety*h*(errmax**pgrow)
  else:
    hnext = 5.e0 * h                            # No more than factor of 5 increase.
    
  x = x + h
  y = ytemp
  return y
 
###################################################################################################################
# 
#     Given values for a variable y and its derivative dydx known at x, use the fifth-order Cash-Karp Runge-Kutta 
#     method to advance the solution over an interval h and return the incremented variables as yout. Also
#     return an estimate of the local truncation error in yout using the embedded fourth order method.  The user 
#     supplies the routine DERIVS(x,y,dydx), which returns derivatives dydx at x.
#
###################################################################################################################

def RUNGE(y,dydx,x,h,yout,yerr,DERIVS,fp,np):
  fp  = np.empty([np])
  a2  =    0.2e0
  a3  =    0.3e0
  a4  =    0.6e0
  a5  =    1.e0
  a6  =    0.875e0
  c1  =   37.e0/378.e0
  c3  =  250.e0/621.e0
  c4  =  125.e0/594.e0
  c6  =  512.e0/1771.e0
  dc1 = c1 -  2825.e0/27648.e0
  dc3 = c3 - 18575.e0/48384.e0
  dc4 = c4 - 13525.e0/55296.e0
  dc5 = -277.e0/14336.e0
  dc6 = c6 -     0.25e0

  ak3 = DERIVS(x+a3*h,fp,np)
  ak4 = DERIVS(x+a4*h,fp,np)
  ak5 = DERIVS(x+a5*h,fp,np)
  ak6 = DERIVS(x+a6*h,fp,np)

# Estimate the fifth order value.
  yout = y + h*(c1*dydx + c3*ak3 + c4*ak4  + c6*ak6)

# Estimate error as difference between fourth and fifth order
  yerr = h*(dc1*dydx + dc3*ak3 + dc4*ak4 + dc5*ak5 + dc6*ak6)
  return yout #yerr       # CHECK RETURN VALUE

###################################################################################################################
#     Spline fit subroutines

def spline(x,y,n,yp1,ypn,y2):
  x  = np.empty([n])
  y  = np.empty([n])
  y2 = np.empty([n])
  NMAX=100010
  u = = np.empty([NMAX])
  if (yp1 > 0.99e30):
    y2[1]=0.e0
    u[1]=0.e0
  else:
    y2[1]=-0.5e0
    u[1]=(3.e0/(x[2]-x[1]))*((y[2]-y[1])/(x[2]-x[1])-yp1)
  for i=2 in range(n-1):
    sig=(x[i]-x[i-1])/(x[i+1]-x[i-1])
    p=sig*y2(i-1)+2.e0
    y2[i]=(sig-1.e0)/p
    u[i]=(6.e0*((y[i+1]-y[i])/(x[i+1]-x[i])-(y[i]-y[i-1])/(x[i]-x[i-1]))/(x[i+1]-x[i-1])-sig*u[i-1])/p
  if (ypn > .99e30):
    qn=0.e0
    un=0.e0
  else:
    qn=0.5e0
    un=(3.e0/(x[n]-x[n-1]))*(ypn-(y[n]-y[n-1])/(x[n]-x[n-1]))
  y2[n]=(un-qn*u[n-1])/(qn*y2[n-1]+1.e0)
  for k in range(n-1,1,-1):
    y2[k]=y2[k]*y2[k+1]+u[k]
  return y2       # CHECK RETURN VALUE

#---------------------------------------------------------------------------------

def splint(xa,ya,y2a,n,x,y):
  xa  = np.empty([n])
  y2a = np.empty([n])
  ya  = np.empty([n])
  while khi-klo < 1:
    k=(khi+klo)/2.
    if(xa(k) > x):
      khi=k
    else:
      klo=k
    
  h=xa[khi]-xa[klo]
  if(h == 0.): 
    print 'bad xa input in splint'
    break
  a=(xa[khi]-x)/h
  b=(x-xa[klo])/h
  y=a*ya[klo]+b*ya[khi]+((a**3-a)*y2a[klo]+(b**3-b)*y2a[khi])*(h**2)/6.
  return y      # CHECK RETURN VALUE

#---------------------------------------------------------------------------------

def ran2(idum):
  IM1=2147483563
  IM2=2147483399
  AM=1./IM1
  IMM1=IM1-1
  IA1=40014
  IA2=40692
  IQ1=53668
  IQ2=52774
  IR1=12211
  IR2=3791
  NTAB=32
  NDIV=1+IMM1/NTAB
  EPS=1.2e-7
  RNMX=1.-EPS
  idum2 = 123456789
  iv = np.empty([NTAB])
  iy = 0
  if (idum <= 0):
    idum=max(-idum,1)
    idum2=idum
    for j in range(NTAB+8,1,-1):
      k=idum/IQ1
      idum=IA1*(idum-k*IQ1)-k*IR1
      if (idum < 0): idum=idum+IM1
      if (j <= NTAB): iv[j]=idum
  iy=iv[1]
  endif
  k=idum/IQ1
  idum=IA1*(idum-k*IQ1)-k*IR1
  if (idum < 0): idum=idum+IM1
  k=idum2/IQ2
  idum2=IA2*(idum2-k*IQ2)-k*IR2
  if (idum2 < 0): idum2=idum2+IM2
  j=1+iy/NDIV
  iy=iv[j]-idum2
  iv[j]=idum
  if(iy < 1): iy=iy+IMM1
  ran2=min(AM*iy,RNMX)

  return

#---------------------------------------------------------------------------------

def gasdev(idum):
  iset = 0
  if (iset == 0):
    while (rsq >= 1. or rsq == 0.):
      v1=2.*ran1(idum)-1.
      v2=2.*ran1(idum)-1.
      rsq=v1**2+v2**2
    fac=sqrt(-2.*math.log[rsq]/rsq)
    gset=v1*fac
    gasdev=v2*fac
    iset=1
  else:
    gasdev=gset
    iset=0
  return

#---------------------------------------------------------------------------------

def ran1(idum):
  IA=16807
  IM=2147483647
  AM=1./IM
  IQ=127773
  IR=2836
  NTAB=32
  NDIV=1+(IM-1)/NTAB
  EPS=1.2e-7
  RNMX=1.-EPS
  iv = np.empty([NTAB])
  iy = 0
  if (idum <= 0 or iy == 0):
    idum=max(-idum,1)
    for j in range(NTAB+8,1,-1):
      k=idum/IQ
      idum=IA*(idum-k*IQ)-IR*k
      if (idum < 0): idum=idum+IM
      if (j <= NTAB): iv[j]=idum
    iy=iv[1]
  k=idum/IQ
  idum=IA*(idum-k*IQ)-IR*k
  if (idum < 0): idum=idum+IM
  j=1+iy/NDIV
  iy=iv[j]
  iv[j]=idum
  ran1=min(AM*iy,RNMX)
  return

#---------------------------------------------------------------------------------

def choldc(a,n,np,p):
  a = np.empty([np,np])
  p = np.empty([n])
  for i in range(1,n):
    for j in range(i,n):
      sum=a[i,j]
      for k in range(i-1,1,-1):
        sum=sum-a[i,k]*a[j,k]
      if(i == j):
        if(sum <= 0.):
          print 'choldc failed'
          break
        p[i]=sqrt(sum)
      else:
        a[j,i]=sum/p[i]
          endif
  return a #p       # CHECK RETURN VALUE

#---------------------------------------------------------------------------------

def jacobi(a,n,np,d,v,nrot):
  a = np.empty([np,np])
  v = np.empty([np,np])
  d = np.empty([np])
  NMAX=500
  b = np.empty([NMAX])
  z = np.empty([NMAX])
  for ip in range(1,n):
    for iq in range(1,n):
      v[ip,iq]=0.
    v[ip,ip]=1.
  for ip in range(1,n):
    b[ip]=a[ip,ip]
    d[ip]=b[ip]
    z[ip]=0.
  nrot=0
  for i in range(1,50):
    sm=0.
    for ip in range(1,n-1):
      for iq in range(ip+1,n):
        sm=sm+abs(a[ip,i])
  if(sm == 0.): return
  if(i < 4):
    tresh=0.2*sm/n**2
  else:
    tresh=0.
  for ip in range(1,n-1):
    for iq in range(ip+1,n):
      g=100.*abs(a[ip,iq])
      if((i > 4) and (abs(d[ip])+g == abs(d(ip))) and (abs(d[iq])+g == abs(d[iq]))):
        a[p,iq]=0.
      elif (abs(a[ip,iq]) > tresh):
        h=d[iq]-d[ip]
        if(abs[h]+g == abs[h]):
          t=a[ip,iq]/h
        else:
          theta=0.5*h/a[ip,iq]
          t=1./(abs(theta)+sqrt(1.+theta**2))
          if(theta <0.): t=-t
        c=1./sqrt(1+t**2)
        s=t*c
        tau=s/(1.+c)
        h=t*a[ip,iq]
        z[ip]=z[ip]-h
        z[iq]=z[iq]+h
        d[ip]=d[ip]-h
        d[iq]=d[iq]+h
        a[ip,iq]=0.
        for j in range(1,ip-1):
          g=a[j,ip]
          h=a[j,iq]
          a[j,ip]=g-s*(h+g*tau)
          a[j,iq]=h+s*(g-h*tau)
        for j in range(ip+1,iq-1):
          g=a[ip,j]
          h=a[j,iq]
          a[ip,j]=g-s*(h+g*tau)
          a[j,iq]=h+s*(g-h*tau)
        for j in range(iq+1,n):
          g=a[ip,j]
          h=a[iq,j]
          a[ip,j]=g-s*(h+g*tau)
          a[iq,j]=h+s*(g-h*tau)
        for j in range(1,n):
          g=v[j,ip]
          h=v[j,iq]
          v[j,ip]=g-s*(h+g*tau)
          v[j,iq]=h+s*(g-h*tau)
        nrot=nrot+1

    for ip in range(1,n):
      b[ip]=b[ip]+z[ip]
      d[ip]=b[ip]
      z[ip]=0.
    
  print 'too many iterations in jacobi'
  return       # CHECK RETURN VALUE

#---------------------------------------------------------------------------------

def moment(data1,n,ave,adev,sdev,var,skew,curt):
  data1 = np.empty([n])
  if(n <= 1):
    print 'n must be at least 2 in moment'
    break
  s=0.
  for j in range(1,n):
     s=s+data1[j]
  ave=s/n
  adev=0.
  var=0.
  skew=0.
  curt=0.
  ep=0.
  for j in range(1,n):
     s=data1[j]-ave
     ep=ep+s
     adev=adev+abs(s)
     p=s*s
     var=var+p
     p=p*s
     skew=skew+p
     p=p*s
     curt=curt+p
  adev=adev/n
  var=(var-ep**2/n)/(n-1)
  sdev=sqrt(var)
  if(var != 0.):
     skew=skew/(n*sdev**3)
     curt=curt/(n*var**2)-3.
  else:
     print 'no skew or kurtosis when zero variance in moment'
  return       # CHECK RETURN VALUE

#---------------------------------------------------------------------------------

def gammp(a,x):
  if(x < 0. or a <= 0.):
    print 'bad arguments in gammp'
    break
  if(x < a+1.):
    gammp=gser(gamser,a,x,gln)
  else:
    gammp=1.-call gcf(gammcf,a,x,gln)
  return

#---------------------------------------------------------------------------------

def gcf(gammcf,a,x,gln):
  ITMAX=100
  EPS=3.e-7
  FPMIN=1.e-30
  gln=gammln(a)
  b=x+1.-a
  c=1./FPMIN
  d=1./b
  h=d
  for i in range(1,ITMAX):
    an=-i*(i-a)
    b=b+2.
    d=an*d+b
    if(abs(d) < FPMIN): d=FPMIN
    c=b+an/c
    if(abs(c) < FPMIN): c=FPMIN
    d=1./d
    de=d*c
    h=h*de
    if(abs(de-1.) < EPS): break 
    print 'a too large, ITMAX too small in gcf'
  gammcf=exp(-x+a*math.log(x)-gln)*h
  return gammcf

#---------------------------------------------------------------------------------

def gser(gamser,a,x,gln):
  ITMAX=100
  EPS=3.e-7
  gln=gammln(a)
  if(x <= 0.):
    if(x < 0.): 
      print 'x < 0 in gser'
      break
    gamser=0.
    return
  ap=a
  sum=1./a
  de=sum
  for n in range(1,ITMAX):
    ap=ap+1.
    de=delx/ap
    sum=sum+de
    if(abs(de) < abs(sum)*EPS): break
  print 'a too large, ITMAX too small in gser'
  gamser=sum*exp(-x+a*math.log(x)-gln)
  return gamser

#---------------------------------------------------------------------------------      

def gammln(xx):
  cof = np.empty([6])
  stp= np.array([76.18009172947146e0,-86.50532032941677e0,24.01409824083091e0,\
    -1.231739572450155e0,.1208650973866179e-2,-.5395239384953d-5,2.5066282746310005e0])
  x=xx
  y=x
  tmp=x+5.5e0
  tmp=(x+0.5e0)*math.log(tmp)-tmp
  ser=1.000000000190015e0
  for j in range(1,6):
    y=y+1.e0
    ser=ser+cof[j]/y
  gammln=tmp+math.log(stp*ser/x)
  return 

#---------------------------------------------------------------------------------      

def rtbis(func,x1,x2,xacc):
  JMAX=500
  fmid=func(x2)
  f=func(x1)
  if(f*fmid >= 0.e0):
    print 'root must be bracketed in rtbis'
    break
  if(f < 0.e0):
    rtbis=x1
    dx=x2-x1
  else:
    rtbis=x2
    dx=x1-x2
  for j in range(1,JMAX):
    dx=dx*0.5e0
    xmid=rtbis+dx
    fmid=func(xmid)
    if(fmid <= 0.e0): rtbis=xmid
    if(dabs(dx) < xacc or fmid == 0.e0): return
  print 'too many bisections in rtbis'
  break

#---------------------------------------------------------------------------------      

def zbrac(func,x1,x2,succes):
  FACTOR=1.6e0
  NTRY=1000
  if(x1 == x2):
    print 'you have to guess an initial range in zbrac'
    break
  f1=func(x1)
  f2=func(x2)
  succes= True
  for j in range(1,NTRY):
    if(f1*f2 < 0.e0): return
    if(dabs(f1) < dabs(f2)):
      x1=x1+FACTOR*(x1-x2)
      f1=func(x1)
    else:
      x2=x2+FACTOR*(x2-x1)
      f2=func(x2)
  succes= False
  return       # CHECK RETURN VALUE

#---------------------------------------------------------------------------------      

def zbrak(fx,x1,x2,n,xb1,xb2,nb):
  xb1 = np.empty([nb])
  xb2 = np.empty([nb])
  nbb=0
  x=x1
  dx=(x2-x1)/n
  fp=fx(x)
  for i in range(1,n):
    x=x+dx
    fc=fx(x)
    if(fc*fp < 0.e0):
      nbb=nbb+1
      xb1[nbb]=x-dx
      xb2[nbb]=x
      if(nbb == nb):
        nb=nbb
        return
    fp=fc
  nb=nbb
  return       # CHECK RETURN VALUE

#---------------------------------------------------------------------------------      

def zbrent(func,x1,x2,tol):
  ITMAX=100
  EPS=3.e-8
  a=x1
  b=x2
  fa=func(a)
  fb=func(b)
  if((fa. >0. and fb > 0.) or (fa < 0. and fb < 0.)):
    print 'root must be bracketed for zbrent'
  c=b
  fc=fb
  for ite in range(1,ITMAX):
    if((fb > 0 and fc > 0.) or (fb < 0. and fc < 0.)):
      c=a
      fc=fa
      d=b-a
      e=d
    if(abs(fc) < abs(fb)):
      a=b
      b=c
      c=a
      fa=fb
      fb=fc
      fc=fa
    tol1=2.*EPS*abs(b)+0.5*tol
    xm=.5*(c-b)
    if(abs(xm) <= tol1  or fb == 0.):
      zbrent=b
      return
    if(abs(e) >= tol1  and abs(fa) > abs(fb)):
      s=fb/fa
      if(a == c):
        p=2.*xm*s
        q=1.-s
      else:
        q=fa/fc
        r=fb/fc
        p=s*(2.*xm*q*(q-r)-(b-a)*(r-1.))
        q=(q-1.)*(r-1.)*(s-1.)
      if(p > 0.): q=-q
      p=abs(p)
      if(2.*p < min(3.*xm*q-abs(tol1*q),abs(e*q))):
        e=d
        d=p/q
      else:
        d=xm
        e=d
    else:
      d=xm
      e=d
    a=b
    fa=fb
    if(abs(d) > tol1):
      b=b+d
    else:
      b=b+sign(tol1,xm)
    fb=func(b)
  print 'zbrent exceeding maximum iterations'
  break
  zbrent=b
  return
      
#---------------------------------------------------------------------------------      

