import yaml
from scipy import special
import numpy as np
from os import mkdir
from AT import get_data
from sys import argv
from matplotlib import pylab as plt
from scipy.integrate import quad,quadrature,nquad
from math import sqrt,cos, log, pi
from scipy import optimize as sciopt
from scipy.interpolate import UnivariateSpline as spline

names = {'booI':"Bootes I",'booII':"Bootes II",'car':"Carina",'com':"Coma Berenices",
'cvnI':"Canes Venatici I",'cvnII':"Canes Venatici II",'dra':"Draco",'for':"Fornax",
'her':"Hercules",'leoI':"Leo I",'leoIV':"Leo IV",'leoT':"Leo T",'scl':"Sculptor",
'seg1':"Segue 1",'sex':"Sextans",'sgr':"Sagittarius",'umaI':"Ursa Major I",
'umaII':"Ursa Major II",'umi':"Ursa Minor",'wil1':"Willman 1",}

###################################################################################################
#					FUNCTIONS DEFINITIONS
###################################################################################################
# stellar density profile
def nu(r,rh):
    return (1 + (r/rh)**2)**(-5./2.)

# dwarf surface brightness profile
def I(R,rh):
    return 4./3. * rh/(1+(R/rh)**2)**2

##########################################################################
# Mass of NFW DMH
def get_M_NFW(x):
    #this is the analytic formula
    #the constant is 4pi*rho0*rs^3
    return np.log(1.+x)-x/(1.+x)

##########################################################################
# numerical integrals in sigma_los

def integrand1(y,alpha,beta):
    result = nu(y,1)*get_M_NFW(y*alpha)/y**(2.-2.*beta)
    return result

def integral1(ymin,alpha,beta):
    res,err = quad(integrand1,ymin,+np.inf,args=(alpha,beta),epsabs=1.e-10,epsrel=1.e-10,limit=1000)
    return res

def integrand2(z,alpha,beta,gamma):
    result = (1.-beta/z**2) * z**(1.-2.*beta)/np.sqrt(z*z-1.)
    res = integral1(gamma*z,alpha,beta)
    return result * res

def integral2(alpha,beta,gamma):
    res,err = quad(integrand2,1.,+np.inf,args=(alpha,beta,gamma),epsabs=1.e-10,epsrel=1.e-10,limit=1000)
    return res

##########################################################################
# jfactor evaluation functions

def func(u,y, D, rt, ymin):
    return (1.+u)**(-4)/u/sqrt(u*u-D**2*(1-y*y))

def lim_u(y, D, rt, ymin):
    return [D*sqrt(1-y*y), rt]

def lim_y(D, rt, ymin):
    return [ymin,1]

def Jfactor(D,rt,r0,rho0,tmax):
    """
    returns the Jfactor computed in the solid angle of
    semi apex angle tmax, in degree, for a NFW halo profile of 
    shape parameters (r0,rho0) at distance D. 
    rt is the maximal radius of integration 
    D, r0 and rt are in kpc, and rho0 is in Msun.kpc^-3
    """
    ymin=cos(np.radians(tmax))
    Dprime=D/r0
    rtprime=rt/r0
    Msun2kpc5_GeVcm5 = 4463954.894661358
    cst = 4*pi*rho0**2*r0*Msun2kpc5_GeVcm5
    res = nquad(func, ranges=[lim_u, lim_y], args=(Dprime,rtprime,ymin),
    	opts=[{'epsabs':1.e-10,'epsrel':1.e-10,'limit':1000},
    	{'epsabs':1.e-10,'epsrel':1.e-10,'limit':1000}])
    return cst*res[0]

###################################################################################################
#					BODY OF THE CODE
###################################################################################################

# extract the dwarf parameter from file
dwarf = argv[1]
#mkdir('/home/andrea/Desktop/work/DWARF/Jvalue/output/new/%s'%dwarf) 	# uncomment if directory not present
R,v,dv,rh,rt,nstars,D = get_data(dwarf)
u=v.mean()

beta=-0.005		# beta fixed to this small value (i.e. near isotropy) 

gamma_array = R/rh
A_array = gamma_array**(1.-2.*beta)/I(R,rh)
r0_array = np.logspace(-1.,np.log10(5.),100)
alpha_array = rh/r0_array
I_array=np.zeros(shape=(len(A_array),len(r0_array)))

for i,gamma in enumerate(gamma_array):
    for j,alpha in enumerate(alpha_array):
        res = integral2(alpha,beta,gamma)
        I_array[i,j] = res *A_array[i]

cst = 8.*np.pi*4.3e-6
# Likelihood definition (only for fixed beta!)
def logLike(M0,j):
	I = cst*M0*I_array[:,j]
	S = dv**2.+I
	res = (np.log(S) + (v-u)**2./S).sum()
	return res/2.

###################################################################################################
#					MAXIMUM LIKELIHOOOD SCHEME
###################################################################################################

log10Jrho1 = np.log10([Jfactor(D,np.inf,r0,1.,0.5) for r0 in r0_array])
def deltaJ(log10rho0,J,j):
    return abs(J-log10Jrho1[j]-2.*log10rho0)

J_array = np.linspace(15.,21.,100)
LikeJ 	= np.zeros_like(r0_array)
J_new 	= np.empty([])
min_LikeJ = np.empty([])
for j,J in enumerate(J_array):
    for j,r0 in enumerate(r0_array):
        log10rho0 = sciopt.minimize_scalar(deltaJ,args=(J,j),tol=1.e-10).x
        LikeJ[j] = logLike(10.**log10rho0*r0**3.,j)
    spline_LikeJ = spline(r0_array,LikeJ,s=0)
    min_r0 = sciopt.minimize_scalar(spline_LikeJ,bracket=(0.1,2.),tol=1.e-10).x
    neg_spline = lambda J : -spline_LikeJ(J)
    if r0_array[0]<min_r0<r0_array[-1]:
    	J_new = np.append(J_new,J)
    	min_LikeJ = np.append(min_LikeJ,spline_LikeJ(min_r0))
    else:
    	max_r0 = sciopt.minimize_scalar(neg_spline,bracket=(0.1,2.),tol=1e-10).x
    	if r0_array[0]<max_r0<r0_array[-1]:
    		J_new = np.append(J_new,J)
    		min_LikeJ = np.append(min_LikeJ,spline_LikeJ(max_r0))

spline_Like = spline(J_new,min_LikeJ)
min_J = sciopt.minimize_scalar(spline_Like,method='Bounded',bounds=(J_array[0],J_array[-1]),tol=1.e-10).x

def one_sigmaJ(J):
    return np.abs(spline_Like(J)-spline_Like(min_J)-0.5)

err_l = sciopt.minimize_scalar(one_sigmaJ,method='Bounded',bounds=(J_array[0],min_J),tol=1.e-10).x-min_J
err_r = sciopt.minimize_scalar(one_sigmaJ,method='Bounded',bounds=(min_J,J_array[-1]),tol=1.e-10).x-min_J

J_plt = np.linspace(min_J-1,min_J+1,100)
plt.plot(J_plt,spline_Like(J_plt)-spline_Like(min_J))
plt.plot(min_J,0.,'^',label='J = %.2f %+.2f %.2f'%(min_J,err_r,err_l))
plt.hlines(0.,min(J_plt),max(J_plt),linestyles='dashed')
plt.hlines(.5,min(J_plt),max(J_plt),colors=('r'),linestyles='dashed',
	label=r'$1-\sigma$'+'\t'+r'$N_{stars}$ = %i'%nstars)
plt.legend(numpoints=1,loc='upper center',fontsize=12)
plt.ylabel(r'$-\Delta$$log$Like(J)',fontsize=14)
plt.xlabel(r'$log_{10}$  J [GeV$^2$ cm$^{-5}$]',fontsize=14)
plt.ylim(-1,10)
plt.xlim(min_J-1,min_J+1)
plt.suptitle('%s'%names[dwarf],fontsize=16)
plt.savefig('output/bfix/%s/LikeJ_%s.png'%(dwarf,dwarf),dpi=300,format='png')
plt.show()
