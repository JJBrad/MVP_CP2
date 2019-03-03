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
          "tMax" : 1000,
          "Measure" : False,
          "Animate" : True
          }

# Get input from command line
args = sys.argv[1:]
interact.readArgs(args, params)
np.random.seed(params["Seed"]) #None is default, changes each run.

lattice = lat.lattice(params["X Dimension"], 
                      params["Y Dimension"], 
                      initialState=params["Initial"],
                      measure=params["Measure"])

if not (params["Animate"] or params["Measure"]):
    print("Either animate or measure must be true.")
    exit()

if params["Animate"]:
    lattice.display(tMax=params["tMax"], interval=params["UpdateRate"])
elif params["Measure"]:
    lattice.run(tMax=params["tMax"])

if params["Measure"]:
    
    # Define function for fitting (linear in this case)
    def fitFunc(x, m, c):
        return(m*x + c)
    
    # Get the x and y c.o.m values as well as times
    comArr = np.array(lattice.COMList)
    xFull = comArr[:,0]
    yFull = comArr[:,1]
    tFull = lattice.tList
    # NaNs should occur in same place at x and y
    # Keep only up to first NaN, could update to keep over longest range
    if np.argwhere(np.isnan(xFull)).size > 0:
        maxInd = np.argwhere(np.isnan(xFull))[0,0]
        x = xFull[0:maxInd] - xFull[0]
        y = yFull[0:maxInd] - yFull[0]
        t = tFull[0:maxInd]
    else:
        x = xFull - xFull[0]
        y = yFull - yFull[0]
        t = tFull
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
    vFit = fitFunc(tFit, totVel, -off)
    
    pyplot.plot(tFull, np.sqrt(np.square(xFull - xFull[0]) + np.square(yFull - yFull[0])), "kx")
    pyplot.plot(tFit, vFit, "r-")
    pyplot.xlabel("Time")
    pyplot.ylabel("Distance from Starting Point")
    pyplot.show()
    if params["Animate"]:
        print("#"*40 + "\nNote: If animation was exited manually then an error sometimes appears above.\nDisregard this error.\n" + "#"*40)
