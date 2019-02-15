import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation
import os

#Declare global variables for J, k, and T parameters, and assign default value.
global J, k, T
J = 1.
k = 1.
T = 1.

def boltzmann(dE):
    """
    Calculates the probability of a switch from the Boltzmann probability and energy change dE.
    :param dE: Energy cost of switching.
    :return float p: Probability of switch.
    """
    return(np.exp(-dE/(k*T)))
    
def switch(dE):
    """
    Randomly determines whether a switch will occur based on Boltzmann probability
    :param dE: Energy cost of switching
    :return result: Boolean for whether a switch occurs.
    """
    if dE > 0:
        #If energy change is positive, use Boltzmann to find prob. of switch.
        p = boltzmann(dE)
        #Generate random number and compare to probability of switch.
        z = np.random.rand()
        if z > p: return(False)
    #If energy change is negative, or passed probabilty test, then switch.
    return(True)

class lattice(object):
    """
    Lattice object for the Ising model with built in dynamics and periodic boundary
    conditions
    """
    def __init__(self, xDim=50, yDim=0, dynamics="G", initialState="R", measure=True, tEquib=100, tCorr=10, label="Run", outDir="Data"):
        """
        Constructor for the lattice object. Defaults to square lattice.
        :param xDim: The x dimension of the lattice. Defaults to 50.
        :param yDim: The y dimension of the lattice (optional), defaults to square lattice.
        :param dynamics: The type of dynamics used to update the system. Glauber is default.
        :param initialState: The initial state of the lattice. "R"andom or "U"niform.
        :param measure: Whether to record measurements
        :param tEquib: The equilibrium time of the system (number of sweeps)
        :param tCorr: Autocorrelation time of the system (number of sweeps)
        """
        self.measure = measure
        self.outDir = outDir
        if self.measure and os.path.exists(self.outDir):
            print("Error. Output path {} already exists and measure is on. Exiting to avoid overwrite.".format(self.outDir))
            exit()
        elif self.measure:
            os.mkdir(self.outDir)
        self.label = label
        self.t = 0 # Number of sweeps performed.
        self.xDim = xDim
        if yDim > 0:
            self.yDim = yDim
        else:
            self.yDim = xDim
        self.dynamics = dynamics
        if type(initialState) is str:
            if initialState == "R":
                #Generate array of determined size with random entries +/-1
                self.lattice = np.sign(np.random.rand(self.xDim, self.yDim) - 0.5)
            elif initialState == "U":
                # Generate uniform lattice of +1
                self.lattice = np.ones(shape=(self.xDim, self.yDim))
            elif initialState == "S":
                self.lattice = np.ones(shape=(self.xDim, self.yDim))
                for i in range(self.xDim*self.yDim/2, self.xDim*self.yDim):
                    self.lattice.ravel()[i] = -self.lattice.ravel()[i]
            else:
                print("Initial lattice type {} not valid. Exiting...".format(initialState))
                exit()
        elif type(initialState) is np.ndarray:
            # Set lattice to specified state
            self.lattice = self.initialState
            # Redefine dimensions
            self.xDim, self.yDim = self.lattice.shape
        else:
            print("Initial lattice type {} not valid. Exiting...".format(initialState))
            exit()
        self.size = self.xDim*self.yDim
        self.energy = self.getEnergy()
        self.magnetisation = np.sum(self.lattice)#/float(self.size)
        self.tEquib = tEquib
        self.tCorr = tCorr
        self.tList = []
        self.EList = []
        self.MList = []
        print(self)
    
    def out(self):
        with open("{}/{}_Output.dat".format(self.outDir, self.label), "w") as outFile:
            outFile.write("Time     Energy        Magnetisation\n")
            for i in range(0, len(self.tList)):
                outFile.write("{}    {:.1f}       {:.1f}\n".format(str(self.tList[i]).ljust(5), self.EList[i], self.MList[i]))
    
    def clean(self):
        """
        Resets the parameters used for new measurement of same lattice.
        """
        self.t = 0
        self.tList = []
        self.EList = []
        self.MList = []
    
    def getEnergy(self):
        """
        Calculate the total energy of the current lattice.
        :return E: Total energy of lattice.
        """
        E = 0.
        # Go through each spin
        for i in range(0, self.xDim):
            for j in range(0, self.yDim):
                # Go through each nearest neighbour and sum spins.
                sumSpins = 0
                for tup in [((i+1)%self.xDim, j), ((i-1)%self.xDim, j), (i, (j+1)%self.yDim), (i, (j-1)%self.yDim)]: #The modulo gives periodic boundary conditions
                    sumSpins += self.lattice[tup[0], tup[1]]
                # Each of neighbor spins corresponds to a bond with energy -J*thisSpin*neighbourSpin. Each bond split between 2 sites. Sum for this site's energy.
                E += -self.lattice[i, j] *  sumSpins * J/2.
        return(E)
    
    def __str__(self):
        """
        Returns string for printing key details of object.
        """
        self.magnetisation = np.sum(self.lattice)#/float(self.size)
        return("Array has shape {}, contains {} +1 entries and {} -1 entries.\nEnergy: {} units.\nMagnetisation: {}".format(self.lattice.shape, np.count_nonzero(self.lattice == 1.), np.count_nonzero(self.lattice == -1.), self.energy, self.magnetisation))
    
    def next(self):
        """
        Perform one sweep with the specified algorithm.
        :param step: A string identifying which dynamics should be used for the system.
        """
        if self.dynamics in ["G", "g", "Glauber", "glauber", "1", 1]:
            for _ in range(self.size):
                self.glauberStep()
        elif self.dynamics in ["K", "k", "Kawasaki", "kawasaki", "2", 2]:
            for _ in range(self.size/2):  #Factor of two for Kawasaki since two spins flipped per step.
                self.kawasakiStep()
        else: 
            print("{} is not a recognised form of dynamics. Exiting...".format(self.dynamics))
        self.t += 1
        if self.measure and self.t > self.tEquib and self.t % self.tCorr == 0:
            self.magnetisation = np.sum(self.lattice)#/float(self.size)
            self.record()
            
    def record(self):
        self.EList.append(self.energy)
        self.MList.append(self.magnetisation)
        self.tList.append(self.t)
    
    
    """def next(self):  #Depreciated. Replaced by "next"
        #Perform one step in the algorithm which describes the dynamics of the system.
        #:param step: A string identifying which dynamics should be used for the system.
        if self.dynamics in ["G", "g", "Glauber", "glauber", "1", 1]: 
            self.glauberStep()
        elif self.dynamics in ["K", "k", "Kawasaki", "kawasaki", "2", 2]:
            self.kawasakiStep()
        else: 
            print("{} is not a recognised form of dynamics. Exiting...".format(self.dynamics))
    """  
    
    def singleSwitchEnergy(self, i, j):
        """
        Calculate the energy change of the lattice when a single spin is switched. 
        :param i: The first (x) index of the given spin in self.lattice.
        :param j: The second (y) index of the given spin in self.lattice.
        :return dE: The energy difference when the spin is flipped.
        """
        #Obtain list of spins of nearest neighbours. Positions are irrelevant.
        sumSpins = 0
        for tup in [((i+1)%self.xDim, j), ((i-1)%self.xDim, j), (i, (j+1)%self.yDim), (i, (j-1)%self.yDim)]: #The modulo gives periodic boundary conditions
            sumSpins += self.lattice[tup[0], tup[1]]
        #Energy change is 2J * current spin * sum NN
        return(2.*J*self.lattice[i, j]*sumSpins)

    def checkNN(self,i, j, iPrime, jPrime):
        """
        Check if two pairs of indices correspond to nearest neighbours. The modulo operator is used to provide periodic boundary conditions.
        :param i: first index of location one
        :param j: second index of location one
        :param iPrime: first index of location two
        :param jPrime: second index of location two.
        """
        return((i == iPrime and ((j + 1)%self.yDim == jPrime or (jPrime + 1)%self.yDim == j)) or (j == jPrime and ((i + 1)%self.xDim == iPrime or (iPrime + 1)%self.xDim == i)))
       
    def glauberStep(self):
        """
        Perform one step in the algorithm using Glauber dynamics. 
        """
        #Obtain random integers corresponding to one site on lattice.
        i = np.random.randint(0, self.xDim)
        j = np.random.randint(0, self.yDim)
        
        #Get energy change of switch and determine whether site should switch.
        dE = self.singleSwitchEnergy(i, j)
        if switch(dE):
            self.lattice[i, j] = -self.lattice[i, j]
            self.energy += dE
            self.magnetisation += 2.*self.lattice[i, j]
            
    def kawasakiStep(self):
        """
        Perform one step in the algorithm using Kawasaki dynamics.
        """
        #Obtain integers corresponding to sites on lattice. Should not be same site.
        i, j, iPrime, jPrime = (-1, -1, -1, -1)
        while i == iPrime and j == jPrime:
            i, iPrime = tuple(np.random.randint(0, self.xDim, size=2))
            j, jPrime = tuple(np.random.randint(0, self.yDim, size=2))

        #if spins are the same, switching is irrelevant. Could add this to while loop above depending on whether it counts as a step.
        if self.lattice[i, j] != self.lattice[iPrime, jPrime]:
            #Get energy changes for independent switches.
            dE = self.singleSwitchEnergy(i, j) + self.singleSwitchEnergy(iPrime, jPrime)
            
            #Check if sites are nearest neighbours
            if self.checkNN(i, j, iPrime, jPrime):
                #If they are nearest neighbours, then bond between them will have been treated as matching (switch 1 at a time) when it is actually still not. From -J to +J.
                dE += (4. * J)
            
            #Determine based on energy change whether site should switch.
            if switch(dE):
                self.lattice[i, j] = -1.*self.lattice[i, j]
                self.lattice[iPrime, jPrime] = -1.*self.lattice[iPrime, jPrime]
                self.energy += dE
              
    def animate(self, f, tMax):
        for _ in range(0, self.updateRate):
            if self.t <= tMax:
                self.next()
        im = pyplot.imshow(self.lattice, cmap="gray", interpolation="nearest") #"seismic"
        self.magnetisation = np.sum(self.lattice)#/float(self.size)
        #note.set_text("Time: {}, E = {}, m = {}".format(self.t, self.energy, self.magnetisation))
        #ax.set_title("Time: {}, E = {}, m = {}".format(self.t, self.energy, self.magnetisation))
        #axis.t.set_text("Time: {}, E = {}, m = {}".format(self.t, self.energy, self.magnetisation))
        #t = pyplot.figtext(0.5,0.9, "Time: {}, E = {}, m = {}".format(self.t, self.energy, self.magnetisation), ha="center")
        pyplot.clim(-1., 1.05)
        if f == (tMax/self.updateRate)-1:
            print("Animation finished. Please close the animation window.")
        return([im])
        
    def display(self, updateRate=None, tMax=1000):
        # TODO: Show current stats, maybe as title.
        if updateRate is None:
            self.updateRate = self.tCorr
        else:
            self.updateRate = updateRate  #How many steps between frames of animation.
        fig, axis = pyplot.subplots()
        for s in axis.spines: axis.spines[s].set_color("b")
        axis.spines['left'].set_position(('outward', 1))
        axis.spines['top'].set_position(('outward', 0.5))
        self.magnetisation = np.sum(self.lattice)#/float(self.size)
        #t = pyplot.figtext(0.5,0.9, "Time: {}, E = {}, m = {}".format(self.t, self.energy, self.magnetisation), ha="center")
        pyplot.imshow(self.lattice, cmap="gray", interpolation="nearest") #"bwr"
        #note = pyplot.figtext(0., 0., "Time: {}, E = {}, m = {}".format(self.t, self.energy, self.magnetisation))
        #ax.set_title()
        pyplot.clim(-1., 1.05)
        anim = FuncAnimation(fig, self.animate, tMax/self.updateRate, interval=0, blit=True, repeat=False, fargs=(tMax,))
        pyplot.show()
        if self.measure: self.out()
        
    def run(self, tMax=1000):
        if not self.measure:
            print("Lattice measurements turned off. Use '-M Y' flag. Exiting...")
            exit()
        for f in range(0, tMax):
            if self.t % int(float(tMax)/10.) == 0:
                print("Measurement {}: {}% complete.".format(self.label, 10*(self.t/int(float(tMax/10.)))))
            if self.t <= tMax:
                self.next()
        print("Measurement {}: {}% complete.".format(self.label, 10*(self.t/int(float(tMax/10.)))))
        self.out()
        
    def getSuscept(self, vals):
        """
        Get the susceptibility of the system from the list of magnetisations.
        """
        return((np.average(np.power(vals, 2.)) - np.average(vals)**2.)/(self.size*T*k))
        
    def getC(self, vals):
        """
        Get the heat capacity of the system from the list of energies.
        """
        return((np.average(np.power(vals, 2.)) - np.average(vals)**2.)/(self.size*T**2.*k))
    
    def bootstrapErr(self, vals, func, kSub=100):
        """
        Estimate error in a value by bootstrapping.
        :param vals: List of values used to calculate result.
        :param func: Function to calculate result from vals.
        :param nSub: Number of entries in each subset.
        :param kSub: Number of subsets used.
        :return Err: Estimate of error in value.
        """
        subVals = []
        for k in range(0, kSub):
            inds = np.random.randint(0, len(vals), size=len(vals))
            subset = [vals[ind] for ind in inds]
            subVals.append(func(subset))
        err = np.sqrt(np.average(np.power(subVals, 2.)) - np.average(subVals)**2.)
        return(err)
        
    def getOutput(self, kSub=100):
        E = np.average(self.EList)
        M = np.average(self.MList)
        # Standard error on mean for E and M.
        errE = np.std(self.EList)/np.sqrt(float(len(self.EList)))
        errM = np.std(self.MList)/np.sqrt(float(len(self.MList)))
        X = self.getSuscept(self.MList)
        C = self.getC(self.EList)
        errX = self.bootstrapErr(self.MList, self.getSuscept, kSub=kSub)
        errC = self.bootstrapErr(self.EList, self.getSuscept, kSub=kSub)
        return(E, M, C, X, errE, errM, errC, errX)
        
