import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation
import os
from PIL import Image

class lattice(object):
    """
    Lattice object for the SIRS model with built in dynamics and periodic boundary conditions. Each site has 
    one of 4 states; 0 is susceptible, 1 is infected, -1 is recovered, and 2 is immune.
    """
    def __init__(self, xDim=50, yDim=0, initProportions=[0.5, 0.5, 0., 0.], probs=(1./3., 1./3., 1./3.)):
        """
        Constructor for the lattice object. Defaults to square lattice.
        :param xDim: The x dimension of the lattice. Defaults to 50.
        :param yDim: The y dimension of the lattice (optional), defaults to square lattice.
        :param initProportions: Fraction of sites in each state as a tuple (S, I, R, Im).
        :param probs: Probabilities for rules, tuple (p1, p2, p3).
        """
        self.t = 0 # Number of sweeps performed.
        self.xDim = xDim
        if yDim > 0:
            self.yDim = yDim
        else:
            self.yDim = xDim
        self.size = self.xDim*self.yDim
        # Check proportions are physical:
        if sum(initProportions) > 1.0:
            print("Error. Proportions sum to more than 1. Exiting.")
            exit()
        if sum(initProportions) < 0.9999999:
            print("Warning. Proportions sum to less than 1. Extra will be made up of S sites.")
        # Number of sites with each state
        N = [int(round(self.size*initProportions[i])) for i in range(0, 4)]
        # Account for any rounding of these fractions by adding susceptible sites, only a small number.
        while sum(N) < self.size:
            N[0] += 1
        # Define lattice
        sites = np.array([0]*N[0] + [1]*N[1] + [-1]*N[2] + [2]*N[3])
        np.random.shuffle(sites)
        self.lattice = sites.reshape(self.xDim, self.yDim)
        # Store probabilities
        self.p1, self.p2, self.p3 = probs
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
        newLat = np.empty(shape=self.lattice.shape)                     # Empty lattice.
        for i in range(0, self.xDim):                                   # Loop through current lattice.
            for j in range(0, self.yDim):                               # 
                if self.lattice[i, j] == 0:                             # For susceptible sites        
                    NNs = [(i-1, j), (i+1, j), (i, j+1), (i, j-1)]      # List of indices of nearest neighbors
                    infected = False                                    # Originally uninfected
                    for n in range(0, 3):                               # Go through NNs
                        if self.lattice[NNs[n]] == 1:                   # If NN infected:
                            if np.random.rand() < p1:                   # Test for infection
                                infected = True                         #
                                break                                   # Only test for infection once
                    newLat[i, j] = int(infected)                        # Update lattice
                elif self.lattice[i, j] == 1:                           # For infected sites
                    if np.random.rand() < p2: newLat[i, j] = -1         # Test for recovery, recover if passes
                    else: newLat[i, j] = 1                              # Otherwise keep infected
                elif self.lattice[i, j] == -1:                          # For recovered sites
                    if np.random.rand() < p3: newLat[i, j] = 0          # Test for (and change to) susceptibility
                    else: newLat[i, j] = -1                             # Else keep the same
                else newLat[i, j] = self.lattice[i, j]                  # Immune are constant
        
        self.lattice = newLat                                           # Update lattice.
        self.t += 1                                                     # Increase time.    

    def animate(self, f, tMax):
        if self.t <= tMax:
            self.next()
        im = pyplot.imshow(self.lattice, cmap="gray", interpolation="nearest") #"seismic"
        pyplot.clim(0., 1.02)
        if f == (tMax)-1:
            print("Animation finished. Please close the animation window.")
        return([im])
        
    def display(self, tMax=1000, interval=300):
        fig, axis = pyplot.subplots()
        for s in axis.spines: axis.spines[s].set_color("r")
        axis.spines['left'].set_position(('outward', 1))
        axis.spines['top'].set_position(('outward', 0.5))
        pyplot.imshow(self.lattice, cmap="gray", interpolation="nearest") #"bwr"
        pyplot.clim(0., 1.02)
        pyplot.colorbar()
        anim = FuncAnimation(fig, self.animate, tMax, interval=interval, blit=True, repeat=False, fargs=(tMax,))
        pyplot.show()
        
    #def run(self, tMax=1000):
    # TODO: Function to run without animating
        
