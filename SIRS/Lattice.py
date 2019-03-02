import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib import colors
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Patch
import os
from PIL import Image

# make a color map of fixed colors
cList = ["orange", "white", "red", "black"]
cmap = colors.ListedColormap(cList)
bounds=[-1.5, -0.5, 0.5, 1.5, 2.5]
norm = colors.BoundaryNorm(bounds, cmap.N)

class lattice(object):
    """
    Lattice object for the SIRS model with built in dynamics and periodic boundary conditions. Each site has 
    one of 4 states; 0 is susceptible, 1 is infected, -1 is recovered, and 2 is immune.
    """
    def __init__(self, xDim=50, yDim=0, initProportions=[0.5, 0.5, 0., 0.], probs=(1./3., 1./3., 1./3.), measure=True, tEquib=100, tCorr=10, outDir="Data", label="Run", status=True):
        """
        Constructor for the lattice object. Defaults to square lattice.
        :param xDim: The x dimension of the lattice. Defaults to 50.
        :param yDim: The y dimension of the lattice (optional), defaults to square lattice.
        :param initProportions: Fraction of sites in each state as a tuple (S, I, R, Im).
        :param probs: Probabilities for rules, tuple (p1, p2, p3).
        :param measure: Whether to record measurements
        :param animate: Whether to animate the system
        :param tEquib: The equilibrium time of the system (number of sweeps)
        :param tCorr: Autocorrelation time of the system (number of sweeps)
        :param outDir: 
        """
        self.outDir = outDir
        self.label = label
        self.path = self.outDir + "/" + self.label
        # Setup measurement 
        self.measure = measure
        self.tEquib = tEquib    # Equilibration time
        self.tCorr = tCorr      # Auto-correlation time
        self.stop = False       # Stop calculations (e.g. if no infected sites)
        if self.measure:
            self.IList = []
            self.tList = []        
            if os.path.exists(self.path):
                # Don't overwrite previous data
                print("Error. Output path {} already exists and measure is on. Exiting to avoid overwrite.".format(self.path))
                exit()
            elif os.path.exists(self.outDir): # Create run directory
                os.mkdir(self.path)
            else: # Create output and run directories
                os.mkdir(self.outDir)
                os.mkdir(self.path)
            
        # Initialise lattice
        self.t = 0 # Number of sweeps performed.
        self.xDim = xDim
        if yDim > 0:
            self.yDim = yDim
        else:
            self.yDim = xDim
        self.size = self.xDim*self.yDim
        # Check proportions are physical:
        if sum(initProportions) > 1.0000001:
            print("Error. Proportions sum to more than 1. Exiting.")
            exit()
        if sum(initProportions) < 0.9999999:
            print("Warning. Proportions sum to less than 1. Extra will be made up of S sites.")
        # Number of sites with each state
        N = [int(round(self.size*initProportions[i])) for i in range(0, 4)]
        # Account for any rounding of these fractions by adding susceptible sites, only a small number.
        while sum(N) < self.size:
            N[0] += 1
        while sum(N) > self.size:
            N[0] -= 1
        # Define lattice
        sites = np.array([0]*N[0] + [1]*N[1] + [-1]*N[2] + [2]*N[3])
        np.random.shuffle(sites)
        self.lattice = sites.reshape(self.xDim, self.yDim)
        
        # Store probabilities
        self.p1, self.p2, self.p3 = probs
        if status:
            # Print state
            print(self)
            
    def __str__(self):
        """
        Returns string for printing key details of object.
        """
        return("Array has shape {}, contains {} S cells, {} I, {} R, and {} Im entries.".format(self.lattice.shape, np.count_nonzero(self.lattice == 0), np.count_nonzero(self.lattice == 1), np.count_nonzero(self.lattice == -1), np.count_nonzero(self.lattice == 2)))
    
    def next(self):
        """
        Perform one sweep.
        """
        for s in range(0, self.size):                                     # Each step
            i = np.random.randint(0, self.xDim)                           # Pick random site
            j = np.random.randint(0, self.yDim)                           # 
            if self.lattice[i, j] == 0:                                   # For susceptible sites        
                NNs = [((i-1)%self.xDim, j), ((i+1)%self.xDim, j),\
                (i, (j+1)%self.yDim), (i, (j-1)%self.yDim)]               # List of indices of nearest neighbors 
                infected = False                                          # Originally uninfected
                for n in range(0, 4):                                     # Go through NNs
                    if self.lattice[NNs[n]] == 1:                         # If NN infected:
                        if np.random.rand() < self.p1:                    # Test for infection
                            infected = True                               #
                            break                                         # Only test for infection once
                self.lattice[i, j] = int(infected)                        # Update lattice
            elif self.lattice[i, j] == 1:                                 # For infected sites
                if np.random.rand() < self.p2: self.lattice[i, j] = -1    # Test for recovery, recover if passes
                else: self.lattice[i, j] = 1                              # Otherwise keep infected
            elif self.lattice[i, j] == -1:                                # For recovered sites
                if np.random.rand() < self.p3: self.lattice[i, j] = 0     # Test for (and change to) susceptibility
                else: self.lattice[i, j] = -1                             # Else keep the same
                                                                          # Immune cells not considered.
        self.t += 1                                                       # Increase time.
        if self.t > self.tEquib and self.t % self.tCorr == 0:             # If time is right
            self.tList.append(self.t)                                     # Update lists
            self.IList.append(self.getFrac())                             # 
        if self.getFrac() == 0:                                           # If no infected sites remain
            self.tList.append(self.t)                                     # Update lists
            self.IList.append(self.getFrac())                             # 
            self.stop = True                                              # End run

    def getFrac(self):
        """
        Get the number of infected sites on the lattice.
        """
        I = np.count_nonzero(self.lattice == 1)
        return(I)

    def animate(self, f, tMax):
        if not self.stop:
            if self.t <= tMax:
                self.next()
            im = pyplot.imshow(self.lattice, cmap=cmap, interpolation="nearest") #"seismic"
            pyplot.clim(-1.5, 2.5)
            return([im])
        else:
            return([])
        
    def display(self, tMax=1000):
        fig, axis = pyplot.subplots()
        for s in axis.spines: axis.spines[s].set_color("r")
        axis.spines['left'].set_position(('outward', 1))
        axis.spines['top'].set_position(('outward', 0.5))
        pyplot.imshow(self.lattice, cmap=cmap, interpolation="nearest") #"bwr"
        pyplot.clim(-1.5, 2.5)
        labels = ["Recovered", "Susceptible", "Infected", "Immune"]
        legendElements = []
        for e in [1, 2, 0, 3]:
            legendElements.append(Patch(facecolor=cList[e], edgecolor="k", label=labels[e]))
        fig.legend(handles=legendElements, loc="center right")
        axis.set_position([0.01, 0.08, 0.85, 0.85], which='both')
        anim = FuncAnimation(fig, self.animate, tMax, interval=0, blit=True, repeat=False, fargs=(tMax,))
        pyplot.show()
        print("Animation finished. Please close the animation window.")

    def run(self, tMax=1000):
        for i in range(0, tMax):
            if not self.stop:
                self.next()
            else: 
                break

    def analyse(self, showPlot=False):
        """
        Function to analyse the results of this run and plot, showing if requested.
        """
        psi = np.array(self.IList)/float(self.size)
        with open("{}/Result.csv".format(self.path), "w") as outFile:
            outFile.write("t,I\n")
            for i in range(0, len(self.tList)):
                outFile.write("{},{}\n".format(self.tList[i], self.IList[i]))
        if 0 in self.IList or len(self.IList) == 0:
            # If the system reaches an absorbing state, it would stay infinitely long,
            # therefore average psi and variance are said to be zero
            avPsi = 0.
            varPsi = 0.
            avI = 0.
            varI = 0.
        else:
            # Convert I to psi (normalised)
            # Get statistics
            avPsi = np.average(psi)
            varPsi = np.var(psi)
            avI = np.average(self.IList)
            varI = np.var(self.IList)
        N = self.size
        n = len(psi)
        pyplot.plot(self.tList, psi)
        pyplot.xlabel("Time (sweeps)")
        pyplot.ylabel("$\psi$")
        pyplot.savefig("{}/PsiVsTime.png".format(self.path))
        if showPlot:
            pyplot.show()
        else:
            pyplot.clf()
        return(avPsi, varPsi, avI, varI, N, n)
        
