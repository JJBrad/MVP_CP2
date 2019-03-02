###### MVP Checkpoint 2 Part 1 ######
Python Game of Life lattice simulation.
Defaults:
Lattice dimensions: 50 x 50
Initial state: Random
Number of Sweeps: 10000
Animation: On
Random seed: varies
Equilibration time: 150 sweeps
Autocorrelation time: 20 sweeps

Usage: python Ising.py <Tags>
Optional tags:
-x <value>        Lattice x dimension.
-y <value>        Lattice y dimension, defaults to match x.
-p <[p1,p2,p3]>   Values of probabilities for updates.
-i <[S,I,R,Im]>   Initial proportion of each type of cell.
-rs <value>       Set random seed.
-N <values>       Number of sweeps to perform.
-A <Y/N>          Turn animation on (Y) or off (N)
-M <Y/N>          Turn measurements on or off
-C <value>        Autocorrelation time (in sweeps) of the system (rate of updates)
-E <value>        Equilibration time (in sweeps) of the system (before 1st measurement)
-r <name>         Run name
-o <dir>          Output directory name
-H                Print this dialogue and exit.

Example with 40 x 25 lattice with 1000 sweeps, and p1=p2=p3=0.5:
python Main.py -x 40 -y 25 -N 1000 -p [0.5,0.5,0.5]
