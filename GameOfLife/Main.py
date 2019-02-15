import numpy as np
import Lattice as lat
import interactive as interact
import matplotlib.pyplot as pyplot
import sys

# Default values:
params = {"T":1.,
          "k":1.,
          "J":1.,
          "X Dimension":50,
          "Y Dimension":-1,
          "Animate":True,
          "Measure":True,
          "Output":"Run",
          "Dynamics":"G",
          "Initial":"R",
          "Seed": None,
          "Equilibration Time" : 100,
          "Autocorrelation" : 10,
          "tMax" : 10000,
          "outDir" : "Data"
          }

args = sys.argv[1:]
interact.readArgs(args, params)

#Try getting seed argument from command line
np.random.seed(params["Seed"]) #None is default, changes each run.

lat.T = params["T"]
lat.J = params["J"]
lat.k = params["k"]
lattice = lat.lattice(params["X Dimension"], 
                      params["Y Dimension"], 
                      dynamics=params["Dynamics"], 
                      initialState=params["Initial"], 
                      measure=params["Measure"], 
                      tEquib=params["Equilibration Time"], 
                      tCorr=params["Autocorrelation"],
                      label=params["Output"],
                      outDir=params["outDir"])

if params["Animate"]:
    lattice.display(updateRate=params["Autocorrelation"], tMax=params["tMax"])
elif params["Measure"]:
    lattice.run(tMax=params["tMax"])
    
if params["Measure"]:
    pyplot.plot(lattice.tList, lattice.EList, "r-")
    pyplot.xlabel("Time (sweeps)")
    pyplot.ylabel("Energy")
    pyplot.show()
    pyplot.plot(lattice.tList, lattice.MList, "r-")
    pyplot.xlabel("Time (sweeps)")
    pyplot.ylabel("Magnetisation")
    pyplot.show()

"""
10000 sweeps per T
Measure from sweep 100, every 10 sweeps.
1 <= T <= 3, step size 0.1
"""
