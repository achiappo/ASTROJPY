import numpy as np
from scipy.integrate import quad
from profiles import DMProfile, StellarProfile, AnisotropyKernel

class SphericalJeansDispersion(object):
    def __init__(self, dm, stellar, anisotropy, dwarf_props, **kwargs):
    	if isinstance(dm, DMProfile):
            self.dm = dm
        elif isinstance(dm, str):
            self.dm = build_profile(dm,**kwargs)
        if isinstance(stellar, StellarProfile):
            self.stellar = stellar
        elif isinstance(stellar, str):
            self.stellar = build_profile(stellar,**kwargs)
        if isinstance(anisotropy, AnisotropyKernel):
            self.kernel = anisotropy
        elif isinstance(anisotropy, str):
            self.kernel = build_kernel(anisotropy,**kwargs)
        G=4.3e-6
        self.dwarf_props = dwarf_props
        self.cst = 8.*np.pi*G
        self.params = {'J':18} #dummy value
        self.synch()
        
    def synch(self):
        for par in self.dm.params:
            self.params['dm_'+par] = self.dm.__dict__[par]
        for par in self.stellar.params:
            self.params['st_'+par] = self.stellar.__dict__[par]
        for par in self.kernel.params:
            self.params['ker_'+par] = self.kernel.__dict__[par]
    
    def setparams(self, name, value):
        if name.strip('dm_') in self.dm.__dict__:
            setattr(self.dm, name.strip('dm_'), value)
        if name.strip('st_') in self.stellar.__dict__:
            setattr(self.stellar, name.strip('st_'), value)
        if name.strip('ker_') in self.kernel.__dict__:
            setattr(self.kernel, name.strip('ker_'), value)
        if name == 'J':
        	setattr(self, name, value)
        	self.params[name] = value
        self.synch()
        
    def integrand(self, s, R, **kwargs):
        #not correct : R could be provided which is not in inital self.R
        #this is weak anyway, why are r0 and rh singled out parameters?
        r0 = kwargs['r0'] if 'r0' in kwargs else self.dm.r0
        rh = kwargs['rh'] if 'rh' in kwargs else self.stellar.rh
        val = self.stellar.density(s/rh) * self.dm.mass(s/r0) * self.kernel(s, R) / s
        return val

    def compute(self, R):
        #called by a LogLike object
        D = self.dwarf_props['D']
        theta = self.dwarf_props['theta']
        rt = self.dwarf_props['rt']
        errs = self.dwarf_props['errs']
        if np.isscalar(R):
            integral, error = sciint.quad(self.integrand, R, np.inf, args=(R,))
            sigma2 = integral / self.stellar.surface_brightness(R) / np.sqrt(self.dm.Jreduced(D, theta, rt, errs))
        else:
            sigma2 = np.zeros_like(R)
            for i,rr in enumerate(R):
                integral, error = quad(self.integrand, rr, np.inf, args=(rr,))
                I_of_R = self.stellar.surface_brightness(rr)
                sigma2[i] = integral / I_of_R / np.sqrt(self.dm.Jreduced(D, theta, rt, errs))
        return sigma2 * self.dm.r0**3 * self.cst * np.power(10,self.J/2.)
        

##############################################################################
class IsoSphSigmaLOS():
    def __init__(self,**kwargs):
        self.__dict__ = kwargs
        self.cst = 8.*np.pi*4.3e-6

    def Kernel(self, u):
        return np.sqrt(1. - 1./u**2)

    def setStellar(self, profile):
        self.star=profile
        self.star_keys = self.star.__dict__.keys()
    
    def setDM(self, profile):
        self.mass=profile
        self.mass_keys = self.mass.__dict__.keys()
    
    def __integrand_s(self, r, R):
        kern = self.kern(r/R)
        star = self.star.density(r)
        mass = self.mass.mass(r)
        return kern*star*mass/r

    def __integral_s(self, R):
        return quad(self.__integrand_s, R, +np.inf, args=(R,))[0]

    def __call__(self, R):
        return __integral_s(R)

    def synch_params(self, **kwargs):
        for k,v in kwargs.items():
            if k in self.mass_keys :
                self.mass.__setattr__(k, v)
            if k in self.star_keys :
                self.star.__setattr__(k, v)
                
    def evaluate(self, **kwargs):
        synch_params(kwargs)
        Int_S = self.__integral_s(kwargs['R'])
        return self.cst*Int_S


def SphericalSigmaLOS(anisotropy_type, **kwargs):
    if anisotropy_type.upper() == 'ISO' or anisotropy_type.upper() == 'IS':
        return IsoSphSigmaLOS(**kwargs)
