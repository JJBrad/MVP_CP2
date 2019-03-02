import numpy as np
import Lattice as lat
import interactive as interact
import matplotlib.pyplot as pyplot
import sys
from scipy.optimize import curve_fit

# Default values:
params = {"X Dimension":50,
          "Y Dimension":-1,
          "pVals" : (1./3., 1./3., 1./3.),
          "Initial" : [0.5, 0.4, 0., 0.1],
          "Seed" : None,
          "tMax" : 10000,
          "Measure" : True,
          "tCorr" : 20,
          "tEquib" : 150,
          "Animate" : True,
          "Measure" : True,
          "RunLabel" : "Run",
          "outDir" : "Data"
          }
"""
Default correlation and equilibration times are based on "psiVsTime.png",
which is the value of psi as a function of t output every sweep with initial
proportions [0.5, 0.4, 0., 0.1] and probabilities (0.2, 1/3, 1/3) as an example.
The system equilibrates (roughly) in 150 sweeps, and local fluctuations are on a
scale of around 10-15 sweeps. 

Example pVals for different states:
Absorbing: [0.1, 1./3., 1./3.]
Dynamic:   [1./3., 1./3., 1./3.]
Waves:     [0.22, 1./3., 1./3.]
"""

# Get input from command line
args = sys.argv[1:]
interact.readArgs(args, params)
np.random.seed(params["Seed"]) #None is default, changes each run.

if not (params["Measure"] or params["Animate"]):
    print("Error, system is set to neither animate nor measure. Exiting...")
    exit()

lattice = lat.lattice(params["X Dimension"], 
                      params["Y Dimension"], 
                      initProportions=params["Initial"], 
                      probs=params["pVals"],
                      tCorr=params["tCorr"],
                      tEquib=params["tEquib"],
                      measure=params["Measure"],
                      label=params["RunLabel"],
                      outDir=params["outDir"])

if params["Animate"]:
    lattice.display(tMax=params["tMax"])
else:
    lattice.run(tMax=params["tMax"])

if params["Measure"]:
    avPsi, varPsi, avI, varI, N, n = lattice.analyse(showPlot=True)
    print("Average psi: {:.3f}\nVariance: {:.3f}".format(avPsi, varPsi))

print("#"*40 + "\nNote: If animation was exited manually then an error may appear above.\nDisregard this error.\n" + "#"*40)
