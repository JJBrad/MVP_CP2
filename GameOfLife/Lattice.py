import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation
import os
from PIL import Image

class lattice(object):
    """
    Lattice object for the Ising model with built in dynamics and periodic boundary
    conditions
    """
    def __init__(self, xDim=50, yDim=0, initialState=None, measure=False):
        """
        Constructor for the lattice object. Defaults to square lattice.
        :param xDim: The x dimension of the lattice. Defaults to 50.
        :param yDim: The y dimension of the lattice (optional), defaults to square lattice.
        :param initialState: Path to file determining initial state of lattice. If none is provided, random.
        """
        self.t = 0 # Number of sweeps performed.
        self.xDim = xDim
        if yDim > 0:
            self.yDim = yDim
        else:
            self.yDim = xDim
        if initialState is None:
            #Generate array of determined size with random entries 0, 1 with 25% alive.
            self.lattice = np.random.choice([0, 1], size=(self.xDim, self.yDim), p=[0.75, 0.25])
        elif type(initialState) is str:
            if initialState[-4:] == ".txt":
                self.latFromTXT(initialState)
            elif initialState[-4:] == ".png":
                self.latFromIMG(initialState)
            else:
                print("Error. Input file {} not valid. Require txt or png file.".initialState)
                exit()
        else:
            print("Error. Input file {} not valid. Require txt or png file.".initialState)
            exit()
        self.size = self.xDim*self.yDim
        self.measure=measure
        if self.measure:
            self.COMList = []
            self.tList = []
        print(self)
    
    def latFromTXT(self, path):
        with open(path, "r") as inFile:                                    # Open file        
            lines = inFile.readlines()                                     # Read file        
            self.xDim = len(lines)                                         # Height is number of lines
            self.yDim = max([len(line.strip("\n")) for line in lines])     # Width is (maximum) line length
            lat = np.zeros(shape=(self.xDim, self.yDim))                   # Lattice of zeros is starting point
            for x in range(0, len(lines)):                                 # Go through each line
                line = lines[x].strip("\n")                                #
                for y in range(0, len(line)):                              # Go through each character
                    if line[y] in ["0", "1"]: lat[x, y] = float(line[y])   # Update lattice
        self.lattice = lat                                                 # Set
        
    def latFromIMG(self, path):
        img = Image.open(path).convert('L')                                     # Open image (greyscale).
        data = np.asarray(img.getdata()).reshape((img.size[1], img.size[0]))    # Convert to array, no idea why image size is loading rotated but it is.
        self.xDim, self.yDim = data.shape
        for i in range(0, self.xDim):
            for j in range(0, self.yDim):
                if data[i, j] > 255./2.: data[i, j] = 0
                else: data[i, j] = 1
        self.lattice = data
        
    def __str__(self):
        """
        Returns string for printing key details of object.
        """
        return("Array has shape {}, contains {} live cells and {} dead entries.".format(self.lattice.shape, np.count_nonzero(self.lattice == 1), np.count_nonzero(self.lattice == 0)))
    
    def next(self):
        """
        Perform one sweep.
        """
        newLat = np.empty(shape=self.lattice.shape)                                 # Updated lattice, only updated when required, otherwise kept.
        for i in range(0, self.xDim):                                               # Loop through lattice.
            for j in range(0, self.yDim):                                           # 
                N = self.liveNeighbours(i, j)                                       # Get number of neighbours for site.
                if self.lattice[i, j] == 1 and (N < 2 or N > 3):                    # Check if cell is alive and num neighbours requires change.
                    newLat[i, j] = 0                                                # Kill live cell if required.
                elif self.lattice[i, j] == 0 and N == 3:                            # Check if cell is dead and num neighbours requires change.                
                    newLat[i, j] = 1                                                # Revive dead cell if required.
                else: newLat[i, j] = self.lattice[i, j]
        self.lattice = newLat                                                       # Update lattice.
        self.t += 1                                                                 # Increase time.    
        if self.measure:
            self.COMList.append(self.getCoM())
            self.tList.append(self.t)
                
    def liveNeighbours(self, i, j):
        """
        Get the number of live neighbours for a given site.
        :param i: The first (x) index of the given site in self.lattice.
        :param j: The second (y) index of the given site in self.lattice.
        :return N: Number of live neighbours.
        """
        Num = 0
        for x in range(i-1, i+2):       # Sum over 3 x 3 box.
            for y in range(j-1, j+2):
                Num += self.lattice[x%self.xDim, y%self.yDim]  # Modulo for periodic BC's
        # Don't count self
        Num -= self.lattice[i, j]
        return(Num)

    def getCoM(self):
        """
        Get the centre of mass of the system, i.e. the average x and y coordinate of live sites.
        :return x: The x coordinate of the c.o.m
        :return y: The y coordinate of the c.o.m
        """
        # Get all indices of nonzero sites, average each to get 2D position of C.o.M
        inds = np.argwhere(self.lattice > 0)
        # If both sides of either boundary are occupied then it is crossing, return NaNs
        if (0 in inds[:,0] and (self.xDim-1) in inds[:,0]) or (0 in inds[:,1] and (self.yDim-1) in inds[:,1]):
            com = np.array([np.nan, np.nan])
        else:
            com = inds.mean(axis=0)
        return(com)

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
        
