import numpy as np
import Lattice as lat
import interactive as interact
import matplotlib.pyplot as pyplot
import sys
from scipy.optimize import curve_fit

# Default values:
params = {"X Dimension":50,
          "Y Dimension":-1,
          "Initial":None,
          "UpdateRate":300,
          "Seed": None,
          "tMax" : 10000,
          "Measure" : True
          }

# Get input from command line
args = sys.argv[1:]
interact.readArgs(args, params)
np.random.seed(params["Seed"]) #None is default, changes each run.

lattice = lat.lattice(params["X Dimension"], 
                      params["Y Dimension"], 
                      initProportions=[0.5, 0.2, 0.2, 0.1], 
                      probs=(1./3., 1./3., 1./3.))

lattice.display(tMax=params["tMax"], interval=params["UpdateRate"])

if params["Measure"]:
    
    # Define function for fitting (linear in this case)
    def fitFunc(x, m, c):
        return(m*x + c)
    
    # Get the x and y c.o.m values as well as times
    comArr = np.array(lattice.COMList)
    x = comArr[:,0]
    y = comArr[:,1]
    t = lattice.tList
    # NaNs should occur in same place at x and y
    # Keep only up to first NaN, could update to keep over longest range
    if np.argwhere(np.isnan(x)).size > 0:
        maxInd = np.argwhere(np.isnan(x))[0,0]
        x = x[0:maxInd]
        y = y[0:maxInd]
        t = t[0:maxInd]
    
    # Initial guess for fitting
    p0 = [0.3, 0.]
    
    # Perform fit for x and y
    xParams, xVar = curve_fit(fitFunc, t, x, p0=p0)
    yParams, yVar = curve_fit(fitFunc, t, y, p0=p0)
    xErr = np.sqrt(np.diag(xVar))
    yErr = np.sqrt(np.diag(yVar))
    
    # Combine for total values
    pos = np.sqrt(np.square(x) + np.square(y))
    totVel = np.sqrt(xParams[0]**2. + yParams[0]**2.)
    err = np.sqrt((1./totVel)*((xParams[0]*xErr[0])**2. + (yParams[0]*yErr[0])**2.))
    print("X component of velocity is {:.5f} +/- {:.5f}".format(xParams[0], xErr[0]))
    print("Y component of velocity is {:.5f} +/- {:.5f}".format(yParams[0], yErr[0]))
    print("Total velocity is {:.5f} +/- {:.5f}".format(totVel, err))
    
    # Plot fit
    off = np.sqrt(xParams[1]**2. + yParams[1]**2.)
    tFit = np.array([min(t)*0.97, max(t)*1.03]) # Since it's linear only need two points
    vFit = fitFunc(tFit, totVel, off)
    
    pyplot.plot(t, np.sqrt(np.square(x) + np.square(y)), "kx")
    pyplot.plot(tFit, vFit, "r-")
    
    pyplot.show()
