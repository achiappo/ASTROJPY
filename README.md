# FRESKA
Frequentist Stellar Kinematics Analyser

The Python package FRESKA allows to build the profile (-log) Likelihood for the astrophysical factor J of Dwarf Spheroidal 
Satellite Galaxies (dSPhs) of the Milky Way. It uses as input the kinematic data from the dSphs member stars. It also performs 
a basic statistical analysis, consisting in the determination of the Maximum Likelihood value of J and its Confidence Intervals. 
This README contains the instructions on how to use it correctly.

-------------------------------------------------------------------------------------------------------------------------------

### MODULES

##### cyfuncs.pyx   
This file contains the definitions of various functions used throughout. For a faster execution, these are written in a format 
compatible with Python Cythonize package. In order to use it, it must first be compiled with a C++ compiler. A Python script 
which performs this operation is also included, "setup.py", which should be executed with the following command

$ python setup.py build_ext --inplace

UTILS.PY  
This file contains useful functions to load the data and to evelope the result a MCMC scan.

PROFILES.PY  
This file contains the definitions of the classes to compute the properties of the two main components of dwarf satellite 
galaxies: stars and Dark Matter.

DISPERSION.PY  
This file contains the class to compute the stellar line-of-sight velocity dispersion, as given by Jeans equation.

LIKELIHOOD.PY  
This file contains the classes to compute the (negative) loglikelihood of the stellar kinematic data, given the model 
parameters entering the Jeans equation formalism.

-------------------------------------------------------------------------------------------------------------------------------

## SCRIPTS

PROFILE

-------------------------------------------------------------------------------------------------------------------------------

## DATA INPUT  

Data should be input into the code as a three-columns datafile consisting of

1) the distance of a star from the dSphs center projected onto the sky (in units of kpc)
2) measured line-of-sight velocity of each star (in units of km/s)
3) measurement error on the line-of-sight velocity in (in units of km/s)

Alternatvely, the user can customize the data input by modifying the function *load_data(gal)* contained in the *utils* module 

-------------------------------------------------------------------------------------------------------------------------------

## DATA OUTPUT  

The code produces two files:

a) "Like.npy" consists of the 2D, vertically stacked array of the profile likelihood components of the dSphs J factor. Its extension means that it is a python numpy-saved objected, thus loadable with the method *numpy.load* from within a python session or script. J is given in log10 basis and has units of Gev^2/cm^5. 

b) "results.yaml" contains a python dictionary with the results of the statistical analysis on the profile
  Likelihood curve. These consist of: its minimum (corresponfing to the Maximum Likelihood J value); the edges of the 1,2 and 3-sigma confidence intervals of the minimum; the velocity anisotropy parameter (r_a in the Osipkov-Merrit case, b in the constant-beta case) 
