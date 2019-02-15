###### MVP Checkpoint 2 Part 1 ######
Python Game of Life lattice simulation.
Defaults:
Lattice dimensions: 50 x 50
Initial state: Random
Number of Sweeps: 10000
Animation: On
Random seed: varies

Usage: python Ising.py <Tags>
Optional tags:
-x <value>        Lattice x dimension
-y <value>        Lattice y dimension, defaults to match x.
-i <path>         Path to png or txt file with initial state of lattice. This overwrites x/y.
-rs <value>       Set random seed
-N <values>       Number of sweeps to perform
-H                Print this dialogue and exit.

Example with 40 x 25 lattice with 100 sweeps:
python Main.py -x 40 -y 25 -N 100
