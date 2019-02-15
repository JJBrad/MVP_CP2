import numpy as np
import Lattice as lat
import interactive as interact
import matplotlib.pyplot as pyplot
import sys

# Default values:
params = {"X Dimension":50,
          "Y Dimension":-1,
          "Initial":None,
          "Seed": None,
          "tMax" : 10000,
          }

# Get input from command line
args = sys.argv[1:]
interact.readArgs(args, params)
np.random.seed(params["Seed"]) #None is default, changes each run.

lattice = lat.lattice(params["X Dimension"], 
                      params["Y Dimension"], 
                      initialState=params["Initial"])

lattice.display(tMax=params["tMax"])
