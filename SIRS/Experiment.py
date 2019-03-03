import numpy as np
import Lattice as lat
import interactive as interact
import matplotlib.pyplot as pyplot
import matplotlib.pylab as pl
import sys
import os
import time

# Default values:
params = {"X Dimension":50,
          "Y Dimension":-1,
          "Seed" : None,
          "tMax" : 10000,
          "Measure" : True,
          "tCorr" : 20,
          "tEquib" : 150,
          "Animate" : False,
          "Measure" : True,
          "outDir" : "Experiment"
          }
"""
Default correlation and equilibration times are based on "psiVsTime.png",
which is the value of psi as a function of t output every sweep with initial
proportions [0.5, 0.4, 0., 0.1] and probabilities (0.2, 1/3, 1/3) as an example.
The system equilibrates (roughly) in 150 sweeps, and local fluctuations are on a
scale of around 10-15 sweeps. 
"""

# Get input from command line
args = sys.argv[1:]
interact.readArgs(args, params)
np.random.seed(params["Seed"]) #None is default, changes each run.

if (not params["Measure"]) or params["Animate"]:
    print("Warning. Measurements set to false or animation set to true")
    print("This will be ignored in the experiment.")

outDir = params["outDir"]
if os.path.exists(outDir):
    print("Error. Output directory exists. Will not overwrite. Exitting...")
    exit()
else:
    os.mkdir(outDir)
with open("{}/Results.csv".format(outDir), "w") as outFile:
    outFile.write("Run:,p1:,p2:,p3:,<I>:,<Psi>:,Var_I:,Var_Psi,N,n:\n")


# Phase diagram:
p2 = 0.5
p1Vals = [float(i)/1000. for i in range(0, 1001, 25)]
p3Vals = [float(i)/1000. for i in range(0, 1001, 25)]
runNum = 1

p1Res = []
p3Res = []
psi = []
varIList = []
varPsiList = []
NList = []
nList = []
maxSweeps = 1000

def runLat(p1, p2, p3, maxSweeps, initParams=[0.5, 0.5, 0., 0.]):
    global params, runNum, p1Res, p3Res, psi, varIList, NList, nList, varPsiList
    # Set p Values
    pVals = [p1, p2, p3]
    # Output progress:
    timeStr = time.gmtime(time.time())
    timeStr = "{:02d}:{:02d}".format(timeStr.tm_hour, timeStr.tm_min)
    print("Starting run {} at {}".format(runNum, timeStr))
    # Define lattice
    lattice = lat.lattice(params["X Dimension"], 
                          params["Y Dimension"], 
                          initProportions=initParams, 
                          probs=pVals,
                          tCorr=params["tCorr"],
                          tEquib=params["tEquib"],
                          measure=True,
                          label="Run{}".format(runNum),
                          outDir=params["outDir"],
                          status=False)
    # Run lattice
    lattice.run(tMax=maxSweeps)
    # Analyse
    avPsi, varPsi, avI, varI, N, n = lattice.analyse(showPlot=False)
    with open("{}/Results.csv".format(outDir), "a") as outFile:
        outFile.write("{},{},{},{},{},{},{},{},{},{}\n".format(runNum, p1, p2, p3, avI, avPsi, varI, varPsi, N, n))
    p1Res.append(p1)
    p3Res.append(p3)
    psi.append(avPsi)
    varIList.append(varI)
    varPsiList.append(varPsi)
    NList.append(N)
    nList.append(n)

print("Beginning Phase diagram")
for p1 in p1Vals:
    for p3 in p3Vals:
        runLat(p1, p2, p3, maxSweeps)
        runNum += 1

p1Bins = [min(p1Vals)-0.005] + [float(p1Vals[i] + p1Vals[i-1])/2. - 0.005 for i in range(1, len(p1Vals))] + [max(p1Vals) + 0.005]
p3Bins = [min(p3Vals)-0.005] + [float(p3Vals[i] + p3Vals[i-1])/2. - 0.005 for i in range(1, len(p3Vals))] + [max(p3Vals) + 0.005]
pl.hist2d(p1Res, p3Res, weights=psi, bins=[p1Bins, p3Bins])
pyplot.xlim(0, 1)
pyplot.ylim(0, 1)
pyplot.xlabel("$P_{1}$")
pyplot.ylabel("$P_{3}$")
pyplot.colorbar()
pyplot.title(r"$\left<\psi\right> = \frac{\left<I\right>}{N}$")
pyplot.savefig("{}/Phase_Diagram.png".format(outDir))
pyplot.clf()
weight = np.array(varIList)/np.array(NList)
pl.hist2d(p1Res, p3Res, weights=weight, bins=[p1Bins, p3Bins])
pyplot.xlim(0, 1)
pyplot.ylim(0, 1)
pyplot.xlabel("$P_{1}$")
pyplot.ylabel("$P_{3}$")
pyplot.colorbar()
pyplot.title(r"$\frac{\sigma_{I}^{2}}{N}$")
pyplot.savefig("{}/Variance.png".format(outDir))
pyplot.clf()

print("Phase diagram completed. Beginning cut.")
# Cut in phase diagram
p2 = 0.5
p3 = 0.5
p1Vals = [float(i)/100. for i in range(20, 51, 1)]
p1Res = []
p3Res = []
psi = []
varIList = []
varPsiList = []
NList = []
nList = []
maxSweeps = 10000

for p1 in p1Vals:
    runLat(p1, p2, p3, maxSweeps)
    runNum += 1

weight = np.array(varIList)/np.array(NList)
pyplot.plot(p1Res, weight, "k-")
pyplot.xlabel("$P_{1}$")
pyplot.ylabel(r"$\frac{\sigma_{I}^{2}}{N}$")
pyplot.savefig("{}/VarCut.png".format(outDir))
pyplot.clf()

print("Cut completed. Beginning immunity.")
# Effect of immunity
p1 = 0.5
p2 = 0.5
p3 = 0.5
psi = []
varIList = []
varPsiList = []
NList = []
nList = []
fracIm = [float(i)/100. for i in range(0, 101, 1)]
maxSweeps = 10000

for fIm in fracIm:
    initParams=[(0.5-fIm/2.), (0.5-fIm/2.), 0., fIm]
    runLat(p1, p2, p3, maxSweeps, initParams=initParams)
    runNum += 1

# Error is standard error on mean
err = np.sqrt(varPsiList)/np.sqrt(nList)
pyplot.errorbar(fracIm, psi, yerr = err, color = "k", ecolor = "k", linestyle = "--", marker = "s", capsize=2)
pyplot.xlabel("$f_{im}$")
pyplot.ylabel(r"$\left<psi\right>$")
pyplot.savefig("{}/ImmuneFraction.png".format(outDir))
pyplot.clf()

pyplot.errorbar(fracIm, psi, yerr = np.sqrt(varPsiList), color = "k", ecolor = "k", linestyle = "--", marker = "s", capsize=2)
pyplot.xlabel("$f_{im}$")
pyplot.ylabel(r"$\left<psi\right>$")
pyplot.savefig("{}/ImmuneFraction_stDevErrBar.png".format(outDir))
pyplot.clf()

